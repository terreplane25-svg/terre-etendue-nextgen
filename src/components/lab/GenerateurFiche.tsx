'use client';
/**
 * GenerateurFiche — Fiche standard d'observation (§33) et archive figée (§34).
 *
 * Expose l'outil C, via le port TypeScript de `src/lib/rapport-expertise/` —
 * épinglé au paquet Python par 117 contrôles.
 *
 * La règle du §33 gouverne toute l'interface : aucun champ ne peut rester
 * vide. Chacun exige un choix explicite — une valeur, ou le sentinel
 * INDISPONIBLE. On ne peut donc pas produire une fiche « en partie remplie »
 * : soit elle est complète, soit elle dit précisément ce qui manque.
 *
 * Ce que le navigateur ne peut pas faire est dit, pas simulé : le paquet
 * Python retire le droit d'écriture sur 10-originaux/ par un chmod, et il n'y
 * a pas de système de fichiers à verrouiller ici. La commande est fournie.
 */
import { useCallback, useMemo, useRef, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import { empreinteSha256 } from '@/lib/preuve-image/noyau';
import {
  ARBORESCENCE_IMPOSEE,
  BLOCS,
  COMMANDE_VERROUILLAGE,
  INDISPONIBLE,
  type Fiche,
  champsIndisponibles,
  champsOmis,
  ficheVide,
  nomDossierArchive,
} from '@/lib/rapport-expertise/noyau';
import { construireZip, texte, type EntreeZip } from '@/lib/rapport-expertise/zip';

const ACCENT = dash.lavender;

interface PieceJointe {
  nom: string;
  taille: number;
  empreinte: string;
}

function Compteur({ valeur, total, couleur, libelle }: {
  valeur: number; total: number; couleur: string; libelle: string;
}) {
  return (
    <div style={{
      flex: '1 1 140px', padding: '10px 14px', borderRadius: 8,
      background: 'var(--card)', border: `1px solid ${couleur}40`,
      borderLeft: `3px solid ${couleur}`,
    }}>
      <div style={{ fontSize: 22, fontWeight: 700, fontFamily: dash.fontMono, color: couleur, lineHeight: 1.1 }}>
        {valeur}<span style={{ fontSize: 13, color: 'var(--ink-muted)', fontWeight: 400 }}> / {total}</span>
      </div>
      <div style={{ fontSize: 11.5, color: 'var(--ink-soft)', marginTop: 3, lineHeight: 1.35 }}>{libelle}</div>
    </div>
  );
}

export default function GenerateurFiche() {
  const [fiche, setFiche] = useState<Fiche>(ficheVide);
  const [ouverts, setOuverts] = useState<Record<string, boolean>>({ identification: true });
  const [pieces, setPieces] = useState<PieceJointe[]>([]);
  const [enCours, setEnCours] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const totalChamps = useMemo(() => BLOCS.reduce((s, b) => s + b.champs.length, 0), []);
  const omis = useMemo(() => champsOmis(fiche), [fiche]);
  const indisponibles = useMemo(() => champsIndisponibles(fiche), [fiche]);
  const renseignes = totalChamps - omis.length - indisponibles.length;

  const identifiant = fiche.identification?.identifiant_dossier ?? '';
  const identifiantUtilisable = identifiant.trim() !== '' && identifiant !== INDISPONIBLE;

  const majChamp = useCallback((bloc: string, champ: string, valeur: string) => {
    setFiche((p) => ({ ...p, [bloc]: { ...p[bloc], [champ]: valeur } }));
    setMessage(null);
  }, []);

  const ajouterPieces = useCallback(async (fichiers: FileList) => {
    setEnCours(true);
    try {
      const nouvelles: PieceJointe[] = [];
      for (const f of Array.from(fichiers)) {
        const octets = new Uint8Array(await f.arrayBuffer());
        nouvelles.push({ nom: f.name, taille: octets.length, empreinte: await empreinteSha256(octets) });
      }
      setPieces((p) => [...p, ...nouvelles]);
    } finally {
      setEnCours(false);
    }
  }, []);

  /** La fiche en texte structuré, telle qu'elle ira dans 20-fiche/. */
  const ficheEnTexte = useCallback((): string => {
    const l: string[] = [
      'FICHE STANDARD D’OBSERVATION',
      'Protocole « Portion visible d’une cible éloignée au-dessus de la mer » v1.0, §33',
      '',
      `Établie le ${new Date().toISOString()}`,
      `Champs renseignés : ${renseignes} · déclarés indisponibles : ${indisponibles.length} · omis : ${omis.length}`,
      '',
      'Un champ marqué « indisponible » l’est explicitement. Un dossier incomplet',
      'est indéterminé, pas défavorable (§33) — mais il faut pouvoir dire ce qui',
      'manque, et c’est ce que la liste finale énumère.',
      '',
    ];
    for (const b of BLOCS) {
      l.push('═'.repeat(72), b.titre.toUpperCase(), '');
      for (const c of b.champs) {
        const v = fiche[b.nom][c.nom];
        l.push(`  ${c.libelle}`);
        l.push(`    ${c.nom} = ${v === '' ? '(OMIS — la fiche n’est pas complète)' : v}`);
        l.push('');
      }
    }
    l.push('═'.repeat(72), 'CHAMPS DÉCLARÉS INDISPONIBLES', '');
    if (indisponibles.length === 0) l.push('  aucun');
    else for (const c of indisponibles) l.push(`  ${c}`);
    l.push('', '═'.repeat(72), 'CHAMPS OMIS', '');
    if (omis.length === 0) l.push('  aucun — la fiche est complète au sens du §33');
    else for (const c of omis) l.push(`  ${c}`);
    l.push('');
    return l.join('\n');
  }, [fiche, indisponibles, omis, renseignes]);

  const telecharger = useCallback(() => {
    let dossier: string;
    try {
      dossier = nomDossierArchive(identifiant.trim());
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
      return;
    }
    const maintenant = new Date();
    const entrees: EntreeZip[] = [{ chemin: `${dossier}/` }];

    const lisezMoi = [
      `ARCHIVE ${dossier}`,
      'Arborescence imposée par le §34 du protocole « Portion visible d’une cible',
      'éloignée au-dessus de la mer » v1.0.',
      '',
      `Créée le ${maintenant.toISOString()} depuis le navigateur.`,
      '',
      'Les numéros fixent l’ordre de lecture : le pré-enregistrement vient avant',
      'les données, les données avant les mesures, les mesures avant le rapport.',
      '',
    ];
    for (const d of ARBORESCENCE_IMPOSEE) {
      entrees.push({ chemin: `${dossier}/${d.nom}/` });
      entrees.push({
        chemin: `${dossier}/${d.nom}/LISEZ-MOI.txt`,
        contenu: texte(`${d.nom}\n${'─'.repeat(d.nom.length)}\n\n${d.description}\n`),
      });
      lisezMoi.push(`  ${d.nom.padEnd(22)} ${d.description}`);
    }
    lisezMoi.push(
      '',
      'CE QUE CETTE ARCHIVE NE CONTIENT PAS ENCORE',
      '',
      '  · Le verrouillage de 10-originaux/. Un navigateur n’a pas de système de',
      '    fichiers à verrouiller. Une fois les fichiers d’origine déposés dedans,',
      '    et une fois seulement, exécuter depuis la racine de l’archive :',
      '',
      `        ${COMMANDE_VERROUILLAGE}`,
      '',
      '  · La preuve de datation des empreintes. Le SHA256SUMS ci-joint établit',
      '    l’intégrité, pas la date : celle-ci doit être attestée par un tiers,',
      '    le jour même (§17.1). Sans cela, la date n’est qu’une déclaration.',
      '',
      '  · La licence de reprise, à déposer dans 70-rapport/ (§34).',
      '',
      'VÉRIFIER L’ARCHIVE',
      '',
      '  Les entrées sont stockées sans compression : leur empreinte est la même',
      '  dans l’archive et hors d’elle. Depuis 11-empreintes/ :',
      '',
      '        sha256sum -c SHA256SUMS',
      '',
    );
    entrees.push({ chemin: `${dossier}/LISEZ-MOI.txt`, contenu: texte(lisezMoi.join('\n')) });

    entrees.push({
      chemin: `${dossier}/20-fiche/fiche-observation.txt`,
      contenu: texte(ficheEnTexte()),
    });
    entrees.push({
      chemin: `${dossier}/20-fiche/fiche-observation.json`,
      contenu: texte(JSON.stringify({
        protocole: 'Portion visible d’une cible éloignée au-dessus de la mer v1.0',
        rubrique: '§33 — fiche standard d’observation',
        etablie_le: maintenant.toISOString(),
        sentinel_indisponible: INDISPONIBLE,
        fiche,
        champs_indisponibles: indisponibles,
        champs_omis: omis,
      }, null, 2) + '\n'),
    });

    if (pieces.length > 0) {
      entrees.push({
        chemin: `${dossier}/11-empreintes/SHA256SUMS`,
        contenu: texte(pieces.map((p) => `${p.empreinte}  ${p.nom}`).join('\n') + '\n'),
      });
      entrees.push({
        chemin: `${dossier}/11-empreintes/date-de-calcul.txt`,
        contenu: texte(
          `Empreintes calculées le ${maintenant.toISOString()} dans le navigateur.\n\n` +
          'Cette date est une DÉCLARATION, pas une preuve. Le §17.1 demande un\n' +
          'dépôt le jour même auprès d’un tiers qui la date : horodatage\n' +
          'électronique, publication datée, registre public. La preuve doit être\n' +
          'jointe dans ce même répertoire.\n\n' +
          'Les fichiers eux-mêmes ne sont pas dans cette archive : ils doivent\n' +
          'être déposés dans 10-originaux/, puis 10-originaux/ verrouillé.\n',
        ),
      });
    }

    entrees.push({
      chemin: `${dossier}/90-journal/journal.txt`,
      contenu: texte(
        'JOURNAL DES OPÉRATIONS — en ajout seul, on n’y efface rien (§34)\n\n' +
        `${maintenant.toISOString()}  création de l’arborescence et de la fiche ` +
        `(navigateur) ; ${renseignes} champs renseignés, ${indisponibles.length} ` +
        `déclarés indisponibles, ${omis.length} omis\n` +
        (pieces.length > 0
          ? `${maintenant.toISOString()}  empreintes calculées pour ${pieces.length} fichier(s)\n`
          : '') +
        '\n' +
        'Ajouter ici, à la suite, toute opération ultérieure — y compris les\n' +
        'écarts au plan déposé, avec leur date et leur motif.\n',
      ),
    });

    const zip = construireZip(entrees, maintenant);
    // Une copie du tampon : le Blob ne doit pas dépendre du tableau typé.
    const blob = new Blob([zip.slice().buffer as ArrayBuffer], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${dossier}.zip`;
    a.click();
    URL.revokeObjectURL(url);
    setMessage(
      `Archive « ${dossier}.zip » produite : ${entrees.length} entrées, ` +
      `${(zip.length / 1024).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} kio.`,
    );
  }, [identifiant, ficheEnTexte, fiche, indisponibles, omis, pieces, renseignes]);

  return (
    <div style={{ maxWidth: 940, margin: '0 auto' }}>

      <div style={{
        background: dash.lavenderSoft, border: `1px solid ${ACCENT}40`,
        borderRadius: 10, padding: '16px 20px', marginBottom: 18,
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 8,
        }}>Aucun champ ne peut rester vide</div>
        <p style={{ margin: '0 0 8px', fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          Les cinquante-six champs du §33 exigent chacun un choix explicite : une valeur, ou la
          mention <strong>indisponible</strong>. C’est la règle du protocole, et c’est pourquoi
          rien n’est prérempli et pourquoi il n’existe pas de fiche « à moitié remplie » — soit
          elle est complète, soit elle dit précisément ce qui manque.
        </p>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          Un dossier incomplet est <strong>indéterminé, pas défavorable</strong>. L’archive
          produite énumère donc les champs manquants au lieu de les taire.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
        <Compteur valeur={renseignes} total={totalChamps} couleur={dash.opal} libelle="renseignés" />
        <Compteur valeur={indisponibles.length} total={totalChamps} couleur={dash.saffron} libelle="déclarés indisponibles" />
        <Compteur valeur={omis.length} total={totalChamps} couleur={omis.length === 0 ? dash.opal : dash.rose} libelle="omis — à trancher" />
      </div>

      {/* ── Les neuf blocs ── */}
      {BLOCS.map((b) => {
        const ouvert = ouverts[b.nom] ?? false;
        const omisBloc = b.champs.filter((c) => fiche[b.nom][c.nom] === '').length;
        return (
          <div key={b.nom} style={{
            background: 'var(--card)', border: '1px solid var(--border)',
            borderRadius: 10, marginBottom: 12, overflow: 'hidden',
          }}>
            <button
              onClick={() => setOuverts((p) => ({ ...p, [b.nom]: !ouvert }))}
              style={{
                width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                padding: '14px 18px', background: 'transparent', border: 'none',
                cursor: 'pointer', textAlign: 'left',
              }}
            >
              <span style={{
                fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, color: ACCENT,
                border: `1px solid ${ACCENT}40`, borderRadius: 3, padding: '2px 6px',
              }}>{String(BLOCS.indexOf(b) + 1).padStart(2, '0')}</span>
              <span style={{ flex: 1, fontSize: 14.5, fontWeight: 700, color: 'var(--ink)' }}>{b.titre}</span>
              <span style={{
                fontSize: 11.5, fontFamily: dash.fontMono,
                color: omisBloc === 0 ? dash.opal : dash.rose,
              }}>
                {omisBloc === 0 ? 'complet' : `${omisBloc} à trancher`}
              </span>
              <span style={{ fontSize: 13, color: 'var(--ink-muted)' }}>{ouvert ? '▲' : '▼'}</span>
            </button>
            {ouvert && (
              <div style={{ padding: '0 18px 16px' }}>
                {b.champs.map((c) => {
                  const v = fiche[b.nom][c.nom];
                  const estIndispo = v === INDISPONIBLE;
                  const estOmis = v === '';
                  return (
                    <div key={c.nom} style={{ marginBottom: 14 }}>
                      <label style={{
                        display: 'block', fontSize: 12, fontWeight: 600,
                        color: 'var(--ink)', marginBottom: 4,
                      }}>{c.libelle}</label>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'stretch' }}>
                        <input
                          type="text"
                          value={estIndispo ? '' : v}
                          disabled={estIndispo}
                          placeholder={estIndispo ? INDISPONIBLE : '—'}
                          onChange={(ev) => majChamp(b.nom, c.nom, ev.target.value)}
                          aria-label={c.libelle}
                          style={{
                            flex: 1, minWidth: 0, padding: '8px 10px', fontSize: 13,
                            background: estIndispo ? 'var(--bg)' : 'var(--card)',
                            color: estIndispo ? dash.inkMuted : 'var(--ink)',
                            fontStyle: estIndispo ? 'italic' : 'normal',
                            border: `1px solid ${estOmis ? dash.rose + '80' : estIndispo ? dash.saffron + '80' : ACCENT + '60'}`,
                            borderRadius: 5, outline: 'none',
                          }}
                        />
                        <button
                          onClick={() => majChamp(b.nom, c.nom, estIndispo ? '' : INDISPONIBLE)}
                          style={{
                            padding: '8px 11px', fontSize: 11.5, cursor: 'pointer', whiteSpace: 'nowrap',
                            background: estIndispo ? dash.saffronSoft : 'var(--card)',
                            color: estIndispo ? dash.saffron : 'var(--ink-muted)',
                            border: `1px solid ${estIndispo ? dash.saffron : 'var(--border)'}`,
                            borderRadius: 5, fontWeight: estIndispo ? 700 : 400,
                          }}
                        >{estIndispo ? 'annuler' : 'indisponible'}</button>
                      </div>
                      <p style={{ margin: '4px 0 0', fontSize: 11.5, color: 'var(--ink-muted)', lineHeight: 1.45 }}>
                        <code style={{ fontSize: 10.5, fontFamily: dash.fontMono, color: dash.inkGhost }}>{c.nom}</code>
                        {' — '}{c.aide}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      {/* ── Empreintes des fichiers d'origine ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '18px 20px', marginBottom: 16,
      }}>
        <h3 style={{ margin: '0 0 6px', fontSize: 14.5, fontWeight: 700, color: 'var(--ink)' }}>
          Empreintes des fichiers d’origine
        </h3>
        <p style={{ margin: '0 0 12px', fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
          Les fichiers ne sont pas transmis et ne seront pas mis dans l’archive : seules leurs
          empreintes le sont, dans <code style={{ fontSize: 11.5 }}>11-empreintes/SHA256SUMS</code>.
          Vous déposerez les fichiers eux-mêmes dans <code style={{ fontSize: 11.5 }}>10-originaux/</code>,
          puis vous verrouillerez ce répertoire.
        </p>
        <button
          onClick={() => inputRef.current?.click()}
          disabled={enCours}
          style={{
            padding: '9px 16px', fontSize: 13, fontWeight: 600, cursor: enCours ? 'wait' : 'pointer',
            background: 'var(--card)', color: 'var(--ink)',
            border: `1px solid ${ACCENT}`, borderRadius: 6,
          }}
        >{enCours ? 'Calcul en cours…' : 'Ajouter des fichiers'}</button>
        <input
          ref={inputRef} type="file" multiple style={{ display: 'none' }}
          onChange={(ev) => { if (ev.target.files?.length) void ajouterPieces(ev.target.files); ev.target.value = ''; }}
        />
        {pieces.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
            <tbody>
              {pieces.map((p, i) => (
                <tr key={i}>
                  <td style={{ padding: '6px 10px 6px 0', fontSize: 12.5, color: 'var(--ink)' }}>{p.nom}</td>
                  <td style={{ padding: '6px 10px', fontSize: 11.5, fontFamily: dash.fontMono, color: 'var(--ink-muted)', textAlign: 'right', whiteSpace: 'nowrap' }}>
                    {p.taille.toLocaleString('fr-FR')} o
                  </td>
                  <td style={{ padding: '6px 0', fontSize: 11, fontFamily: dash.fontMono, color: 'var(--ink-soft)', wordBreak: 'break-all' }}>
                    {p.empreinte}
                  </td>
                  <td style={{ padding: '6px 0 6px 10px' }}>
                    <button
                      onClick={() => setPieces((prev) => prev.filter((_, j) => j !== i))}
                      style={{
                        fontSize: 11, padding: '2px 7px', cursor: 'pointer',
                        background: 'transparent', color: dash.rose,
                        border: `1px solid ${dash.rose}40`, borderRadius: 4,
                      }}
                    >retirer</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Production de l'archive ── */}
      <div style={{
        background: 'var(--card)', border: `1px solid ${omis.length === 0 ? ACCENT : 'var(--border)'}`,
        borderRadius: 10, padding: '18px 20px', marginBottom: 16,
      }}>
        <h3 style={{ margin: '0 0 10px', fontSize: 14.5, fontWeight: 700, color: 'var(--ink)' }}>
          Archive du §34
        </h3>
        {omis.length > 0 && (
          <p style={{
            margin: '0 0 12px', fontSize: 13, lineHeight: 1.6, color: 'var(--ink)',
            padding: '10px 12px', borderRadius: 6,
            background: dash.roseSoft, border: `1px solid ${dash.rose}40`,
          }}>
            <strong>{omis.length} champ{omis.length > 1 ? 's' : ''} non tranché{omis.length > 1 ? 's' : ''}.</strong>{' '}
            L’archive reste produisible — le protocole veut qu’un dossier incomplet soit
            indéterminé, pas refusé — mais la fiche portera la mention <em>OMIS</em> à chacun de
            ces endroits, et les listera. Trancher chaque champ, même par « indisponible », vaut
            mieux que de laisser un blanc.
          </p>
        )}
        <button
          onClick={telecharger}
          disabled={!identifiantUtilisable}
          title={identifiantUtilisable ? undefined : 'Renseignez d’abord l’identifiant du dossier'}
          style={{
            padding: '11px 20px', fontSize: 14, fontWeight: 700,
            cursor: identifiantUtilisable ? 'pointer' : 'not-allowed',
            background: identifiantUtilisable ? ACCENT : 'var(--border)',
            color: identifiantUtilisable ? '#fff' : 'var(--ink-muted)',
            border: 'none', borderRadius: 7,
          }}
        >Télécharger l’archive</button>
        {!identifiantUtilisable && (
          <p style={{ margin: '8px 0 0', fontSize: 12.5, color: dash.rose }}>
            L’archive se nomme d’après l’identifiant du dossier : renseignez-le dans le bloc 01.
            Un identifiant « indisponible » ne peut pas nommer une archive.
          </p>
        )}
        {message && (
          <p style={{ margin: '10px 0 0', fontSize: 13, lineHeight: 1.55, color: 'var(--ink)' }}>{message}</p>
        )}
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
          <p style={{ margin: '0 0 8px', fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
            <strong>Ce que le navigateur ne peut pas faire.</strong> Le paquet de référence retire
            le droit d’écriture sur <code style={{ fontSize: 11.5 }}>10-originaux/</code> ; il n’y a
            pas de système de fichiers à verrouiller ici. Une fois les fichiers d’origine déposés
            dedans, et une fois seulement, depuis la racine de l’archive :
          </p>
          <code style={{
            display: 'block', padding: '9px 12px', borderRadius: 6, fontSize: 12.5,
            fontFamily: dash.fontMono, background: 'var(--bg)',
            border: '1px solid var(--border)', color: 'var(--ink)',
          }}>{COMMANDE_VERROUILLAGE}</code>
          <p style={{ margin: '10px 0 0', fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
            Les entrées de l’archive sont stockées sans compression : l’empreinte d’un fichier est
            la même dedans et dehors, ce qui permet de contrôler le manifeste sans décompresseur —{' '}
            <code style={{ fontSize: 11.5 }}>sha256sum -c SHA256SUMS</code> depuis{' '}
            <code style={{ fontSize: 11.5 }}>11-empreintes/</code>.
          </p>
        </div>
      </div>
    </div>
  );
}
