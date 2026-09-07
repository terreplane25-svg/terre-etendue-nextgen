/**
 * verifier-sources-texte.mjs — Aucun fichier source ne doit être binaire.
 *
 * POURQUOI CE CONTRÔLE EXISTE
 * ───────────────────────────
 * Trois fois dans ce dépôt, un octet NUL réel s'est glissé dans un littéral
 * TypeScript en écrivant du code qui compare des octets — « Exif\0\0 », le
 * « crx\0 » de Canon, le nettoyage des chaînes ICC. Le fichier devient alors
 * binaire : git le traite comme tel, les diffs deviennent illisibles, et
 * surtout la comparaison qu'on croit lire dans le source n'est PAS celle qui
 * est écrite. Le compilateur ne dit rien, les tests passent, et la relecture
 * ne voit rien parce qu'il n'y a rien à voir.
 *
 * La règle est donc : un octet nul dans un source s'écrit en échappement, jamais en
 * clair. Ce contrôle la fait tenir.
 *
 * Il vérifie aussi l'absence d'octets de contrôle C0 autres que la tabulation
 * et le saut de ligne, pour la même raison : ils sont invisibles à la lecture.
 *
 *     node scripts/verifier-sources-texte.mjs
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));

/** Les arborescences de sources écrites à la main. */
const DOSSIERS = ['src', 'scripts', 'outils'];

/** Les extensions de fichiers qui doivent rester du texte. */
const EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.mjs', '.py', '.css', '.md', '.json']);

/** Ce qu'on ne parcourt pas : dépendances, caches, environnements. */
const IGNORES = new Set(['node_modules', '__pycache__', '.venv', '.next', '.git', 'dist', 'build']);

function parcourir(dossier) {
  const out = [];
  let entrees;
  try { entrees = readdirSync(dossier); } catch { return out; }
  for (const nom of entrees) {
    if (IGNORES.has(nom)) continue;
    const chemin = join(dossier, nom);
    let st;
    try { st = statSync(chemin); } catch { continue; }
    if (st.isDirectory()) out.push(...parcourir(chemin));
    else if (EXTENSIONS.has(extname(nom))) out.push(chemin);
  }
  return out;
}

const fautifs = [];
let examines = 0;

for (const dossier of DOSSIERS) {
  for (const chemin of parcourir(join(RACINE, dossier))) {
    examines += 1;
    const octets = readFileSync(chemin);
    const problemes = [];
    for (let i = 0; i < octets.length; i++) {
      const o = octets[i];
      // Tabulation (9), saut de ligne (10) et retour chariot (13) sont légitimes.
      if (o === 0 || (o < 32 && o !== 9 && o !== 10 && o !== 13)) {
        // On rend le contexte lisible : sans lui, « octet 0 à la position
        // 4312 » n'aide personne à trouver le littéral fautif.
        const debut = Math.max(0, i - 60);
        const contexte = octets
          .subarray(debut, i + 20)
          .toString('utf8')
          .replace(/[\u0000-\u001f]/g, (c) => `\\x${c.charCodeAt(0).toString(16).padStart(2, '0')}`);
        problemes.push({ position: i, octet: o, contexte });
        if (problemes.length >= 3) break;
      }
    }
    if (problemes.length > 0) fautifs.push({ chemin: relative(RACINE, chemin), problemes });
  }
}

if (fautifs.length > 0) {
  console.error(`\n✗ ${fautifs.length} fichier(s) source contiennent des octets de contrôle en clair.\n`);
  for (const f of fautifs) {
    console.error(`  ${f.chemin}`);
    for (const p of f.problemes) {
      console.error(`    octet 0x${p.octet.toString(16).padStart(2, '0')} à la position ${p.position}`);
      console.error(`      …${p.contexte}…`);
    }
  }
  console.error(
    '\n  Un octet nul dans un source s’écrit « \\u0000 », jamais en clair : sinon le\n'
    + '  fichier devient binaire, et la comparaison qu’on croit lire dans le source\n'
    + '  n’est pas celle qui est écrite.\n',
  );
  process.exitCode = 1;
} else {
  console.log(`✓ Sources en texte pur : ${examines} fichiers examinés, aucun octet de contrôle en clair.`);
}
