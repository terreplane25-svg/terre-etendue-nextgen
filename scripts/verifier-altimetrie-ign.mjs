/**
 * verifier-altimetrie-ign.mjs — Éprouve la couche altimétrique SANS réseau.
 *
 * CE QUE CE CONTRÔLE ÉTABLIT, ET CE QU'IL N'ÉTABLIT PAS
 * ────────────────────────────────────────────────────
 * Il établit : que les points interrogés tombent sur la géodésique et non sur
 * une corde, que les requêtes sont mises en forme selon le contrat publié,
 * qu'une réponse conforme est correctement appariée aux distances, et surtout
 * qu'une réponse NON conforme ou lacunaire est refusée au lieu d'être comblée.
 *
 * Il n'établit PAS que le service de l'IGN répond ce qu'on croit. Cet
 * environnement n'a pas d'accès sortant vers data.geopf.fr : le service n'a
 * jamais été interrogé. C'est une limite réelle, elle est écrite ici, dans le
 * module, et affichée dans l'interface.
 *
 *     node scripts/verifier-altimetrie-ign.mjs
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'visee-optique');

let echecs = 0;
let controles = 0;
function verifier(nom, condition, detail = '') {
  controles += 1;
  if (!condition) {
    echecs += 1;
    console.error(`  ✗ ${nom}${detail ? `\n      ${detail}` : ''}`);
  }
}
async function leve(nom, appel, motif = '') {
  controles += 1;
  try {
    await appel();
    echecs += 1;
    console.error(`  ✗ ${nom} : aucune erreur levée`);
  } catch (err) {
    if (motif && !String(err.message).includes(motif)) {
      echecs += 1;
      console.error(`  ✗ ${nom} : le message ne mentionne pas « ${motif} »\n      ${err.message}`);
    }
  }
}

const dossier = mkdtempSync(join(tmpdir(), 'alti-'));
try {
  execFileSync('npx', ['--no-install', 'tsc',
    join(DIR, 'altimetrie-ign.ts'), join(DIR, 'relief.ts'), join(DIR, 'noyau.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });
  for (const f of ['altimetrie-ign.js', 'relief.js']) {
    const p = join(dossier, f);
    writeFileSync(p, readFileSync(p, 'utf8')
      .replaceAll("'./noyau'", "'./noyau.js'").replaceAll("'./relief'", "'./relief.js'"));
  }
  const A = await import(pathToFileURL(join(dossier, 'altimetrie-ign.js')).href);
  const N = await import(pathToFileURL(join(dossier, 'noyau.js')).href);

  // Le cas d'étude de Sangatte : digue de Sangatte → phare de South Foreland.
  const [latA, lonA, latB, lonB] = [50.94642, 1.75305, 51.13152, 1.338825];

  // 1. Les points tombent sur la géodésique, pas sur la corde.
  const ech = A.pointsSurLaGeodesique(latA, lonA, latB, lonB, 500);
  verifier('distance conforme à Vincenty',
    Math.abs(ech.distanceM - N.vincentyInverse(latA, lonA, latB, lonB).distanceM) < 1e-9);
  verifier('pas réel au plus égal au pas demandé (§33 : 500 m au plus)', ech.pasReelM <= 500 + 1e-9,
    `pas réel = ${ech.pasReelM.toFixed(2)} m`);
  verifier('extrémités rendues telles que saisies',
    ech.points[0].latitudeDeg === latA && ech.points.at(-1).longitudeDeg === lonB);
  verifier('distances strictement croissantes',
    ech.points.every((p, i) => i === 0 || p.distanceM > ech.points[i - 1].distanceM));

  // Un point du milieu doit s'écarter de l'interpolation linéaire : c'est
  // exactement ce que l'emploi de Vincenty direct achète. S'il n'y avait pas
  // d'écart, le contrôle ne prouverait pas qu'on ne fait pas l'interpolation.
  const milieu = ech.points[Math.floor(ech.points.length / 2)];
  const t = milieu.distanceM / ech.distanceM;
  const lineaire = { lat: latA + (latB - latA) * t, lon: lonA + (lonB - lonA) * t };
  const ecartM = N.vincentyInverse(milieu.latitudeDeg, milieu.longitudeDeg, lineaire.lat, lineaire.lon).distanceM;
  verifier('la géodésique s’écarte bien de l’interpolation linéaire', ecartM > 0.5,
    `écart au milieu = ${ecartM.toFixed(2)} m — s’il était nul, ce contrôle ne prouverait rien`);

  // 2. La requête suit le contrat publié.
  const url = A.urlRequete(ech.points.slice(0, 3));
  const u = new URL(url);
  verifier('URL : bon service', url.startsWith(A.RACINE_IGN));
  verifier('URL : ressource déclarée', u.searchParams.get('resource') === A.RESSOURCE_IGN);
  verifier('URL : autant de longitudes que de latitudes',
    u.searchParams.get('lon').split('|').length === u.searchParams.get('lat').split('|').length);
  verifier('URL : trois points demandés', u.searchParams.get('lon').split('|').length === 3);
  verifier('URL : sous la limite de longueur des navigateurs',
    A.urlRequete(ech.points.slice(0, A.POINTS_PAR_REQUETE)).length < 8000,
    `longueur = ${A.urlRequete(ech.points.slice(0, A.POINTS_PAR_REQUETE)).length}`);

  // 3. Une réponse conforme est appariée aux bonnes distances.
  const faux = (zs) => ({
    ok: true, status: 200,
    json: async () => ({ elevations: zs.map((z) => ({ z, lon: 0, lat: 0, acc: '2.5' })) }),
  });
  let demandes = 0;
  const recuperer = async (u2) => {
    demandes += 1;
    const n = new URL(u2).searchParams.get('lon').split('|').length;
    // Un relief en cloche, pour que l'appariement distance/altitude soit
    // discriminant : avec un profil constant, un décalage ne se verrait pas.
    return faux(Array.from({ length: n }, (_, i) => 10 + i));
  };
  const r = await A.profilDepuisIgn(latA, lonA, latB, lonB, { pasM: 500, recuperer });
  verifier('profil : autant de points que d’échantillons', r.profil.points.length === ech.points.length);
  verifier('profil : altitudes appariées dans l’ordre',
    r.profil.points[0].altitudeM === 10 && r.profil.points[1].altitudeM === 11);
  verifier('profil : source nommant l’IGN et la ressource',
    r.profil.source.includes('IGN') && r.profil.source.includes(A.RESSOURCE_IGN));
  verifier('profil : pas déclaré', Math.abs(r.profil.pasM - ech.pasReelM) < 1e-9);
  verifier('profil : aucune lacune sur une réponse complète', r.lacunesM.length === 0);
  verifier('profil : la réserve est jointe', r.reserve === A.RESERVE_IGN);
  verifier('lots enchaînés', demandes === Math.ceil(ech.points.length / A.POINTS_PAR_REQUETE),
    `${demandes} requête(s) pour ${ech.points.length} points`);

  // 4. LE POINT CRITIQUE : une lacune n'est pas une altitude nulle.
  const avecLacunes = async (u2) => {
    const n = new URL(u2).searchParams.get('lon').split('|').length;
    return faux(Array.from({ length: n }, (_, i) => (i % 5 === 2 ? A.SENTINEL_SANS_DONNEE : 100 + i)));
  };
  const rl = await A.profilDepuisIgn(latA, lonA, latB, lonB, { pasM: 2000, recuperer: avecLacunes });
  verifier('lacunes : signalées', rl.lacunesM.length > 0);
  verifier('lacunes : jamais comblées par zéro',
    rl.profil.points.every((p) => p.altitudeM > 0),
    'un -99999 traité comme altitude creuserait un gouffre et déclarerait tout visible');
  verifier('lacunes : points manquants absents du profil',
    rl.profil.points.length + rl.lacunesM.length === Math.ceil(ech.distanceM / 2000) + 1);

  // 5. Les refus. Une réponse qu'on ne comprend pas ne produit jamais de profil.
  await leve('réponse sans « elevations »',
    () => A.profilDepuisIgn(latA, lonA, latB, lonB, {
      recuperer: async () => ({ ok: true, status: 200, json: async () => ({ autre: [] }) }),
    }), 'elevations');
  await leve('réponse de mauvaise longueur',
    () => A.profilDepuisIgn(latA, lonA, latB, lonB, {
      recuperer: async () => faux([1, 2, 3]),
    }), 'incohérente');
  await leve('service en erreur',
    () => A.profilDepuisIgn(latA, lonA, latB, lonB, {
      recuperer: async () => ({ ok: false, status: 503, json: async () => ({}) }),
    }), '503');
  await leve('service injoignable',
    () => A.profilDepuisIgn(latA, lonA, latB, lonB, {
      recuperer: async () => { throw new Error('réseau coupé'); },
    }), 'saisi à la main');
  await leve('aucune donnée exploitable (hors couverture)',
    () => A.profilDepuisIgn(latA, lonA, latB, lonB, {
      recuperer: async (u2) => {
        const n = new URL(u2).searchParams.get('lon').split('|').length;
        return faux(Array.from({ length: n }, () => A.SENTINEL_SANS_DONNEE));
      },
    }), 'France');
  await leve('points confondus', () => A.pointsSurLaGeodesique(latA, lonA, latA, lonA), 'confondus');
  await leve('pas nul', () => A.pointsSurLaGeodesique(latA, lonA, latB, lonB, 0), 'strictement positif');

  // 6. La saisie manuelle : la voie sans réseau.
  const manuel = A.profilDepuisTexte('0 12\n500, 40\n1000;95\n1500\t3', 'relevé terrain, carnet n°4');
  verifier('saisie manuelle : quatre points', manuel.points.length === 4);
  verifier('saisie manuelle : séparateurs mêlés admis',
    manuel.points[1].altitudeM === 40 && manuel.points[2].altitudeM === 95 && manuel.points[3].altitudeM === 3);
  verifier('saisie manuelle : source conservée', manuel.source === 'relevé terrain, carnet n°4');
  const avecCommentaires = A.profilDepuisTexte('# mon relevé\n0 12\n\n500 40\n', 'essai');
  verifier('saisie manuelle : commentaires et lignes vides ignorés', avecCommentaires.points.length === 2);
  const virgule = A.profilDepuisTexte('0 12,5\n500 40,25', 'essai');
  verifier('saisie manuelle : virgule décimale admise', virgule.points[0].altitudeM === 12.5);
  await leve('saisie manuelle : sans source', () => A.profilDepuisTexte('0 1\n1 2', '  '), 'source');
  await leve('saisie manuelle : une seule ligne', () => A.profilDepuisTexte('0 1', 'essai'), 'deux');
  await leve('saisie manuelle : distances non croissantes',
    () => A.profilDepuisTexte('0 1\n500 2\n200 3', 'essai'), 'croissants');
  await leve('saisie manuelle : texte illisible',
    () => A.profilDepuisTexte('bonjour\nau revoir', 'essai'), 'deux nombres');
  const virguleSeule = A.profilDepuisTexte('0,12\n500,40', 'essai');
  verifier('saisie manuelle : virgule SEULE lue comme séparateur de colonnes',
    virguleSeule.points.length === 2 && virguleSeule.points[1].altitudeM === 40,
    'sans autre séparateur sur la ligne, la virgule ne peut être que la colonne');

  if (echecs === 0) {
    console.log(`✓ Couche altimétrique : ${controles} contrôles, aucun écart.`);
    console.log('  Réserve : le service de l’IGN n’a jamais été interrogé depuis cet');
    console.log('  environnement (pas d’accès sortant). Seul le contrat est éprouvé.');
  } else {
    console.error(`\n✗ ${echecs} écart(s) sur ${controles} contrôles.`);
    process.exitCode = 1;
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
