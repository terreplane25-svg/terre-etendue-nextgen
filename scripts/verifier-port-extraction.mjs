/**
 * verifier-port-extraction.mjs — Épingle les ports de quantification et de télémétrie.
 *
 * Rejoue en TypeScript les vecteurs de
 * `src/lib/preuve-image/vecteurs-or-extraction.json` : les tables IJG
 * reconstruites, l'estimation de qualité AVEC son écart, l'analyse complète de
 * douze JPEG, les refus, et la télémétrie de six paquets XMP.
 *
 *     node scripts/verifier-port-extraction.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-extraction.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = join(RACINE, 'src', 'lib', 'preuve-image');
const VECTEURS = join(DIR, 'vecteurs-or-extraction.json');

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

const dossier = mkdtempSync(join(tmpdir(), 'extraction-'));
try {
  execFileSync('npx', ['--no-install', 'tsc',
    join(DIR, 'quantification.ts'), join(DIR, 'telemetrie.ts'),
    '--target', 'ES2022', '--module', 'ES2022', '--moduleResolution', 'bundler',
    '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'], { cwd: RACINE, stdio: 'pipe' });

  const Q = await import(pathToFileURL(join(dossier, 'quantification.js')).href);
  const T = await import(pathToFileURL(join(dossier, 'telemetrie.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  // Les sentinelles doivent être identiques des deux côtés : un motif qui
  // divergerait ferait dire à l'interface autre chose que ce que le paquet
  // établit.
  comparer('sentinelles', 'motif aucune signature', v.motif_aucune_signature, Q.MOTIF_AUCUNE_SIGNATURE);
  comparer('sentinelles', 'motif station sol', v.motif_station_sol, T.MOTIF_STATION_SOL_ABSENTE);
  comparer('sentinelles', 'avertissement altitude', v.avertissement_altitude, T.AVERTISSEMENT_ALTITUDE_RELATIVE);
  comparer('sentinelles', 'registre vide', {}, Q.SIGNATURES_CONNUES);
  comparer('sentinelles', 'table annexe K', v.table_annexe_k, [...Q.TABLE_LUMINANCE_ANNEXE_K]);
  n += 5;

  // La reconstruction IJG. La division entière de Python (`//`) doit être
  // reproduite par Math.floor : un `/` nu donnerait des flottants et une table
  // différente à toutes les qualités où le quotient n'est pas entier.
  for (const t of v.tables_ijg) {
    comparer(`table IJG q=${t.qualite}`, 'coefficients', t.table, Q.tableIjg(t.qualite));
    n += 1;
  }

  // L'estimation, avec son écart — c'est le couple qui compte.
  for (const e of v.qualites_estimees) {
    const [q, ecart] = Q.qualiteIjgEstimee(e.valeurs);
    comparer(`estimation décalage=${e.decalage}`, 'qualité', e.qualite, q);
    comparer(`estimation décalage=${e.decalage}`, 'écart', e.ecart, ecart);
    n += 2;
  }

  for (const c of v.jpeg) {
    const octets = new Uint8Array(Buffer.from(c.octets_b64, 'base64'));
    const sujet = `jpeg ${c.nom}`;
    let a;
    try { a = await Q.analyserQuantification(octets); } catch (err) {
      faux(sujet, 'analyse', 'succès', err.message);
      continue;
    }
    comparer(sujet, 'empreinte de l’ensemble', c.empreinte_ensemble, a.empreinteEnsemble);
    comparer(sujet, 'qualité IJG', c.qualite_ijg, a.qualiteIjg);
    comparer(sujet, 'écart à IJG', c.ecart_a_ijg, a.ecartAIjg);
    comparer(sujet, 'conforme IJG', c.conforme_ijg, a.conformeIjg);
    comparer(sujet, 'sous-échantillonnage', c.sous_echantillonnage, a.sousEchantillonnage);
    comparer(sujet, 'progressif', c.progressif, a.progressif);
    comparer(sujet, 'largeur', c.largeur, a.largeur);
    comparer(sujet, 'hauteur', c.hauteur, a.hauteur);
    comparer(sujet, 'composantes', c.composantes, a.composantes);
    comparer(sujet, 'signature', c.signature, a.signature);
    comparer(sujet, 'marqueurs', c.marqueurs, a.marqueurs);
    n += 11;

    comparer(sujet, 'tables',
      c.tables.map((t) => ({
        identifiant: t.identifiant, precision_bits: t.precision_bits,
        valeurs: t.valeurs, offset: t.offset,
      })),
      a.tables.map((t) => ({
        identifiant: t.identifiant, precision_bits: t.precisionBits,
        valeurs: t.valeurs, offset: t.offset,
      })));
    n += 1;

    // Les empreintes de table, calculées séparément : elles doivent tomber sur
    // les mêmes valeurs que côté Python, ce qui atteste que l'ordre zigzag est
    // respecté des deux côtés.
    for (let i = 0; i < c.tables.length && i < a.tables.length; i++) {
      comparer(`${sujet} table ${i}`, 'empreinte',
        c.tables[i].empreinte, await Q.empreinteTable(a.tables[i]));
      n += 1;
    }
  }

  for (const r of v.refus_jpeg) {
    const octets = new Uint8Array(Buffer.from(r.octets_b64, 'base64'));
    let leve = false;
    try { await Q.analyserQuantification(octets); } catch { leve = true; }
    if (!leve) faux(`refus ${r.nom}`, 'analyse', 'erreur levée', 'aucune erreur');
    n += 1;
  }

  for (const c of v.xmp) {
    const paquet = new Uint8Array(Buffer.from(c.paquet_b64, 'base64'));
    const sujet = `xmp ${c.nom}`;
    const t = T.extraireTelemetrie(paquet);
    comparer(sujet, 'présent', c.present, t.present);
    comparer(sujet, 'origine', c.origine, t.origine);
    comparer(sujet, 'préfixes', c.prefixes, t.prefixes);
    comparer(sujet, 'latitude', c.latitude_deg, t.latitudeDeg);
    comparer(sujet, 'longitude', c.longitude_deg, t.longitudeDeg);
    comparer(sujet, 'altitude absolue', c.altitude_absolue_m, t.altitudeAbsolueM);
    comparer(sujet, 'altitude relative', c.altitude_relative_m, t.altitudeRelativeM);
    comparer(sujet, 'altitude sol', c.altitude_sol_m, t.altitudeSolM);
    comparer(sujet, 'tangage nacelle', c.tangage_nacelle_deg, t.tangageNacelleDeg);
    comparer(sujet, 'lacet nacelle', c.lacet_nacelle_deg, t.lacetNacelleDeg);
    comparer(sujet, 'roulis nacelle', c.roulis_nacelle_deg, t.roulisNacelleDeg);
    comparer(sujet, 'visée horizontale', c.visee_horizontale, T.viseeHorizontale(t));
    comparer(sujet, 'station sol', c.station_sol, t.stationSol);
    comparer(sujet, 'sens', c.sens, t.sens);
    comparer(sujet, 'champs',
      c.champs,
      t.champs.map((x) => ({
        prefixe: x.prefixe, nom: x.nom, brut: x.brut, valeur: x.valeur, cle: x.cle,
      })));
    n += 15;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 20)) {
      console.error(`  ${e.sujet}\n    ${e.champ} :\n      attendu ${String(e.attendu).slice(0, 260)}\n      obtenu  ${String(e.obtenu).slice(0, 260)}`);
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
