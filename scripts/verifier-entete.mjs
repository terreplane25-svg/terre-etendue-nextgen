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
 * IL VÉRIFIE AUSSI LES CONTRASTES
 * ───────────────────────────────
 * Le libellé de la section ACTIVE prenait la couleur de son pilier comme
 * couleur de texte : 2,59:1 pour le saffron de la Bibliothèque, très en
 * dessous du seuil de 4,5:1. Autrement dit, le mot qui vous dit où vous êtes
 * était le moins lisible de l'en-tête.
 *
 * Un fait structurel a guidé la correction : aucune couleur fixe ne peut
 * servir de texte dans les DEUX thèmes. Assez sombre pour le blanc, elle
 * tombe sous le seuil sur la carte sombre — et réciproquement. Il a donc fallu
 * une variante par thème, la plus proche de l'originale qui atteigne 4,5:1.
 *
 * Ce contrôle balaie les HUIT sections, chacune ayant sa teinte : n'en tester
 * qu'une ne dirait rien des sept autres.
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

// ── Les contrastes ──────────────────────────────────────────────────────────
//
// Le lien actif porte la teinte de sa section : en tester une seule laisserait
// les sept autres sans contrôle. Le soulignement est jugé à 3:1 — un trait
// n'est pas un mot — et le texte au seuil de sa taille.
const SECTIONS_PAGES = ['/library', '/headquarters', '/observatory', '/experiences',
  '/lab', '/laboratoire', '/enseignants', '/about'];

/**
 * Les largeurs où les contrastes sont relevés : une par palier, plus le
 * téléphone.
 *
 * Une première version ne mesurait qu'à 1280 px, et la casse délibérée a
 * montré ce que ce point unique laissait passer. Deux défauts y échappaient
 * pour la même raison — ce qui n'est pas visible à 1280 n'est pas mesuré :
 *
 *   · le vert du logo échoue à 390 px, où il fait 18 px gras et relève donc du
 *     seuil de 4,5:1 ; à 1280 px il fait 24 px et relève de celui de 3:1, où
 *     il passe. Le défaut n'existe qu'en dessous du palier de bureau.
 *   · le libellé de la recherche est MASQUÉ sous 1440 px. À 1280 px il n'est
 *     pas à l'écran, donc jamais jugé, et son gris fantôme à 1,92:1 revenait
 *     sans que rien ne le signale.
 *
 * Un contrôle qui ne regarde qu'un point ne garantit que ce point.
 */
const LARGEURS_CONTRASTE = [390, 1152, 1280, 1440, 1580];

