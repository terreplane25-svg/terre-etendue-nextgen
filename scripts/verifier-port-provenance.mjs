/**
 * verifier-port-provenance.mjs — Épingle le module d'ingestion au paquet Python.
 *
 * L'ingestion tourne dans le navigateur — le fichier de l'opérateur ne doit pas
 * en sortir — donc en TypeScript, alors que la référence testée est le paquet
 * Python `preuve_image`. Ce script rejoue en TypeScript les lectures que le
 * Python a produites dans `src/lib/preuve-image/vecteurs-or-provenance.json`,
 * SUR LES MÊMES OCTETS, et compare.
 *
 *     node scripts/verifier-port-provenance.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-provenance.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC_PROV = join(RACINE, 'src', 'lib', 'preuve-image', 'provenance.ts');
const SRC_NOYAU = join(RACINE, 'src', 'lib', 'preuve-image', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'preuve-image', 'vecteurs-or-provenance.json');

const TOL_REL = 1e-12;
const TOL_ABS = 1e-9;

function compiler() {
  const dossier = mkdtempSync(join(tmpdir(), 'provenance-port-'));
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC_PROV, SRC_NOYAU, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict', '--lib', 'ES2022,DOM'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  return dossier;
}

const ecarts = [];
let n = 0;

function comparer(sujet, champ, attendu, obtenu, tolAbs = TOL_ABS) {
  n += 1;
  if (attendu === null || attendu === undefined) {
    if (obtenu !== null && obtenu !== undefined) {
      ecarts.push({ sujet, champ, attendu: 'null', obtenu: String(obtenu) });
    }
    return;
  }
  if (typeof attendu === 'number' && typeof obtenu === 'number') {
    const abs = Math.abs(attendu - obtenu);
    const rel = Math.abs(attendu) > 0 ? abs / Math.abs(attendu) : abs;
    if (abs > tolAbs && rel > TOL_REL) {
      ecarts.push({ sujet, champ, attendu, obtenu, ecart: abs.toExponential(3) });
    }
    return;
  }
  if (typeof attendu === 'object') {
    const a = JSON.stringify(attendu);
    const b = JSON.stringify(obtenu);
    if (a !== b) ecarts.push({ sujet, champ, attendu: a.slice(0, 160), obtenu: String(b).slice(0, 160) });
    return;
  }
  if (attendu !== obtenu) {
    ecarts.push({ sujet, champ, attendu: String(attendu).slice(0, 160), obtenu: String(obtenu).slice(0, 160) });
  }
}

const octets = (hex) => Uint8Array.from(Buffer.from(hex, 'hex'));

/**
 * Le Python encode les chaînes d'octets en `{_octets_hex: "..."}` pour qu'elles
 * ne se confondent pas avec des tableaux d'entiers. Le TypeScript rend des
 * `Uint8Array` : on les ramène à la même forme avant de comparer, sans quoi la
 * comparaison porterait sur la représentation et non sur la valeur.
 */
function normaliser(v) {
  if (v instanceof Uint8Array) return { _octets_hex: Buffer.from(v).toString('hex') };
  if (Array.isArray(v)) return v.map(normaliser);
  if (v && typeof v === 'object') {
    const out = {};
    for (const [k, x] of Object.entries(v)) out[k] = normaliser(x);
    return out;
  }
  return v;
}

