/**
 * verifier-port-fiche.mjs — Épingle le port TypeScript de la fiche terrain.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/visee-optique/vecteurs-or-fiche.json` : structure des blocs, champs,
 * réserves, et le rendu TEXTE COMPLET — caractère par caractère.
 *
 * Pourquoi le texte entier plutôt qu'un résumé : la fiche EST du texte. Une
 * apostrophe droite devenue typographique, une coupure de ligne un mot plus
 * loin, un « du » redevenu « de le » ne cassent rien, ne lèvent rien, et
 * s'impriment sur la feuille que le volontaire emporte. La divergence
 * d'apostrophe entre Python et TypeScript s'est déjà produite quatre fois dans
 * ce dépôt.
 *
 *     node scripts/verifier-port-fiche.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-fiche.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'visee-optique');
const VECTEURS = join(DIR, 'vecteurs-or-fiche.json');

const ecarts = [];
function faux(sujet, champ, attendu, obtenu) {
  ecarts.push({ sujet, champ, attendu, obtenu });
}
function comparer(sujet, champ, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (JSON.stringify(a) !== JSON.stringify(o)) {
    faux(sujet, champ, JSON.stringify(a), JSON.stringify(o));
  }
}

/**
 * Compare deux textes et, en cas d'écart, DÉSIGNE la première ligne et le
 * premier caractère qui diffèrent. Sans cela, un écart d'une apostrophe dans
 * un document de deux cents lignes se solde par deux pavés à comparer à l'œil
 * — exactement ce que ce vérificateur existe pour éviter.
 */
function comparerTexte(sujet, attendu, obtenu) {
  if (attendu === obtenu) return;
  const la = attendu.split('\n');
  const lo = obtenu.split('\n');
  for (let i = 0; i < Math.max(la.length, lo.length); i++) {
    if (la[i] === lo[i]) continue;
    const a = la[i] ?? '(ligne absente)';
    const o = lo[i] ?? '(ligne absente)';
    let col = 0;
    while (col < a.length && col < o.length && a[col] === o[col]) col += 1;
    faux(sujet, `rendu texte, ligne ${i + 1}, colonne ${col + 1}`
      + ` (attendu ${JSON.stringify(a[col] ?? '')}, obtenu ${JSON.stringify(o[col] ?? '')})`,
      a, o);
    return;
  }
  faux(sujet, 'rendu texte', `${la.length} lignes`, `${lo.length} lignes`);
}

/** La structure TypeScript remise dans la forme du Python, sans rien omettre. */
function enFormePython(f, distanceM, nomFichier) {
  return {
    milieu: f.milieu,
    milieu_nom: f.milieuNom,
    reference_verticale: f.referenceVerticale,
    titre: f.titre,
    sous_titre: f.sousTitre,
    horodatage: f.horodatage,
    discriminante: f.discriminante,
    nom_fichier: nomFichier(f, distanceM),
    champs_ecartes: f.champsEcartes.map((x) => [...x]),
    sections: f.sections.map((s) => ({
      numero: s.numero,
      titre: s.titre,
      releves: s.releves.map((x) => [...x]),
      champs: s.champs.map((c) => ({
        libelle: c.libelle, unite: c.unite,
        pourquoi: c.pourquoi, obligatoire: c.obligatoire,
      })),
      consignes: [...s.consignes],
      reserves: [...s.reserves],
      sous_scelle: s.sousScelle,
    })),
  };
}

