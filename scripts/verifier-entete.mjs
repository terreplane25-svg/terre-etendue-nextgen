/**
 * verifier-entete.mjs — L'en-tête ne doit se chevaucher à AUCUNE largeur.
 *
 * LE DÉFAUT QUE CE CONTRÔLE EXISTE POUR ATTRAPER
 * ──────────────────────────────────────────────
 * La barre de navigation portait `flex: 1` avec `minWidth: 0`, et ses liens
 * `whiteSpace: nowrap`. Quand la fenêtre devenait trop étroite, la boîte du
 * menu se comprimait sous la largeur de son contenu — mais les liens, eux, ne
 * se comprimaient pas : ils DÉBORDAIENT de la boîte, des deux côtés puisque le
 * menu est centré. À gauche ils passaient sous le logo, à droite sous la
 * recherche.
 *
 * Mesuré : la disposition de bureau a besoin de 1548 px et démarrait à
 * 1024 px. Le chevauchement était donc garanti sur toute la plage des écrans
 * d'ordinateur portable — c'est-à-dire chez la plupart des visiteurs, sur
 * TOUTES les pages du site.
 *
 * CE QU'IL VÉRIFIE
 * ────────────────
 * Que deux éléments cliquables de l'en-tête ne se recouvrent jamais, à un
 * balayage de largeurs allant du téléphone au grand écran. Un chevauchement de
 * quelques pixels sur une bordure n'est pas un défaut ; au-delà de la
 * tolérance, deux liens se disputent la même surface et l'un est inatteignable.
 *
 * Il vérifie aussi qu'aucun lien ne DÉBORDE de la fenêtre, l'autre issue du
 * même mécanisme : un menu qui ne rentre pas peut sortir du cadre au lieu de
 * recouvrir son voisin, ce qui rend le lien invisible plutôt que masqué.
 *
 *     node scripts/verifier-entete.mjs [port]
 */
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const PORT = process.argv[2] ?? '3250';
const RACINE = `http://localhost:${PORT}`;

/** Un chevauchement sous ce seuil est un artefact de bordure, pas un défaut. */
const TOLERANCE_PX = 2;

/**
 * La marge minimale exigée autour du menu, sur la barre de bureau.
 *
 * « Ne se chevauche pas » n'est pas « respire ». Une première version des
 * paliers basculait à 1120 px, où la barre tenait avec exactement 0 px entre le
 * logo et le premier lien : aucun chevauchement, et pourtant les mots se
 * touchaient. Le contrôle ne le voyait pas, et c'est en regardant la capture
 * que le défaut est apparu. Il l'attrape maintenant.
 */
const MARGE_MIN_PX = 14;

/**
 * Les largeurs balayées. Elles couvrent les tailles réelles, et surtout les
 * ABORDS des points de bascule : c'est là que les dispositions se cassent, et
 * un balayage grossier passerait juste à côté.
 */
const LARGEURS = [
  320, 360, 390, 414, 480, 600, 700, 768, 800, 900, 1000,
  1020, 1024, 1080, 1120, 1148, 1152, 1156, 1200, 1230, 1276, 1280, 1284,
  1330, 1366, 1400, 1436, 1440, 1444, 1500, 1536, 1548, 1576, 1580, 1584,
  1600, 1700, 1920, 2560,
];

const PAGES = ['/', '/lab', '/library'];

let echecs = 0;
let controles = 0;

const nav = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
try {
  for (const chemin of PAGES) {
    for (const largeur of LARGEURS) {
      const page = await nav.newPage({ viewport: { width: largeur, height: 800 } });
      try {
        await page.goto(RACINE + chemin, { waitUntil: 'domcontentloaded' });
        // Les polices changent les métriques : mesurer avant leur chargement
        // donnerait un verdict sur une mise en page qui n'existe pas.
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(120);

        const r = await page.evaluate(({ tol, margeMin }) => {
          const cibles = [...document.querySelectorAll('header a, header button')]
            .map((e) => ({
              t: (e.textContent || '').trim().slice(0, 20) || e.getAttribute('aria-label') || '?',
              r: e.getBoundingClientRect(),
            }))
            .filter((x) => x.r.width > 0 && x.r.height > 0
              && getComputedStyle(document.elementFromPoint(1, 1) ?? document.body).display !== 'none');
          const chevauchements = [];
          for (let i = 0; i < cibles.length; i += 1) {
            for (let j = i + 1; j < cibles.length; j += 1) {
              const [a, b] = [cibles[i].r, cibles[j].r];
              const h = Math.min(a.right, b.right) - Math.max(a.left, b.left);
              const v = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
              if (h > tol && v > tol) {
                chevauchements.push(`${cibles[i].t}⨯${cibles[j].t} (${Math.round(h)}×${Math.round(v)} px)`);
              }
            }
          }
          const debords = cibles
            .filter((x) => x.r.left < -tol || x.r.right > window.innerWidth + tol)
            .map((x) => `${x.t} (${Math.round(x.r.left)}→${Math.round(x.r.right)})`);

          // Les marges autour du menu, sur la barre de bureau seulement : la
          // barre compacte n'a pas de menu horizontal à border.
          const etroites = [];
          const bureau = [...document.querySelectorAll('header > div')]
            .find((d) => d.classList.contains('tei-entete-bureau')
              && getComputedStyle(d).display !== 'none');
          if (bureau) {
            const logo = bureau.querySelector('a');
            const liens = [...bureau.querySelectorAll('nav > div > a')]
              .filter((a) => a.offsetWidth > 0);
            const droite = bureau.lastElementChild;
            if (logo && liens.length > 0 && droite) {
              const g = Math.round(liens[0].getBoundingClientRect().left
                - logo.getBoundingClientRect().right);
              const d = Math.round(droite.getBoundingClientRect().left
                - liens.at(-1).getBoundingClientRect().right);
              if (g < margeMin) etroites.push(`logo→premier lien : ${g} px`);
              if (d < margeMin) etroites.push(`dernier lien→recherche : ${d} px`);
            }
          }
          return { chevauchements, debords, etroites, nb: cibles.length };
        }, { tol: TOLERANCE_PX, margeMin: MARGE_MIN_PX });

        controles += 1;
        if (r.nb === 0) {
          echecs += 1;
          console.error(`  ✗ ${chemin} @ ${largeur} px : aucun élément d'en-tête trouvé — le contrôle ne mesure rien`);
        } else if (r.chevauchements.length > 0 || r.debords.length > 0
                   || r.etroites.length > 0) {
          echecs += 1;
          console.error(`  ✗ ${chemin} @ ${largeur} px`);
          for (const c of r.chevauchements) console.error(`      chevauchement : ${c}`);
          for (const d of r.debords) console.error(`      hors cadre : ${d}`);
          for (const e of r.etroites) console.error(`      marge sous ${MARGE_MIN_PX} px — ${e}`);
        }
      } finally {
        await page.close();
      }
    }
  }
} finally {
  await nav.close();
}

if (echecs === 0) {
  console.log(`✓ En-tête : ${controles} largeurs × pages contrôlées, aucun chevauchement ni débord.`);
  console.log(`  De ${LARGEURS[0]} à ${LARGEURS.at(-1)} px, polices chargées, tolérance ${TOLERANCE_PX} px,`);
  console.log(`  marge minimale exigée autour du menu : ${MARGE_MIN_PX} px.`);
} else {
  console.error(`\n✗ ${echecs} configuration(s) en défaut sur ${controles}.`);
  process.exitCode = 1;
}
