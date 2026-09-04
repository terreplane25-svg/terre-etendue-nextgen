/**
 * verifier-port-rapport.mjs — Épingle le port TypeScript de l'outil C au Python.
 *
 * Ce qui est vérifié ici n'est pas du calcul mais une structure : les neuf
 * blocs du §33, le nom et l'ORDRE exact de leurs cinquante-six champs, les dix
 * répertoires du §34 et leurs descriptions. C'est le genre de chose qui se
 * désynchronise sans que rien ne casse — un champ ajouté côté Python et oublié
 * côté navigateur donnerait une fiche qui a l'air complète et qui ne l'est pas.
 *
 *     node scripts/verifier-port-rapport.mjs
 *
 * Régénérer les vecteurs après toute correction du Python :
 *     python3 scripts/generer-vecteurs-or-rapport.py
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC = join(RACINE, 'src', 'lib', 'rapport-expertise', 'noyau.ts');
const VECTEURS = join(RACINE, 'src', 'lib', 'rapport-expertise', 'vecteurs-or.json');

const ecarts = [];
const faux = (sujet, champ, attendu, obtenu) => ecarts.push({ sujet, champ, attendu, obtenu });

const dossier = mkdtempSync(join(tmpdir(), 'rapport-port-'));
try {
  execFileSync(
    'npx',
    ['--no-install', 'tsc', SRC, '--target', 'ES2022', '--module', 'ES2022',
     '--moduleResolution', 'bundler', '--outDir', dossier, '--strict'],
    { cwd: RACINE, stdio: 'pipe' },
  );
  const M = await import(pathToFileURL(join(dossier, 'noyau.js')).href);
  const v = JSON.parse(readFileSync(VECTEURS, 'utf8'));
  let n = 0;

  if (v.sentinel_indisponible !== M.INDISPONIBLE) {
    faux('sentinel', 'INDISPONIBLE', v.sentinel_indisponible, M.INDISPONIBLE);
  }
  n += 1;

  // Les blocs, dans l'ordre, avec leurs champs dans l'ordre.
  if (v.blocs.length !== M.BLOCS.length) {
    faux('blocs', 'nombre', v.blocs.length, M.BLOCS.length);
  }
  n += 1;
  for (let i = 0; i < v.blocs.length; i++) {
    const attendu = v.blocs[i];
    const obtenu = M.BLOCS[i];
    if (!obtenu) {
      faux(`bloc ${i}`, 'présence', attendu.nom, 'absent');
      continue;
    }
    if (obtenu.nom !== attendu.nom) faux(`bloc ${i}`, 'nom', attendu.nom, obtenu.nom);
    const nomsTs = obtenu.champs.map((c) => c.nom);
    if (nomsTs.join('|') !== attendu.champs.join('|')) {
      faux(`bloc ${attendu.nom}`, 'champs et leur ordre', attendu.champs.join(', '), nomsTs.join(', '));
    }
    // Chaque champ doit porter un libellé et une aide : une structure sans
    // intitulé se remplirait à l'aveugle.
    for (const c of obtenu.champs) {
      if (!c.libelle || !c.aide) faux(`champ ${attendu.nom}.${c.nom}`, 'libellé et aide', 'non vides', `${c.libelle} / ${c.aide}`);
    }
    n += 2 + obtenu.champs.length;
  }

  // Les trois fiches et leurs champs indisponibles.
  for (const f of v.fiches) {
    const sujet = `fiche ${f.mode}`;
    const obtenus = M.champsIndisponibles(f.contenu);
    if (obtenus.join('|') !== f.champs_indisponibles.join('|')) {
      faux(sujet, 'champs_indisponibles', f.champs_indisponibles.join(', '), obtenus.join(', '));
    }
    // Une fiche des vecteurs est toujours entièrement déclarée : aucun omis.
    const omis = M.champsOmis(f.contenu);
    if (omis.length !== 0) faux(sujet, 'champsOmis', '[]', omis.join(', '));
    // Et elle passe donc la validation.
    let leve = null;
    try { M.validerFiche(f.contenu); } catch (err) { leve = err.message; }
    if (leve) faux(sujet, 'validerFiche', 'aucune erreur', leve);
    n += 3;
  }

  // Une fiche vide : tous les champs omis, aucun indisponible, validation refusée.
  const vide = M.ficheVide();
  const totalChamps = v.blocs.reduce((s, b) => s + b.champs.length, 0);
  if (M.champsOmis(vide).length !== totalChamps) {
    faux('fiche vide', 'champsOmis', totalChamps, M.champsOmis(vide).length);
  }
  if (M.champsIndisponibles(vide).length !== 0) {
    faux('fiche vide', 'champsIndisponibles', 0, M.champsIndisponibles(vide).length);
  }
  let refuse = false;
  try { M.validerFiche(vide); } catch { refuse = true; }
  if (!refuse) faux('fiche vide', 'validerFiche', 'erreur levée', 'aucune erreur');
  n += 3;

  // declarer refuse le vide et le nul.
  for (const r of v.refus_declarer) {
    const valeur = r.valeur === 'null' ? null : '';
    let leve = false;
    try { M.declarer(valeur, 'champ_de_test'); } catch { leve = true; }
    if (!leve) faux(`declarer ${r.valeur}`, 'refus', 'erreur levée', 'aucune erreur');
    n += 1;
  }

  // L'arborescence : noms, ordre, descriptions.
  if (v.arborescence.length !== M.ARBORESCENCE_IMPOSEE.length) {
    faux('arborescence', 'nombre', v.arborescence.length, M.ARBORESCENCE_IMPOSEE.length);
  }
  n += 1;
  for (let i = 0; i < v.arborescence.length; i++) {
    const a = v.arborescence[i];
    const o = M.ARBORESCENCE_IMPOSEE[i];
    if (!o) { faux(`répertoire ${i}`, 'présence', a.nom, 'absent'); continue; }
    if (o.nom !== a.nom) faux(`répertoire ${i}`, 'nom', a.nom, o.nom);
    // Les apostrophes typographiques du port diffèrent des droites du Python :
    // on compare sur une forme normalisée, la description étant du texte
    // d'affichage et non un identifiant.
    const norm = (s) => s.replace(/[’']/g, "'").trim();
    if (norm(o.description) !== norm(a.description)) {
      faux(`répertoire ${a.nom}`, 'description', a.description, o.description);
    }
    n += 2;
  }

  for (const c of v.nom_dossier) {
    const obtenu = M.nomDossierArchive(c.identifiant);
    if (obtenu !== c.nom) faux(`nom_dossier « ${c.identifiant} »`, 'nom', c.nom, obtenu);
    n += 1;
  }
  for (const c of v.refus_nom_dossier) {
    let leve = false;
    try { M.nomDossierArchive(c.identifiant); } catch { leve = true; }
    if (!leve) faux(`nom_dossier « ${c.identifiant} »`, 'refus', 'erreur levée', 'aucune erreur');
    n += 1;
  }

  if (ecarts.length > 0) {
    console.error(`\n✗ Le port TypeScript a dérivé du paquet Python : ${ecarts.length} écart(s) sur ${n} contrôles.\n`);
    for (const e of ecarts.slice(0, 25)) {
      console.error(`  ${e.sujet}\n    ${e.champ} : attendu ${e.attendu}, obtenu ${e.obtenu}`);
    }
    if (ecarts.length > 25) console.error(`  … et ${ecarts.length - 25} autre(s).`);
    console.error('\n  Corriger le Python d\'abord, puis répercuter ici, puis régénérer les vecteurs.\n');
    process.exitCode = 1;
  } else {
    console.log(`✓ Port TypeScript conforme au paquet Python : ${n} contrôles, aucun écart.`);
    console.log(`  Vecteurs générés le ${v.genere_le}`);
  }
} finally {
  rmSync(dossier, { recursive: true, force: true });
}
