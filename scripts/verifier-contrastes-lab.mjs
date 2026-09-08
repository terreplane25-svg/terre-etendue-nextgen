/**
 * verifier-contrastes-lab.mjs — Mesure les contrastes des cartes d'outils.
 *
 * POURQUOI UN CONTRÔLE ET NON UNE PROMESSE
 * ────────────────────────────────────────
 * La version précédente des cartes posait le descriptif en `--ink-muted`
 * (3,25:1 sur blanc) et les étiquettes en `--ink-ghost` sur gris (1,76:1).
 * Personne ne l'avait décidé : les valeurs avaient dérivé, et un texte à
 * 1,76:1 est effacé sans que rien ne le signale. Un commentaire promettant
 * « conforme AA » aurait vieilli aussi mal.
 *
 * Ce script ne fait donc aucune supposition : il LIT les couleurs des outils
 * dans `src/lib/lab-tools.ts` et les tokens dans `src/styles/globals.css`,
 * puis applique la formule WCAG 2.1. Ajouter un outil d'une couleur trop
 * pâle, ou éclaircir un token, échoue ici.
 *
 * CE QU'IL VÉRIFIE, ET CE QU'IL NE PEUT PAS VÉRIFIER
 * ──────────────────────────────────────────────────
 * Il vérifie les couples couleur/fond des rôles de texte et des composants
 * non textuels, dans les DEUX thèmes. Il ne vérifie pas que ces couples sont
 * bien ceux que le composant emploie — pour cela il relit les tailles et les
 * rôles déclarés dans `LabClient.tsx` par motif, ce qui attrape le cas qui
 * compte : un titre redescendu sous le seuil du texte large, où la couleur de
 * pilier cesserait d'être admise.
 *
 *     node scripts/verifier-contrastes-lab.mjs
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));

let echecs = 0;
let controles = 0;
function verifier(nom, condition, detail = '') {
  controles += 1;
  if (!condition) {
    echecs += 1;
    console.error(`  ✗ ${nom}${detail ? `\n      ${detail}` : ''}`);
  }
}

/** Luminance relative, WCAG 2.1 §dfn-relative-luminance. */
function luminance(hex) {
  const c = hex.replace('#', '');
  if (!/^[0-9a-fA-F]{6}$/.test(c)) throw new Error(`couleur illisible : ${hex}`);
  const [r, g, b] = [0, 2, 4]
    .map((i) => parseInt(c.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function ratio(a, b) {
  const [haut, bas] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (haut + 0.05) / (bas + 0.05);
}

/**
 * Le seuil applicable. WCAG 2.1 : 4,5:1 pour un texte normal, 3:1 pour un
 * texte LARGE — au moins 24 px, ou 18,66 px s'il est gras.
 */
function seuilTexte(px, gras) {
  return px >= 24 || (gras && px >= 18.66) ? 3.0 : 4.5;
}

// ── Ce que les fichiers déclarent RÉELLEMENT ────────────────────────────────

const tokens = (theme) => {
  const css = readFileSync(join(RACINE, 'src/styles/globals.css'), 'utf8');
  const bloc = theme === 'clair'
    ? css.slice(css.indexOf(':root'), css.indexOf('[data-theme="dark"]'))
    : css.slice(css.indexOf('[data-theme="dark"]'));
  const lire = (nom) => {
    const m = new RegExp(`--${nom}:\\s*(#[0-9a-fA-F]{6})`).exec(bloc);
    if (m === null) throw new Error(`token --${nom} introuvable en thème ${theme}`);
    return m[1];
  };
  return {
    bg: lire('bg'), card: lire('card'), ink: lire('ink'),
    inkSoft: lire('ink-soft'), inkMuted: lire('ink-muted'), border: lire('border'),
  };
};

const couleursOutils = (() => {
  const src = readFileSync(join(RACINE, 'src/lib/lab-tools.ts'), 'utf8');
  const couleurs = [...src.matchAll(/color:\s*'(#[0-9a-fA-F]{6})'/g)].map((m) => m[1]);
  if (couleurs.length === 0) throw new Error('aucune couleur d’outil lue : le fichier a changé de forme');
  return [...new Set(couleurs)];
})();

const carte = readFileSync(join(RACINE, 'src/app/lab/LabClient.tsx'), 'utf8');

// ── 1. Le titre : sa taille autorise-t-elle la couleur de pilier ? ──────────
//
// C'est LE contrôle qui compte. Les couleurs de pilier plafonnent autour de
// 3,3:1 sur blanc : admises en texte large, illégales en texte normal. Si
// quelqu'un ramène le titre à 15 px, l'état actif devient non conforme sans
// qu'aucun test d'apparence ne s'en aperçoive.
const bloc = carte.slice(carte.indexOf('function ToolCard('), carte.indexOf('function SimulatorLoader('));
const titre = /fontSize: (\d+(?:\.\d+)?), fontWeight: (\d+),\n\s+color: active \? tool\.color/.exec(bloc);
verifier('la taille du titre est lisible dans le composant', titre !== null,
  'le motif du titre a changé : ce contrôle ne mesure plus rien');
if (titre !== null) {
  const px = Number(titre[1]);
  const gras = Number(titre[2]) >= 700;
  const seuil = seuilTexte(px, gras);
  verifier(`titre à ${px} px / ${titre[2]} : le seuil applicable est ${seuil}:1`,
    seuil === 3.0,
    `à cette taille le seuil est ${seuil}:1, et aucune couleur de pilier ne l’atteint`);
  for (const theme of ['clair', 'sombre']) {
    const t = tokens(theme);
    for (const c of couleursOutils) {
      const r = ratio(c, t.card);
      verifier(`titre actif ${c} sur carte ${theme}`, r >= seuil,
        `${r.toFixed(2)}:1 < ${seuil}:1`);
    }
    verifier(`titre au repos sur carte ${theme}`, ratio(t.ink, t.card) >= 4.5,
      `${ratio(t.ink, t.card).toFixed(2)}:1`);
  }
}

// ── 2. Le descriptif et les étiquettes : texte normal, seuil 4,5:1 ─────────
for (const theme of ['clair', 'sombre']) {
  const t = tokens(theme);
  verifier(`descriptif (--ink-soft sur --card) en ${theme}`,
    ratio(t.inkSoft, t.card) >= 4.5, `${ratio(t.inkSoft, t.card).toFixed(2)}:1`);
  verifier(`étiquettes (--ink-soft sur --bg) en ${theme}`,
    ratio(t.inkSoft, t.bg) >= 4.5, `${ratio(t.inkSoft, t.bg).toFixed(2)}:1`);
  // Et le token qui échouait ne doit PAS revenir porter un mot dans la carte.
  verifier(`--ink-muted reste absent de la carte (${theme})`,
    !bloc.includes('--ink-muted'),
    `--ink-muted vaut ${ratio(t.inkMuted, t.card).toFixed(2)}:1 sur la carte : sous le seuil`);
}

// ── 3. Le numéro : pastille pleine, texte blanc ─────────────────────────────
const num = /fontSize: (\d+(?:\.\d+)?), fontFamily: dash\.fontMono, fontWeight: (\d+),\n\s+color: '#FFFFFF', background: tool\.color/.exec(bloc);
verifier('la pastille du numéro est lisible dans le composant', num !== null);
if (num !== null) {
  const seuil = seuilTexte(Number(num[1]), Number(num[2]) >= 700);
  for (const c of couleursOutils) {
    const r = ratio('#FFFFFF', c);
    verifier(`numéro blanc sur ${c} (${num[1]} px / ${num[2]})`, r >= seuil,
      `${r.toFixed(2)}:1 < ${seuil}:1`);
  }
}

// ── 4. La barre d'accentuation et la bordure : non textuel, seuil 3:1 ──────
for (const theme of ['clair', 'sombre']) {
  const t = tokens(theme);
  for (const c of couleursOutils) {
    verifier(`barre/bordure ${c} sur carte ${theme}`, ratio(c, t.card) >= 3.0,
      `${ratio(c, t.card).toFixed(2)}:1 < 3:1`);
  }
}

// ── 5. L'anneau de focus existe, et il est visible ─────────────────────────
const css = readFileSync(join(RACINE, 'src/styles/globals.css'), 'utf8');
verifier('un anneau de focus est déclaré pour la carte',
  /\.tei-carte-outil:focus-visible\s*\{[^}]*outline:/.test(css),
  'sans lui la carte est atteignable au clavier mais invisible');
verifier('la carte porte bien la classe du focus', bloc.includes('tei-carte-outil'));

if (echecs === 0) {
  console.log(`✓ Contrastes des cartes du Lab : ${controles} contrôles, aucun écart.`);
  console.log('  Mesuré sur les couleurs réellement déclarées, dans les deux thèmes.');
} else {
  console.error(`\n✗ ${echecs} écart(s) sur ${controles} contrôles.`);
  process.exitCode = 1;
}