const nav2 = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
try {
  // Le lien ACTIF porte la teinte de sa section : les huit pages sont donc
  // parcourues, à la largeur où toutes les teintes sont à l'écran.
  for (const theme of ['light', 'dark']) {
    for (const chemin of SECTIONS_PAGES) {
      const page = await nav2.newPage({
        viewport: { width: 1280, height: 600 }, colorScheme: theme,
      });
      try {
        // Les transitions sont COUPÉES avant de mesurer. Les liens du menu
        // portent `transition: color 0.15s` : mesurer à 120 ms attrapait une
        // couleur intermédiaire, et le contrôle rapportait des échecs qui
        // n'existaient pas à l'état stabilisé — 4,43:1 au lieu de 4,57:1.
        // Attendre plus longtemps aurait marché aujourd'hui et cassé le jour
        // où quelqu'un allonge la transition ; couper l'animation retire le
        // facteur temps de l'équation.
        await page.addStyleTag({
          content: '*, *::before, *::after { transition: none !important; '
            + 'animation: none !important; }',
        });
        await page.goto(RACINE + chemin, { waitUntil: 'domcontentloaded' });
        await page.addStyleTag({
          content: '*, *::before, *::after { transition: none !important; '
            + 'animation: none !important; }',
        });
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(120);
        const r = await page.evaluate(() => {
          const lum = (s) => {
            const [r, g, b] = s.match(/[\d.]+/g).slice(0, 3).map((v) => v / 255)
              .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
            return 0.2126 * r + 0.7152 * g + 0.0722 * b;
          };
          const fond = (el) => {
            for (let x = el; x; x = x.parentElement) {
              const c = getComputedStyle(x).backgroundColor;
              if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c;
            }
            return 'rgb(255, 255, 255)';
          };
          const ratio = (a, b) => {
            const [h, l] = [lum(a), lum(b)].sort((x, y) => y - x);
            return (h + 0.05) / (l + 0.05);
          };
          const actif = [...document.querySelectorAll('header nav > div > a')]
            .find((a) => !/transparent|rgba\(0, 0, 0, 0\)/
              .test(getComputedStyle(a).borderBottomColor));
          if (!actif) return null;
          const st = getComputedStyle(actif);
          const px = parseFloat(st.fontSize);
          const gras = parseInt(st.fontWeight, 10) >= 700;
          // Tout texte de l'en-tête, pas seulement le lien actif : le libellé
          // de la recherche et le vert du logo ont échoué là aussi.
          const tous = [];
          for (const el of document.querySelectorAll('header *')) {
            const t = [...el.childNodes].filter((x) => x.nodeType === 3)
              .map((x) => x.textContent).join('').trim();
            if (t.length < 2 || !el.offsetWidth) continue;
            const e = getComputedStyle(el);
            if (e.visibility === 'hidden' || e.display === 'none') continue;
            const p = parseFloat(e.fontSize);
            const g = parseInt(e.fontWeight, 10) >= 700;
            const seuil = p >= 24 || (g && p >= 18.66) ? 3 : 4.5;
            const rr = ratio(e.color, fond(el));
            if (rr < seuil) tous.push(`« ${t.slice(0, 24)} » ${rr.toFixed(2)}:1 < ${seuil} (${p} px)`);
          }
          return {
            t: actif.textContent.trim().slice(0, 20),
            seuilTexte: px >= 24 || (gras && px >= 18.66) ? 3 : 4.5,
            texte: ratio(st.color, fond(actif)),
            trait: ratio(st.borderBottomColor, fond(actif)),
            tous,
          };
        });
        controles += 1;
        if (r === null) {
          echecs += 1;
          console.error(`  ✗ contraste ${theme} ${chemin} : aucun lien actif — le contrôle ne mesure rien`);
        } else {
          const soucis = [...r.tous];
          if (r.texte < r.seuilTexte) {
            soucis.push(`lien actif « ${r.t} » : ${r.texte.toFixed(2)}:1 < ${r.seuilTexte}`);
          }
          if (r.trait < 3) soucis.push(`soulignement : ${r.trait.toFixed(2)}:1 < 3`);
          if (soucis.length > 0) {
            echecs += 1;
            console.error(`  ✗ contraste ${theme} ${chemin}`);
            for (const x of soucis) console.error(`      ${x}`);
          }
        }
      } finally {
        await page.close();
      }
    }
  }

  // Second balayage : TOUT le texte de l'en-tête, à chaque largeur et dans les
  // deux thèmes. C'est celui qui attrape ce qui n'apparaît qu'à certaines
  // tailles — le libellé de la recherche au-delà de 1440 px, le logo compact
  // en dessous du palier de bureau.
  for (const theme of ['light', 'dark']) {
    for (const largeur of LARGEURS_CONTRASTE) {
      const page = await nav2.newPage({
        viewport: { width: largeur, height: 600 }, colorScheme: theme,
      });
      try {
        await page.addStyleTag({
          content: '*, *::before, *::after { transition: none !important; '
            + 'animation: none !important; }',
        });
        await page.goto(`${RACINE}/library`, { waitUntil: 'domcontentloaded' });
        await page.addStyleTag({
          content: '*, *::before, *::after { transition: none !important; '
            + 'animation: none !important; }',
        });
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(120);
        const soucis = await page.evaluate(() => {
          const lum = (s) => {
            const [r, g, b] = s.match(/[\d.]+/g).slice(0, 3).map((v) => v / 255)
              .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
            return 0.2126 * r + 0.7152 * g + 0.0722 * b;
          };
          const fond = (el) => {
            for (let x = el; x; x = x.parentElement) {
              const c = getComputedStyle(x).backgroundColor;
              if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c;
            }
            return 'rgb(255, 255, 255)';
          };
          const ratio = (a, b) => {
            const [h, l] = [lum(a), lum(b)].sort((x, y) => y - x);
            return (h + 0.05) / (l + 0.05);
          };
          const out = [];
          for (const el of document.querySelectorAll('header *')) {
            // Le texte porté DIRECTEMENT par l'élément : les liens du menu
            // contiennent une icône, et les écarter sur `children.length`
            // laissait le lien actif hors de toute mesure.
            const t = [...el.childNodes].filter((x) => x.nodeType === 3)
              .map((x) => x.textContent).join('').trim();
            if (t.length < 2 || !el.offsetWidth) continue;
            const e = getComputedStyle(el);
            if (e.visibility === 'hidden' || e.display === 'none') continue;
            const p = parseFloat(e.fontSize);
            const g = parseInt(e.fontWeight, 10) >= 700;
            const seuil = p >= 24 || (g && p >= 18.66) ? 3 : 4.5;
            const rr = ratio(e.color, fond(el));
            if (rr < seuil) out.push(`« ${t.slice(0, 24)} » ${rr.toFixed(2)}:1 < ${seuil} (${p} px)`);
          }
          return out;
        });
        controles += 1;
        if (soucis.length > 0) {
          echecs += 1;
          console.error(`  ✗ contraste ${theme} @ ${largeur} px`);
          for (const x of soucis) console.error(`      ${x}`);
        }
      } finally {
        await page.close();
      }
    }
  }
} finally {
  await nav2.close();
}

if (echecs === 0) {
  console.log(`✓ En-tête : ${controles} contrôles — géométrie et contrastes, aucun écart.`);
  console.log(`  De ${LARGEURS[0]} à ${LARGEURS.at(-1)} px, polices chargées, tolérance ${TOLERANCE_PX} px,`);
  console.log(`  marge minimale exigée autour du menu : ${MARGE_MIN_PX} px.`);
  console.log(`  Contrastes : les 8 sections actives, plus tout le texte de l'en-tête`);
  console.log(`  à ${LARGEURS_CONTRASTE.length} largeurs — le tout dans les deux thèmes.`);
} else {
  console.error(`\n✗ ${echecs} configuration(s) en défaut sur ${controles}.`);
  process.exitCode = 1;
}
