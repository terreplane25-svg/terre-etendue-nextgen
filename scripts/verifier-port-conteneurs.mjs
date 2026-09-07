/**
 * verifier-port-conteneurs.mjs — Épingle le port des conteneurs hors EXIF.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or-conteneurs.json` : PNG, WebP, GIF, BMP,
 * SVG et profils ICC. Les octets extraits sont comparés par leur EMPREINTE.
 *
 * Le port est ASYNCHRONE là où le Python est synchrone : les chunks zTXt et
 * iCCP sont compressés en zlib, et le navigateur ne sait les décompresser que
 * par `DecompressionStream`. Les deux rendent la même chose ; ce sont les
 * résultats qui sont comparés, pas les signatures.
 *
 *     node scripts/verifier-port-conteneurs.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-conteneurs.json');

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
async function sha256(octets) {
  const c = await crypto.subtle.digest('SHA-256', octets.slice().buffer);
  return Array.from(new Uint8Array(c)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

const dossier = mkdtempSync(join(tmpdir(), 'conteneurs-'));
try {
  execFileSync('npx', ['--no-install', 'tsc', join(DIR, 'conteneurs.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });
  const C = await import(pathToFileURL(join(dossier, 'conteneurs.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  const profilAttendu = (p) => p;
  const profilObtenu = (p) => (p === null ? null : ({
    octets: p.octets, version: p.version,
    classe: p.classe, classe_libelle: p.classeLibelle,
    espace: p.espace, espace_libelle: p.espaceLibelle,
    espace_connexion: p.espaceConnexion,
    plateforme: p.plateforme, createur: p.createur,
    date: p.date, description: p.description, copyright: p.copyright,
  }));

  for (const c of v.icc) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    comparer(`icc ${c.nom}`, 'profil', profilAttendu(c.profil), profilObtenu(C.lireProfilIcc(octets)));
    n += 1;
  }

  for (const c of v.cas) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    const sujet = c.nom;
    const a = c.inventaire;
    let inv;
    try { inv = await C.inventorier(octets); } catch (err) {
      faux(sujet, 'inventaire', 'succès', err.message);
      continue;
    }
    comparer(sujet, 'format', a.format, inv.format);
    comparer(sujet, 'octets', a.octets, inv.octets);
    comparer(sujet, 'largeur', a.largeur, inv.largeur);
    comparer(sujet, 'hauteur', a.hauteur, inv.hauteur);
    comparer(sujet, 'profondeur', a.profondeur_bits, inv.profondeurBits);
    comparer(sujet, 'dpi X', a.dpi_x, inv.dpiX);
    comparer(sujet, 'dpi Y', a.dpi_y, inv.dpiY);
    n += 7;

    comparer(sujet, 'chunks', a.chunks,
      inv.chunks.map((x) => ({
        type: x.type, offset: x.offset, longueur: x.longueur,
        crc_valide: x.crcValide, role: x.role,
      })));
    comparer(sujet, 'textes', a.textes,
      inv.textes.map((t) => ({
        origine: t.origine, cle: t.cle, valeur: t.valeur,
        compresse: t.compresse, langue: t.langue,
      })));
    comparer(sujet, 'chunks corrompus', a.chunks_corrompus, inv.chunksCorrompus);
    comparer(sujet, 'propriétés', a.proprietes, inv.proprietes);
    comparer(sujet, 'profil ICC', a.profil_icc, profilObtenu(inv.profilIcc));
    n += 5;

    comparer(sujet, 'bloc EXIF (octets)', a.bloc_exif_octets,
      inv.blocExif === null ? null : inv.blocExif.length);
    comparer(sujet, 'bloc EXIF (empreinte)', a.bloc_exif_sha256,
      inv.blocExif === null ? null : await sha256(inv.blocExif));
    comparer(sujet, 'paquets XMP', a.paquets_xmp,
      await Promise.all(inv.paquetsXmp.map((x) => sha256(x))));
    n += 3;
  }

  for (const r of v.refus) {
    const octets = new Uint8Array(Buffer.from(r.octets_b64, 'base64'));
    let leve = false;
    try { await C.inventorier(octets); } catch { leve = true; }
    if (!leve) faux(`refus ${r.nom}`, 'inventaire', 'erreur levée', 'aucune erreur');
    n += 1;
  }

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
