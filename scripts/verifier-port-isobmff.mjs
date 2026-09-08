/**
 * verifier-port-isobmff.mjs — Épingle le port TypeScript des conteneurs à boîtes.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or-isobmff.json` : structure de boîtes, items,
 * emplacements, aperçus, et ce que `lireExif` en tire. Les octets extraits sont
 * comparés par leur EMPREINTE — c'est ce qui atteste que les deux
 * implémentations ont pris exactement les mêmes, au bit près.
 *
 *     node scripts/verifier-port-isobmff.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-isobmff.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-isobmff.json');

const ecarts = [];
function faux(sujet, champ, attendu, obtenu) {
  ecarts.push({ sujet, champ, attendu, obtenu });
}
function comparer(sujet, champ, attendu, obtenu) {
  const a = attendu === undefined ? null : attendu;
  const o = obtenu === undefined ? null : obtenu;
  if (JSON.stringify(a) !== JSON.stringify(o)) faux(sujet, champ, JSON.stringify(a), JSON.stringify(o));
}

async function sha256(octets) {
  const c = await crypto.subtle.digest('SHA-256', octets.slice().buffer);
  return Array.from(new Uint8Array(c)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

const dossier = mkdtempSync(join(tmpdir(), 'isobmff-'));
try {
  execFileSync('npx', ['--no-install', 'tsc',
    join(DIR, 'isobmff.ts'), join(DIR, 'noyau.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });
  // tsc ne réécrit pas les extensions ; l'ESM de Node les exige. On compte les
  // occurrences : sans cette réécriture, Node refuse le module sans dire lequel.
  const fn = join(dossier, 'noyau.js');
  const code = readFileSync(fn, 'utf8');
  if (!code.includes("'./isobmff'")) {
    throw new Error("noyau.js n'importe pas './isobmff' : la compilation a changé de forme.");
  }
  writeFileSync(fn, code.replaceAll("'./isobmff'", "'./isobmff.js'"));

  const I = await import(pathToFileURL(join(dossier, 'isobmff.js')).href);
  const N = await import(pathToFileURL(fn).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  for (const c of v.cas) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    const sujet = c.nom;
    const attendu = c.structure;

    comparer(sujet, 'conteneur détecté', c.conteneur_detecte, N.detecterConteneur(octets));
    comparer(sujet, 'empreinte du fichier', c.empreinte, await sha256(octets));
    n += 2;

    const s = I.analyserIsobmff(octets);
    comparer(sujet, 'marque', attendu.marque, s.marque);
    comparer(sujet, 'marques compatibles', attendu.marques_compatibles, s.marquesCompatibles);
    comparer(sujet, 'est HEIF', attendu.est_heif, I.estHeif(s));
    comparer(sujet, 'est AVIF', attendu.est_avif, I.estAvif(s));
    comparer(sujet, 'est CR3', attendu.est_cr3, I.estCr3(s));
    comparer(sujet, 'item principal', attendu.item_principal, s.itemPrincipal);
    comparer(sujet, 'version du codec', attendu.version_codec, s.versionCodec);
    // Les dimensions de l'item principal, lues dans `ispe` via `ipma`. C'est
    // la seule MESURE qu'un HEIF porte hors de l'EXIF : une divergence ici
    // rendrait la confrontation mesure/déclaration fausse côté navigateur.
    comparer(sujet, 'largeur (ispe)', attendu.largeur, s.largeur);
    comparer(sujet, 'hauteur (ispe)', attendu.hauteur, s.hauteur);
    n += 9;

    // Les boîtes : type, position ET profondeur. La profondeur est ce qui
    // trahit un `meta` mal traité — les enfants remontent d'un niveau ou
    // disparaissent.
    comparer(sujet, 'boîtes',
      attendu.boites,
      s.boites.map((b) => ({
        type: b.type, debut: b.debut, taille: b.taille,
        debut_charge: b.debutCharge, profondeur: b.profondeur,
      })));
    n += 1;

    comparer(sujet, 'items',
      attendu.items,
      s.items.map((i) => ({
        identifiant: i.identifiant, type: i.type, nom: i.nom,
        offset: i.offset, longueur: i.longueur,
        type_auxiliaire: i.typeAuxiliaire, reference_vers: i.referenceVers,
        largeur: i.largeur, hauteur: i.hauteur,
      })));
    comparer(sujet, 'auxiliaires', attendu.auxiliaires, s.auxiliaires.map((i) => i.identifiant));
    n += 2;

    comparer(sujet, 'bloc EXIF (octets)', attendu.bloc_exif_octets,
      s.blocExif === null ? null : s.blocExif.length);
    comparer(sujet, 'bloc EXIF (empreinte)', attendu.bloc_exif_sha256,
      s.blocExif === null ? null : await sha256(s.blocExif));
    comparer(sujet, 'MakerNotes (empreinte)', attendu.makernotes_sha256,
      s.makernotes === null ? null : await sha256(s.makernotes));
    n += 3;

    comparer(sujet, 'paquets XMP', attendu.paquets_xmp,
      await Promise.all(s.paquetsXmp.map((x) => sha256(x))));
    n += 1;

    comparer(sujet, 'aperçus', attendu.apercus,
      await Promise.all(s.apercus.map(async (a) => ({
        origine: a.origine, octets: a.octets.length, sha256: await sha256(a.octets),
      }))));
    n += 1;

    // Le chemin réel : `lireExif` sur des octets, sans rien savoir du format.
    // Épingler la structure sans épingler la lecture laisserait passer une
    // erreur de câblage entre les deux.
    if (c.exif.lu) {
      let e;
      try { e = N.lireExif(octets); } catch (err) { faux(sujet, 'lireExif', 'succès', err.message); continue; }
      comparer(sujet, 'exif.conteneur', c.exif.conteneur, e.conteneur);
      comparer(sujet, 'exif.fabricant', c.exif.fabricant, e.fabricant);
      comparer(sujet, 'exif.modele', c.exif.modele, e.modele);
      comparer(sujet, 'exif.iso', c.exif.sensibilite_iso, e.sensibiliteIso);
      comparer(sujet, 'exif.largeur', c.exif.largeur_px, e.largeurPx);
      comparer(sujet, 'exif.previsualisations', c.exif.previsualisations,
        await Promise.all(e.previsualisations.map(async (m) => ({
          origine: m.origine, longueur: m.longueur, sha256: await sha256(m.octets),
        }))));
      n += 6;
    } else {
      let message = null;
      try { N.lireExif(octets); } catch (err) { message = err.message; }
      if (message === null) faux(sujet, 'lireExif', 'erreur levée', 'aucune erreur');
      n += 1;
    }
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 20)) {
      console.error(`  ${e.sujet}\n    ${e.champ} :\n      attendu ${String(e.attendu).slice(0, 300)}\n      obtenu  ${String(e.obtenu).slice(0, 300)}`);
    }
    if (ecarts.length > 20) console.error(`  … et ${ecarts.length - 20} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
