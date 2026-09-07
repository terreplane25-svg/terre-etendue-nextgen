/**
 * verifier-port-makernotes.mjs — Épingle le port des notes propriétaires.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or-makernotes.json`. La comparaison est
 * CHAMP PAR CHAMP sur l'analyse entière, tags compris : c'est la base des
 * offsets qui est en jeu, et une base fausse ne lève aucune erreur — elle rend
 * simplement d'autres empreintes.
 *
 * Le port est ASYNCHRONE là où le Python est synchrone : les empreintes
 * passent par `crypto.subtle`. Les deux rendent la même chose ; ce sont les
 * résultats qui sont comparés, pas les signatures.
 *
 *     node scripts/verifier-port-makernotes.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-makernotes.json');

const ecarts = [];
function comparer(sujet, champ, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (JSON.stringify(a) !== JSON.stringify(o)) {
    ecarts.push({ sujet, champ, attendu: JSON.stringify(a), obtenu: JSON.stringify(o) });
  }
}

/** L'analyse TypeScript remise dans la forme du Python, sans rien omettre. */
function enFormePython(a) {
  return {
    present: a.present,
    octets: a.octets,
    constructeur: a.constructeur,
    signature_hex: a.signatureHex,
    empreinte: a.empreinte,
    base_retenue: a.baseRetenue,
    base_attendue: a.baseAttendue,
    base_conforme: a.baseConforme,
    boutisme: a.boutisme,
    nombre_de_tags: a.nombreDeTags,
    tags: a.tags.map((t) => ({
      identifiant: t.identifiant,
      type: t.type,
      type_nom: t.typeNom,
      cardinalite: t.cardinalite,
      octets: t.octets,
      en_ligne: t.enLigne,
      empreinte: t.empreinte,
      forme: t.forme,
      apercu_texte: t.apercuTexte,
      sens: t.sens === null ? null : [...t.sens],
    })),
    motif_structure_illisible: a.motifStructureIllisible,
    motif_aucun_sens: a.motifAucunSens,
    remarque_constructeur: a.remarqueConstructeur,
  };
}

const dossier = mkdtempSync(join(tmpdir(), 'makernotes-'));
try {
  // `noyau.ts` tire à sa suite le reste du paquet : on compile l'ensemble
  // plutôt que de deviner la clôture des dépendances.
  const modules = ['makernotes', 'noyau', 'conteneurs', 'isobmff', 'provenance',
    'quantification', 'telemetrie'];
  const sources = modules.map((f) => join(DIR, `${f}.ts`));
  execFileSync('npx', ['--no-install', 'tsc', ...sources,
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. On compte les
  // remplacements : un remplacement silencieusement nul laisserait un import
  // que Node refuserait plus loin sans dire pourquoi.
  let total = 0;
  for (const f of readdirSync(dossier).filter((x) => x.endsWith('.js'))) {
    const p = join(dossier, f);
    let code = readFileSync(p, 'utf8');
    for (const m of modules) {
      total += code.split(`'./${m}'`).length - 1;
      code = code.replaceAll(`'./${m}'`, `'./${m}.js'`);
    }
    writeFileSync(p, code);
  }
  if (total === 0) throw new Error('aucun import relatif réécrit : la compilation a changé de forme.');
  const M = await import(pathToFileURL(join(dossier, 'makernotes.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  for (const c of v.cas) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    // eslint-disable-next-line no-await-in-loop
    const obtenu = enFormePython(await M.analyserMakerNote(
      octets, c.offset_dans_le_tiff, c.boutisme_fichier));
    for (const champ of Object.keys(c.analyse)) {
      comparer(c.nom, champ, c.analyse[champ], obtenu[champ]);
      n += 1;
    }
    // Le port ne doit rien rendre de PLUS que le Python : un champ en trop est
    // une divergence de contrat, même s'il ne contredit aucune valeur.
    const enTrop = Object.keys(obtenu).filter((k) => !(k in c.analyse));
    if (enTrop.length > 0) comparer(c.nom, 'champs en trop', [], enTrop);
  }

  // Le registre des sens est vide des deux côtés, et c'est une promesse tenue
  // par le code, pas seulement par les vecteurs.
  comparer('registre', 'SENS_CONNUS vide', {}, M.SENS_CONNUS);
  comparer('registre', 'nombre de signatures', 19, M.SIGNATURES.length);
  n += 2;

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 15)) {
      console.error(`  ${e.sujet}\n    ${e.champ} :\n      attendu ${String(e.attendu).slice(0, 300)}\n      obtenu  ${String(e.obtenu).slice(0, 300)}`);
    }
    if (ecarts.length > 15) console.error(`  … et ${ecarts.length - 15} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