const dossier = mkdtempSync(join(tmpdir(), 'fiche-'));
try {
  // `simulation.ts` dépend de `noyau.ts` : les trois sont compilés ensemble,
  // sans quoi Node refuse le module au chargement.
  execFileSync('npx', ['--no-install', 'tsc',
    join(DIR, 'fiche-terrain.ts'), join(DIR, 'simulation.ts'), join(DIR, 'noyau.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  const fn = join(dossier, 'fiche-terrain.js');

  // La fiche ne doit dépendre QUE de `simulation` : elle ne calcule rien
  // elle-même, et une dépendance à la géodésie signalerait qu'elle a commencé.
  // Le contrôle se fait AVANT la réécriture des extensions, sur les imports
  // tels que tsc les a émis.
  const imports = [...new Set(readFileSync(fn, 'utf8').match(/from ['"]\.[^'"]*['"]/g) ?? [])];
  if (imports.length !== 1 || !imports[0].includes('simulation')) {
    throw new Error(`fiche-terrain.ts a pris des dépendances inattendues : ${imports.join(', ')}`);
  }

  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. La
  // substitution est COMPTÉE : sans elle, Node refuse le module sans dire
  // lequel, et le message ne désigne pas le fichier fautif.
  let reecrits = 0;
  for (const f of ['fiche-terrain.js', 'simulation.js', 'noyau.js']) {
    const chemin = join(dossier, f);
    const code = readFileSync(chemin, 'utf8');
    const corrige = code.replace(/(from ['"]\.\/[^'"]*)(['"])/g, (_, a, b) => {
      reecrits += 1;
      return `${a}.js${b}`;
    });
    writeFileSync(chemin, corrige);
  }
  if (reecrits < 2) {
    throw new Error(`Seuls ${reecrits} imports relatifs réécrits : la compilation a changé de forme.`);
  }

  const F = await import(pathToFileURL(fn).href);
  // Les formateurs vivent dans `simulation` : la fiche et l'écran écrivent
  // les mêmes chiffres, et une seule implémentation les produit.
  const S = await import(pathToFileURL(join(dossier, 'simulation.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  // ── Les constantes ────────────────────────────────────────────────────────
  const c = v.constantes;
  comparer('constantes', 'pixels min écart', c.pixels_min_ecart, F.PIXELS_MIN_ECART);
  comparer('constantes', 'largeur txt', c.largeur_txt, F.LARGEUR_TXT);
  comparer('constantes', 'préfixe de référence',
    c.prefixe_reference_attendu, F.PREFIXE_REFERENCE_ATTENDU);
  comparer('constantes', 'champs écartés', c.champs_ecartes,
    F.CHAMPS_ECARTES.map((x) => [...x]));
  n += 4;
  for (const [cle, d] of Object.entries(c.milieux)) {
    const t = F.MILIEUX[cle];
    if (!t) { faux('milieux', cle, 'présent', 'absent du port'); n += 1; continue; }
    comparer(`milieu ${cle}`, 'nom', d.nom, t.nom);
    comparer(`milieu ${cle}`, 'référence', d.reference, t.reference);
    comparer(`milieu ${cle}`, 'réserve', d.reserve, t.reserve);
    n += 3;
  }
  // Un milieu EN TROP dans le port serait une divergence de contrat, même s'il
  // ne contredit aucune valeur.
  comparer('milieux', 'liste', Object.keys(c.milieux).sort(), Object.keys(F.MILIEUX).sort());
  n += 1;

  // ── La convention d'arrondi ──────────────────────────────────────────────
  //
  // `toFixed` arrondit les égalités à l'écart de zéro, le « %.*f » du Python
  // les arrondit vers le pair. 1,25 rendait 1,2 d'un côté et 1,3 de l'autre,
  // sur le seuil en mètres — affiché à l'écran ET imprimé sur la fiche.
  for (const a of v.arrondis) {
    const s2 = `arrondi de ${a.valeur}`;
    comparer(s2, 'mètres', a.metres, S.formatMetres(a.valeur));
    comparer(s2, 'pourcent', a.pourcent, S.formatPourcent(a.valeur));
    comparer(s2, 'k', a.k, S.formatK(a.valeur));
    n += 3;
  }

  // ── Le replieur : il décide de toutes les coupures ───────────────────────
  for (const r of v.replis) {
    comparer(`repli ${JSON.stringify(r.texte.slice(0, 24))} @${r.largeur}`,
      'lignes', r.lignes, F.replier(r.texte, r.largeur, r.premier, r.suite));
    n += 1;
  }

  // ── Les fiches ───────────────────────────────────────────────────────────
  for (const cas of v.cas) {
    const e = cas.entree;
    const sujet = cas.nom;
    const verdict = {
      discriminante: cas.verdict.discriminante,
      motif: cas.verdict.motif,
      hauteurMasqueeBaseM: cas.verdict.hauteur_masquee_base_m,
      fractionMasqueeBase: cas.verdict.fraction_masquee_base,
      hauteurMasqueePlatM: cas.verdict.hauteur_masquee_plat_m,
      ecartEntreModelesM: cas.verdict.ecart_entre_modeles_m,
      seuilApplique: cas.verdict.seuil_applique,
    };
    const fiche = F.construireFiche({
      milieu: e.milieu,
      horodatage: e.horodatage,
      obsLatitude: e.obs_latitude,
      obsLongitude: e.obs_longitude,
      obsLibelle: e.obs_libelle,
      cibleLatitude: e.cible_latitude,
      cibleLongitude: e.cible_longitude,
      cibleLibelle: e.cible_libelle,
      distanceM: e.distance_m,
      azimutDeg: e.azimut_deg,
      hauteurObservateurM: e.hauteur_observateur_m,
      hauteurCibleM: e.hauteur_cible_m,
      masqueeEnveloppeMinM: e.masquee_enveloppe_min_m,
      masqueeEnveloppeMaxM: e.masquee_enveloppe_max_m,
      kEmploye: e.k_employe,
      kPersonnalise: e.k_personnalise,
      verdict,
    });

    const attendu = cas.fiche;
    const obtenu = enFormePython(fiche, e.distance_m, F.nomFichier);
    // Comparaison bloc par bloc, pour que l'écart soit DÉSIGNÉ plutôt que
    // noyé dans un objet de deux cents lignes.
    for (const cle of Object.keys(attendu)) {
      // `sections` et `txt` sont comparés à part, l'un bloc par bloc et
      // l'autre caractère par caractère : les passer ici les comparerait à un
      // champ absent de la forme rendue, et douze faux écarts masqueraient
      // les vrais.
      if (cle === 'sections' || cle === 'txt') continue;
      comparer(sujet, cle, attendu[cle], obtenu[cle]);
      n += 1;
    }
    comparer(sujet, 'nombre de blocs', attendu.sections.length, obtenu.sections.length);
    n += 1;
    for (let i = 0; i < attendu.sections.length; i++) {
      comparer(sujet, `bloc ${attendu.sections[i].numero}`,
        attendu.sections[i], obtenu.sections[i]);
      n += 1;
    }
    // Un champ EN TROP côté port serait une divergence de contrat.
    const enTrop = Object.keys(obtenu).filter((k) => !(k in attendu));
    if (enTrop.length > 0) comparer(sujet, 'champs en trop', [], enTrop);

    comparerTexte(sujet, attendu.txt, F.rendreTxt(fiche));
    n += 1;
  }

  // ── Les refus ────────────────────────────────────────────────────────────
  const valide = {
    milieu: 'mer', horodatage: '2026-01-01T00:00:00Z',
    obsLatitude: 50, obsLongitude: 1, obsLibelle: null,
    cibleLatitude: 51, cibleLongitude: 1, cibleLibelle: null,
    distanceM: 30000, azimutDeg: 300,
    hauteurObservateurM: 2, hauteurCibleM: 110,
    masqueeEnveloppeMinM: 30, masqueeEnveloppeMaxM: 50,
    kEmploye: 0.13, kPersonnalise: false,
    verdict: {
      discriminante: true, motif: 'x', hauteurMasqueeBaseM: 40,
      fractionMasqueeBase: 0.36, hauteurMasqueePlatM: 0,
      ecartEntreModelesM: 40, seuilApplique: 0.1,
    },
  };
  //
  // Le MOTIF est vérifié, pas seulement le fait qu'une erreur soit levée. Une
  // première version se contentait de « quelque chose a été jeté » : une
  // rupture qui supprimait la garde laissait alors passer un `TypeError` sur
  // un objet indéfini, et le mutant survivait. Un plantage n'est pas un refus.
  for (const [nom, patch, attendu] of [
    ['milieu inconnu', { milieu: 'océan' }, 'Milieu inconnu'],
    ['horodatage vide', { horodatage: '   ' }, "L'horodatage manque"],
    ['distance nulle', { distanceM: 0 }, 'La distance doit'],
    ['distance négative', { distanceM: -1 }, 'La distance doit'],
    ['cible de hauteur nulle', { hauteurCibleM: 0 }, 'hauteur de la cible'],
    ['observateur sous la surface', { hauteurObservateurM: -0.5 }, "l'observateur"],
  ]) {
    let err = null;
    try { F.construireFiche({ ...valide, ...patch }); } catch (e) { err = e; }
    if (err === null) {
      faux(`refus : ${nom}`, 'erreur', 'erreur levée', 'aucune');
    } else if (err.name !== 'FicheError') {
      faux(`refus : ${nom}`, 'nature du refus', 'FicheError',
        `${err.name} — ${err.message}`);
    } else if (!err.message.includes(attendu)) {
      faux(`refus : ${nom}`, 'motif du refus', attendu, err.message);
    }
    n += 1;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 12)) {
      console.error(`  ${e.sujet}\n    ${e.champ} :\n      attendu ${String(e.attendu).slice(0, 400)}\n      obtenu  ${String(e.obtenu).slice(0, 400)}`);
    }
    if (ecarts.length > 12) console.error(`  … et ${ecarts.length - 12} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