const dossier = compiler();
try {
  // Les deux sources vivent dans le même dossier : tsc en fait la racine, et les
  // fichiers émis sont à plat, sans le niveau `preuve-image/`.
  const P = await import(pathToFileURL(join(dossier, 'provenance.js')).href);
  const N = await import(pathToFileURL(join(dossier, 'noyau.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));

  // --- CBOR : les vecteurs de la RFC 8949 ---
  for (const c of v.cbor) {
    comparer(`CBOR ${c.hex}`, 'valeur', c.valeur, normaliser(P.decoderCbor(octets(c.hex))));
  }

  // --- JUMBF ---
  for (const cas of v.jumbf) {
    const boites = P.analyserBoitesJumbf(octets(cas.hex));
    comparer(cas.nom, 'nombre de boîtes', cas.boites.length, boites.length);
    cas.boites.forEach((attendue, i) => {
      const b = boites[i];
      if (!b) return;
      comparer(cas.nom, `[${i}] type`, attendue.type, b.type);
      comparer(cas.nom, `[${i}] taille`, attendue.taille, b.taille);
      comparer(cas.nom, `[${i}] offset`, attendue.offset, b.offset);
      comparer(cas.nom, `[${i}] label`, attendue.label, b.label);
      comparer(cas.nom, `[${i}] uuid_type`, attendue.uuid_type, b.uuidType);
      comparer(cas.nom, `[${i}] charge`, attendue.charge_hex, Buffer.from(b.charge).toString('hex'));
      comparer(cas.nom, `[${i}] filles`, attendue.nb_filles, b.filles.length);
    });
  }

  // --- C2PA ---
  for (const cas of v.c2pa) {
    const r = P.extraireC2pa(octets(cas.hex));
    const a = cas.resultat;
    comparer(cas.nom, 'present', a.present, r.present);
    comparer(cas.nom, 'conteneur', a.conteneur, r.conteneur);
    comparer(cas.nom, 'octets', a.octets, r.octets);
    comparer(cas.nom, 'signature_verifiee', a.signature_verifiee, r.signatureVerifiee);
    comparer(cas.nom, 'avertissement', a.avertissement, r.avertissement);
    comparer(cas.nom, 'motif_non_verifiee', a.motif_non_verifiee, r.motifNonVerifiee);
    comparer(cas.nom, 'boites', a.boites, r.boites);
    comparer(cas.nom, 'nb manifestes', a.manifestes.length, r.manifestes.length);
    a.manifestes.forEach((am, i) => {
      const m = r.manifestes[i];
      if (!m) return;
      comparer(cas.nom, `manifeste ${i} label`, am.label, m.label);
      comparer(cas.nom, `manifeste ${i} generateur`, am.generateur, m.generateur);
      comparer(cas.nom, `manifeste ${i} algorithme`, am.algorithme_signature, m.algorithmeSignature);
      comparer(cas.nom, `manifeste ${i} signature`, am.signature_presente, m.signaturePresente);
      comparer(cas.nom, `manifeste ${i} assertions`, am.assertions, Object.keys(m.assertions).sort());
      comparer(cas.nom, `manifeste ${i} actions`, am.actions, normaliser(m.actions));
      comparer(cas.nom, `manifeste ${i} revendication`, am.revendication, normaliser(m.revendication));
    });
  }

  // --- XMP ---
  for (const cas of v.xmp) {
    const blocs = P.extraireXmp(octets(cas.hex));
    comparer(cas.nom, 'nb blocs', cas.blocs.length, blocs.length);
    cas.blocs.forEach((ab, i) => {
      const b = blocs[i];
      if (!b) return;
      comparer(cas.nom, `[${i}] conteneur`, ab.conteneur, b.conteneur);
      comparer(cas.nom, `[${i}] etendu`, ab.etendu, b.etendu);
      comparer(cas.nom, `[${i}] octets`, ab.octets, b.octets);
      comparer(cas.nom, `[${i}] début du paquet`, ab.debut, b.brut.slice(0, 24));
      comparer(cas.nom, `[${i}] champs`, ab.champs, b.champs);
    });
  }

  // --- IPTC ---
  for (const cas of v.iptc) {
    const enr = P.extraireIptc(octets(cas.hex));
    comparer(cas.nom, 'nb enregistrements', cas.enregistrements.length, enr.length);
    cas.enregistrements.forEach((ae, i) => {
      const e = enr[i];
      if (!e) return;
      comparer(cas.nom, `[${i}]`, ae, { jeu: e.jeu, numero: e.numero, libelle: e.libelle, valeur: e.valeur });
    });
  }

  // --- Chaînes ---
  for (const cas of v.chaines) {
    const ch = P.extraireChaines(octets(cas.hex));
    comparer(cas.nom, 'nb chaînes', cas.chaines.length, ch.length);
    comparer(cas.nom, 'chaînes', cas.chaines,
      ch.map((c) => ({ offset: c.offset, encodage: c.encodage, texte: c.texte, marqueur: c.marqueur })));
    const prov = P.analyserProvenance(octets(cas.hex));
    comparer(cas.nom, 'marqueurs', cas.marqueurs_logiciels, prov.marqueursLogiciels);
  }

  comparer('constantes', 'marqueurs logiciels', v.marqueurs_logiciels, P.MARQUEURS_LOGICIELS);
  comparer('constantes', 'avertissement C2PA', v.avertissement_c2pa, P.AVERTISSEMENT_C2PA);

  // --- EXIF étendu ---
  const comparerExif = (nom, attendu, e) => {
    for (const [cle, champ] of [
      ['fabricant', 'fabricant'], ['modele', 'modele'], ['logiciel', 'logiciel'],
      ['artiste', 'artiste'], ['droits', 'droits'],
      ['date_heure_original', 'dateHeureOriginal'],
      ['date_heure_modification', 'dateHeureModification'],
      ['date_heure_numerisation', 'dateHeureNumerisation'],
      ['sensibilite_iso', 'sensibiliteIso'], ['ouverture', 'ouverture'],
      ['temps_pose_s', 'tempsPoseS'], ['focale_mm', 'focaleMm'],
      ['focale_equivalente_35mm', 'focaleEquivalente35mm'],
      ['largeur_px', 'largeurPx'], ['hauteur_px', 'hauteurPx'],
      ['largeur_ifd0_px', 'largeurIfd0Px'], ['hauteur_ifd0_px', 'hauteurIfd0Px'],
      ['resolution_x', 'resolutionX'], ['resolution_y', 'resolutionY'],
      ['unite_resolution', 'uniteResolution'], ['dpi_x', 'dpiX'], ['dpi_y', 'dpiY'],
      ['espace_colorimetrique', 'espaceColorimetrique'],
      ['mode_exposition', 'modeExposition'],
      ['programme_exposition', 'programmeExposition'],
      ['balance_blancs', 'balanceBlancs'],
      ['rapport_zoom_numerique', 'rapportZoomNumerique'],
      ['type_scene', 'typeScene'], ['flash', 'flash'],
    ]) {
      comparer(nom, cle, attendu[cle], e[champ]);
    }
    const lib = N.libellesExif(e);
    for (const [cle, champ] of [
      ['flash', 'flash'], ['mode_exposition', 'modeExposition'],
      ['programme_exposition', 'programmeExposition'], ['balance_blancs', 'balanceBlancs'],
      ['espace_colorimetrique', 'espaceColorimetrique'], ['type_scene', 'typeScene'],
      ['unite_resolution', 'uniteResolution'],
    ]) {
      comparer(nom, `libellé ${cle}`, attendu.libelles[cle], lib[champ]);
    }
    comparer(nom, 'zoom numérique appliqué', attendu.zoom_numerique_applique, N.zoomNumeriqueApplique(e));
    if (attendu.miniature === null) {
      comparer(nom, 'miniature', null, e.miniature);
    } else {
      comparer(nom, 'miniature offset', attendu.miniature.offset, e.miniature?.offset);
      comparer(nom, 'miniature longueur', attendu.miniature.longueur, e.miniature?.longueur);
      comparer(nom, 'miniature compression', attendu.miniature.compression, e.miniature?.compression);
      comparer(nom, 'miniature est JPEG', attendu.miniature.est_jpeg, e.miniature?.estJpeg);
      comparer(nom, 'miniature octets', attendu.miniature.octets_hex,
        e.miniature ? Buffer.from(e.miniature.octets).toString('hex') : null);
    }
  };

  for (const cas of v.exif.jpeg) comparerExif(cas.nom, cas.exif, N.lireExifDepuisJpeg(octets(cas.hex)));
  for (const cas of v.exif.tiff) comparerExif(cas.nom, cas.exif, N.lireExifDepuisTiff(octets(cas.hex)));
  for (const f of v.exif.flash) comparer(`flash 0x${f.code.toString(16)}`, 'libellé', f.libelle, N.decrireFlash(f.code));
  for (const d of v.exif.dpi) comparer(`DPI ${d.resolution}/${d.unite}`, 'valeur', d.dpi, N.versDpi(d.resolution, d.unite));

  // --- Refus attendus ---
  const refus = [
    ['CBOR tronqué', () => P.decoderCbor(octets('1903'))],
    ['CBOR trop imbriqué', () => P.decoderCbor(new Uint8Array([...Array(1000).fill(0x81), 0x00]))],
    ['CBOR information réservée', () => P.decoderCbor(new Uint8Array([0x1c]))],
  ];
  for (const [nom, f] of refus) {
    n += 1;
    let leve = false;
    try { f(); } catch { leve = true; }
    if (!leve) ecarts.push({ sujet: 'refus attendu', champ: nom, attendu: 'erreur', obtenu: 'aucune' });
  }

  // --- Le port ne doit jamais se déclarer vérificateur ---
  for (const affirmation of ['est authentique', 'est valide', 'signature valide', 'provenance vérifiée']) {
    n += 1;
    if (P.AVERTISSEMENT_C2PA.toLowerCase().includes(affirmation)) {
      ecarts.push({ sujet: 'restitution', champ: `affirmation « ${affirmation} »`, attendu: 'absente', obtenu: 'présente' });
    }
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 25)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu}`);
    }
    if (ecarts.length > 25) console.error(`  … et ${ecarts.length - 25} autre(s).`);
    console.error("\n  Corriger le Python d'abord, puis répercuter ici, puis régénérer les vecteurs.\n");
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
