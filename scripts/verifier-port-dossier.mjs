/**
 * verifier-port-dossier.mjs — Épingle le port du relevé unifié.
 *
 * La comparaison porte sur le DOCUMENT ENTIER, sérialisé : une clé oubliée,
 * renommée ou ajoutée d'un seul côté fait tomber le contrôle. C'est plus sévère
 * qu'une liste de champs choisis, et c'est ce qu'on veut d'un relevé dont la
 * forme est le contrat.
 *
 *     node scripts/verifier-port-dossier.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-dossier.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-dossier.json');

const ecarts = [];

/**
 * Compare deux documents en NOMMANT le chemin de la divergence.
 *
 * Un simple `JSON.stringify` inégal dirait « les documents diffèrent » sans
 * dire où — sur une structure à six blocs et une centaine de champs, c'est
 * inutilisable. On descend donc dans l'arbre.
 */
function comparerProfond(sujet, chemin, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (a === null || o === null || typeof a !== 'object' || typeof o !== 'object') {
    if (JSON.stringify(a) !== JSON.stringify(o)) {
      ecarts.push({ sujet, chemin, attendu: JSON.stringify(a), obtenu: JSON.stringify(o) });
    }
    return;
  }
  if (Array.isArray(a) !== Array.isArray(o)) {
    ecarts.push({ sujet, chemin, attendu: Array.isArray(a) ? 'liste' : 'objet', obtenu: Array.isArray(o) ? 'liste' : 'objet' });
    return;
  }
  if (Array.isArray(a)) {
    if (a.length !== o.length) {
      ecarts.push({ sujet, chemin: `${chemin} (longueur)`, attendu: a.length, obtenu: o.length });
      return;
    }
    a.forEach((x, i) => comparerProfond(sujet, `${chemin}[${i}]`, x, o[i]));
    return;
  }
  const cles = new Set([...Object.keys(a), ...Object.keys(o)]);
  for (const c of cles) {
    if (!(c in a)) { ecarts.push({ sujet, chemin: `${chemin}.${c}`, attendu: '(absent)', obtenu: JSON.stringify(o[c]).slice(0, 120) }); continue; }
    if (!(c in o)) { ecarts.push({ sujet, chemin: `${chemin}.${c}`, attendu: JSON.stringify(a[c]).slice(0, 120), obtenu: '(absent)' }); continue; }
    comparerProfond(sujet, `${chemin}.${c}`, a[c], o[c]);
  }
}

const dossier = mkdtempSync(join(tmpdir(), 'dossier-'));
try {
  const sources = ['dossier.ts', 'conteneurs.ts', 'isobmff.ts', 'makernotes.ts',
    'noyau.ts', 'provenance.ts', 'quantification.ts', 'telemetrie.ts'].map((f) => join(DIR, f));
  execFileSync('npx', ['--no-install', 'tsc', ...sources,
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. On compte les
  // remplacements : un remplacement silencieusement nul laisserait un import
  // que Node refuserait plus loin sans dire pourquoi.
  const modules = ['conteneurs', 'isobmff', 'makernotes', 'noyau', 'provenance', 'quantification', 'telemetrie', 'dossier'];
  let total = 0;
  for (const f of readdirSync(dossier).filter((x) => x.endsWith('.js'))) {
    const p = join(dossier, f);
    let code = readFileSync(p, 'utf8');
    for (const m of modules) {
      const avant = `'./${m}'`;
      total += code.split(avant).length - 1;
      code = code.replaceAll(avant, `'./${m}.js'`);
    }
    writeFileSync(p, code);
  }
  if (total === 0) throw new Error('aucun import relatif réécrit : la compilation a changé de forme.');

  const D = await import(pathToFileURL(join(dossier, 'dossier.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  // Les sentinelles doivent être identiques : un motif qui divergerait ferait
  // dire à l'interface autre chose que ce que le paquet établit.
  comparerProfond('sentinelles', 'motif_numero_serie', v.motif_numero_serie, D.MOTIF_NUMERO_SERIE_ABSENT);
  comparerProfond('sentinelles', 'motif_declenchements', v.motif_declenchements, D.MOTIF_DECLENCHEMENTS_ABSENT);
  comparerProfond('sentinelles', 'motif_ecran', v.motif_ecran, D.MOTIF_ECRAN_NON_EVALUE);
  n += 3;

  for (const c of v.cas) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    let obtenu;
    try {
      obtenu = await D.constituerDossier(octets, c.nom_fichier);
    } catch (err) {
      ecarts.push({ sujet: c.nom, chemin: '(appel)', attendu: 'succès', obtenu: err.message });
      continue;
    }
    // Le document ENTIER : une clé oubliée d'un seul côté fait tomber.
    comparerProfond(c.nom, 'dossier', c.dossier, JSON.parse(JSON.stringify(obtenu)));
    n += 1;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} documents comparés.\n`);
    for (const e of ecarts.slice(0, 25)) {
      console.error(`  ${e.sujet} — ${e.chemin}`);
      console.error(`      attendu ${String(e.attendu).slice(0, 200)}`);
      console.error(`      obtenu  ${String(e.obtenu).slice(0, 200)}`);
    }
    if (ecarts.length > 25) console.error(`  … et ${ecarts.length - 25} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} documents comparés champ par champ, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
