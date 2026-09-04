/**
 * verifier-port-preuve.mjs — Épingle le port TypeScript de l'outil B au Python.
 *
 * Le vérificateur d'intégrité du site tourne dans le navigateur : le fichier
 * de l'utilisateur ne quitte jamais sa machine. La référence testée reste le
 * paquet Python `preuve_image` et ses 137 tests.
 *
 * Ce script rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or.json` — empreintes SHA-256, lectures EXIF
 * sur des JPEG construits par la suite de tests du paquet, refus attendus, et
 * classement des opérations du §17.2 — puis compare.
 *
 *     node scripts/verifier-port-preuve.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-preuve.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC = join(RACINE, 'src', 'lib', 'preuve-image', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'preuve-image', 'vecteurs-or.json');

const ecarts = [];
function faux(sujet, champ, attendu, obtenu) {
  ecarts.push({ sujet, champ, attendu, obtenu });
}

/** Les noms de champs diffèrent entre les deux langages : snake_case ↔ camelCase. */
const CORRESPONDANCE = {
  fabricant: 'fabricant',
  modele: 'modele',
  objectif: 'objectif',
  focale_mm: 'focaleMm',
  focale_equivalente_35mm: 'focaleEquivalente35mm',
  ouverture: 'ouverture',
  temps_pose_s: 'tempsPoseS',
  sensibilite_iso: 'sensibiliteIso',
  largeur_px: 'largeurPx',
  hauteur_px: 'hauteurPx',
  date_heure_original: 'dateHeureOriginal',
  orientation: 'orientation',
};
const CORRESPONDANCE_GPS = {
  latitude_deg: 'latitudeDeg',
  longitude_deg: 'longitudeDeg',
  altitude_m: 'altitudeM',
  incertitude_m: 'incertitudeM',
  source: 'source',
};

function comparerNombre(sujet, champ, attendu, obtenu) {
  if (attendu === null || attendu === undefined) {
    if (obtenu !== null && obtenu !== undefined) faux(sujet, champ, 'null', obtenu);
    return;
  }
  if (typeof attendu === 'string') {
    if (attendu !== obtenu) faux(sujet, champ, attendu, obtenu);
    return;
  }
  const abs = Math.abs(attendu - obtenu);
  if (!(abs <= 1e-12 || abs / Math.abs(attendu || 1) <= 1e-12)) {
    faux(sujet, champ, attendu, obtenu);
  }
}

const dossier = mkdtempSync(join(tmpdir(), 'preuve-port-'));
try {
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  const M = await import(pathToFileURL(join(dossier, 'noyau.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  // Le sentinel doit être identique dans les deux langages, sinon un champ
  // déclaré indisponible d'un côté ne l'est pas de l'autre.
  if (v.sentinel_indisponible !== M.INDISPONIBLE) {
    faux('sentinel', 'INDISPONIBLE', v.sentinel_indisponible, M.INDISPONIBLE);
  }
  n += 1;

  for (const c of v.sha256) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    if (octets.length !== c.taille) faux(`sha256 ${c.nom}`, 'taille', c.taille, octets.length);
    const e = await M.empreinteSha256(octets);
    if (e !== c.empreinte) faux(`sha256 ${c.nom}`, 'empreinte', c.empreinte, e);
    if (!M.empreinteValide(e)) faux(`sha256 ${c.nom}`, 'empreinteValide', true, false);
    n += 3;
  }

  for (const c of v.exif) {
    const octets = new Uint8Array(Buffer.from(c.jpeg_b64, 'base64'));
    const sujet = `exif ${c.nom}`;
    const e = await M.empreinteSha256(octets);
    if (e !== c.empreinte) faux(sujet, 'empreinte du JPEG', c.empreinte, e);
    n += 1;

    let d;
    try {
      d = M.lireExifDepuisJpeg(octets);
    } catch (err) {
      faux(sujet, 'lecture', 'succès', err.message);
      continue;
    }
    for (const [cle, cleTs] of Object.entries(CORRESPONDANCE)) {
      comparerNombre(sujet, cle, c.attendu[cle], d[cleTs]);
      n += 1;
    }
    if (c.attendu.gps === null) {
      if (d.gps !== null) faux(sujet, 'gps', 'null', JSON.stringify(d.gps));
      n += 1;
    } else {
      if (d.gps === null) {
        faux(sujet, 'gps', 'objet', 'null');
      } else {
        for (const [cle, cleTs] of Object.entries(CORRESPONDANCE_GPS)) {
          comparerNombre(`${sujet} gps`, cle, c.attendu.gps[cle], d.gps[cleTs]);
          n += 1;
        }
      }
    }

    // Le rapport d'ensemble doit retrouver l'empreinte et l'EXIF sans se
    // contredire lui-même.
    const rap = await M.analyserFichier(`${c.nom}.jpg`, 'image/jpeg', octets);
    if (rap.empreinte !== c.empreinte) faux(sujet, 'analyserFichier.empreinte', c.empreinte, rap.empreinte);
    if (rap.motifExifAbsent !== null) faux(sujet, 'analyserFichier.motifExifAbsent', 'null', rap.motifExifAbsent);
    if (rap.tailleOctets !== octets.length) faux(sujet, 'analyserFichier.taille', octets.length, rap.tailleOctets);
    n += 3;
  }

  // Les refus : le port doit refuser là où le Python refuse. On ne compare pas
  // les messages — ils n'ont pas à être identiques mot pour mot — mais le fait
  // de lever, et que le rapport d'ensemble le signale au lieu de le taire.
  for (const r of v.refus) {
    const octets = new Uint8Array(Buffer.from(r.jpeg_b64, 'base64'));
    let leve = false;
    try { M.lireExifDepuisJpeg(octets); } catch { leve = true; }
    if (!leve) faux(`refus ${r.nom}`, 'lecture', 'erreur levée', 'aucune erreur');
    const rap = await M.analyserFichier(`${r.nom}.bin`, '', octets);
    if (rap.exif !== null) faux(`refus ${r.nom}`, 'analyserFichier.exif', 'null', 'objet');
    if (!rap.motifExifAbsent) faux(`refus ${r.nom}`, 'analyserFichier.motifExifAbsent', 'un motif', rap.motifExifAbsent);
    if (rap.typeDeclare !== M.INDISPONIBLE) {
      faux(`refus ${r.nom}`, 'typeDeclare vide', M.INDISPONIBLE, rap.typeDeclare);
    }
    if (!M.empreinteValide(rap.empreinte)) {
      faux(`refus ${r.nom}`, 'empreinte malgré EXIF illisible', 'valide', rap.empreinte);
    }
    n += 5;
  }

  for (const o of v.operations) {
    let obtenu;
    try { obtenu = M.classerOperation(o.nom); } catch { obtenu = 'levée'; }
    if (obtenu !== o.admise) faux(`opération ${o.nom}`, 'classement', o.admise, obtenu);
    n += 1;
  }
  for (const nom of v.operations_inconnues) {
    let leve = false;
    try { M.classerOperation(nom); } catch { leve = true; }
    if (!leve) faux(`opération inconnue « ${nom} »`, 'classement', 'erreur levée', 'aucune erreur');
    n += 1;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 30)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu}`);
    }
    if (ecarts.length > 30) console.error(`  … et ${ecarts.length - 30} autre(s).`);
    console.error('\n  Corriger le Python d\'abord, puis répercuter ici, puis régénérer les vecteurs.\n');
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
