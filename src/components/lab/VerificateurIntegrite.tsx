'use client';
/**
 * VerificateurIntegrite — Empreinte SHA-256 et métadonnées d'un fichier image.
 *
 * Expose l'outil B du protocole, via le port TypeScript de
 * `src/lib/preuve-image/` — épinglé au paquet Python par 152 contrôles
 * (scripts/verifier-port-preuve.mjs).
 *
 * TOUT SE PASSE DANS LE NAVIGATEUR. Le fichier n'est jamais transmis, ni
 * stocké, ni journalisé côté serveur. Ce n'est pas une commodité technique :
 * c'est ce qu'un tiers de confiance doit pouvoir dire de son propre outil.
 *
 * Les mêmes règles que le calculateur gouvernent l'affichage :
 *
 *  1. Un champ que l'appareil n'a pas écrit s'affiche « non écrit par
 *     l'appareil », jamais rempli d'une valeur plausible.
 *  2. Ce que l'outil établit et ce qu'il n'établit pas sont dits ensemble :
 *     l'empreinte prouve l'intégrité, pas l'authenticité, et l'EXIF s'écrit.
 *  3. Un EXIF illisible n'invalide pas l'empreinte, et le motif de l'échec
 *     est rapporté tel quel plutôt qu'escamoté.
 */
import { useCallback, useRef, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import {
  INDISPONIBLE,
  type DonneesExif,
  type RapportFichier,
  analyserFichier,
  empreinteSha256,
  empreinteValide,
  libellesExif,
  zoomNumeriqueApplique,
} from '@/lib/preuve-image/noyau';
import {
  AVERTISSEMENT_C2PA,
  type Provenance,
  analyserProvenance,
} from '@/lib/preuve-image/provenance';
import { documentIngestion } from '@/lib/preuve-image/document';

const ACCENT = dash.cyan;
const NON_ECRIT = 'non écrit par l’appareil';

/** Un fichier volumineux se hache en flux ; au-delà, on refuse plutôt que de figer l'onglet. */
const TAILLE_MAX = 256 * 1024 * 1024;

function fmtTaille(o: number): string {
  if (o < 1024) return `${o} octets`;
  if (o < 1024 * 1024) return `${(o / 1024).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} kio`;
  return `${(o / (1024 * 1024)).toLocaleString('fr-FR', { maximumFractionDigits: 2 })} Mio`;
}

function fmtNb(x: number | null, n = 2, unite = ''): string {
  if (x === null) return NON_ECRIT;
  return `${x.toLocaleString('fr-FR', { maximumFractionDigits: n })}${unite ? ' ' + unite : ''}`;
}

function fmtPose(s: number | null): string {
  if (s === null) return NON_ECRIT;
  if (s >= 1) return `${s.toLocaleString('fr-FR', { maximumFractionDigits: 2 })} s`;
  return `1/${Math.round(1 / s)} s`;
}

function Ligne({ cle, val, mono = true }: { cle: string; val: string; mono?: boolean }) {
  const absent = val === NON_ECRIT || val === INDISPONIBLE;
  return (
    <tr>
      <td style={{
        padding: '7px 12px 7px 0', fontSize: 13, color: 'var(--ink-soft)',
        verticalAlign: 'top', whiteSpace: 'nowrap',
      }}>{cle}</td>
      <td style={{
        padding: '7px 0', fontSize: 13,
        fontFamily: absent || !mono ? 'inherit' : dash.fontMono,
        color: absent ? dash.inkMuted : 'var(--ink)',
        fontStyle: absent ? 'italic' : 'normal',
        wordBreak: 'break-all', verticalAlign: 'top',
      }}>{val}</td>
    </tr>
  );
}

function Bloc({ titre, num, children }: { titre: string; num: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)',
      borderRadius: 10, padding: '18px 20px', marginBottom: 16,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <span style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, color: ACCENT,
          border: `1px solid ${ACCENT}40`, borderRadius: 3, padding: '2px 6px',
        }}>{num}</span>
        <h3 style={{ margin: 0, fontSize: 14.5, fontWeight: 700, color: 'var(--ink)' }}>{titre}</h3>
      </div>
      {children}
    </div>
  );
}

function BlocExif({ d }: { d: DonneesExif }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <tbody>
        <Ligne cle="Fabricant" val={d.fabricant ?? NON_ECRIT} mono={false} />
        <Ligne cle="Modèle de boîtier" val={d.modele ?? NON_ECRIT} mono={false} />
        <Ligne cle="Objectif" val={d.objectif ?? NON_ECRIT} mono={false} />
        <Ligne cle="Focale optique réelle" val={fmtNb(d.focaleMm, 2, 'mm')} />
        <Ligne cle="Focale équivalente 24×36" val={fmtNb(d.focaleEquivalente35mm, 0, 'mm')} />
        <Ligne cle="Ouverture" val={d.ouverture === null ? NON_ECRIT : `f/${d.ouverture.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}`} />
        <Ligne cle="Temps de pose" val={fmtPose(d.tempsPoseS)} />
        <Ligne cle="Sensibilité" val={d.sensibiliteIso === null ? NON_ECRIT : `ISO ${d.sensibiliteIso}`} />
        <Ligne cle="Dimensions déclarées" val={d.largeurPx === null || d.hauteurPx === null ? NON_ECRIT : `${d.largeurPx} × ${d.hauteurPx} px`} />
        <Ligne cle="Date et heure de prise de vue" val={d.dateHeureOriginal ?? NON_ECRIT} />
        <Ligne cle="Orientation" val={fmtNb(d.orientation, 0)} />
      </tbody>
    </table>
  );
}

/**
 * Les champs d'ingestion. Chaque code est rendu AVEC son libellé, jamais
 * remplacé par lui : un libellé est une interprétation, le code est ce que
 * l'appareil a écrit. Un lecteur qui conteste la table garde la donnée.
 */
function BlocExifEtendu({ d }: { d: DonneesExif }) {
  const lib = libellesExif(d);
  const codeEt = (code: number | null, libelle: string | null) =>
    code === null ? NON_ECRIT : `${code}${libelle ? ` — ${libelle}` : ''}`;
  const zoom = zoomNumeriqueApplique(d);
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <tbody>
        <Ligne cle="Logiciel déclaré" val={d.logiciel ?? NON_ECRIT} mono={false} />
        <Ligne cle="Auteur déclaré" val={d.artiste ?? NON_ECRIT} mono={false} />
        <Ligne cle="Mention de droits" val={d.droits ?? NON_ECRIT} mono={false} />
        <Ligne cle="Date de numérisation" val={d.dateHeureNumerisation ?? NON_ECRIT} />
        <Ligne cle="Date de dernière modification" val={d.dateHeureModification ?? NON_ECRIT} />
        <Ligne
          cle="Dimensions de l’IFD0"
          val={d.largeurIfd0Px === null || d.hauteurIfd0Px === null
            ? NON_ECRIT : `${d.largeurIfd0Px} × ${d.hauteurIfd0Px} px`}
        />
        <Ligne
          cle="Résolution"
          val={d.resolutionX === null ? NON_ECRIT
            : `${fmtNb(d.resolutionX, 1)} × ${fmtNb(d.resolutionY, 1)} par ${lib.uniteResolution ?? '?'}`}
        />
        <Ligne
          cle="Densité en points par pouce"
          val={d.dpiX === null ? NON_ECRIT : `${fmtNb(d.dpiX, 1)} × ${fmtNb(d.dpiY, 1)} DPI`}
        />
        <Ligne cle="Espace colorimétrique" val={codeEt(d.espaceColorimetrique, lib.espaceColorimetrique)} />
        <Ligne cle="Mode d’exposition" val={codeEt(d.modeExposition, lib.modeExposition)} />
        <Ligne cle="Programme d’exposition" val={codeEt(d.programmeExposition, lib.programmeExposition)} />
        <Ligne cle="Balance des blancs" val={codeEt(d.balanceBlancs, lib.balanceBlancs)} />
        <Ligne cle="Type de scène" val={codeEt(d.typeScene, lib.typeScene)} />
        <Ligne cle="État du flash" val={codeEt(d.flash, lib.flash)} />
        <Ligne
          cle="Rapport de zoom numérique"
          val={d.rapportZoomNumerique === null ? NON_ECRIT
            : `${fmtNb(d.rapportZoomNumerique, 2)} — ${zoom ? 'zoom numérique appliqué' : 'non employé'}`}
        />
      </tbody>
    </table>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

export default function VerificateurIntegrite() {
  const [rapport, setRapport] = useState<RapportFichier | null>(null);
  const [provenance, setProvenance] = useState<Provenance | null>(null);
  const [urlMiniature, setUrlMiniature] = useState<string | null>(null);
  const [document_, setDocument] = useState<Record<string, unknown> | null>(null);
  const [empreinteMiniature, setEmpreinteMiniature] = useState<string | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [survol, setSurvol] = useState(false);
  const [copie, setCopie] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const traiter = useCallback(async (fichier: File) => {
    setErreur(null);
    setRapport(null);
    setProvenance(null);
    setDocument(null);
    setEmpreinteMiniature(null);
    setUrlMiniature((precedente) => {
      if (precedente) URL.revokeObjectURL(precedente);
      return null;
    });
    setCopie(false);
    if (fichier.size > TAILLE_MAX) {
      setErreur(
        `Fichier de ${fmtTaille(fichier.size)} : au-delà de ${fmtTaille(TAILLE_MAX)}, ` +
        'le calcul est refusé plutôt que de figer l’onglet. Un fichier plus gros se ' +
        'traite avec l’outil en ligne de commande du paquet Python.',
      );
      return;
    }
    setEnCours(true);
    try {
      const octets = new Uint8Array(await fichier.arrayBuffer());
      const r = await analyserFichier(fichier.name, fichier.type, octets);
      setRapport(r);
      setProvenance(analyserProvenance(octets));
      setDocument(await documentIngestion(octets, fichier.name));
      // La miniature est affichée depuis ses propres octets, jamais depuis
      // l'image principale redimensionnée : c'est justement leur écart qui a
      // valeur, et le montrer supposerait de les confondre.
      const m = r.exif?.miniature ?? null;
      if (m && m.estJpeg) {
        setUrlMiniature(URL.createObjectURL(new Blob([m.octets], { type: 'image/jpeg' })));
        setEmpreinteMiniature(await empreinteSha256(m.octets));
      }
    } catch (err) {
      setErreur(err instanceof Error ? err.message : String(err));
    } finally {
      setEnCours(false);
    }
  }, []);

  const onDrop = useCallback((ev: React.DragEvent) => {
    ev.preventDefault();
    setSurvol(false);
    const f = ev.dataTransfer.files?.[0];
    if (f) void traiter(f);
  }, [traiter]);

  const copier = useCallback(() => {
    if (!rapport) return;
    void navigator.clipboard.writeText(rapport.empreinte).then(() => {
      setCopie(true);
      setTimeout(() => setCopie(false), 1800);
    });
  }, [rapport]);

  const gps = rapport?.exif?.gps ?? null;

  return (
    <div style={{ maxWidth: 940, margin: '0 auto' }}>

      {/* ── Ce que l'outil fait, et où passe le fichier ── */}
      <div style={{
        background: dash.cyanSoft, border: `1px solid ${ACCENT}40`,
        borderRadius: 10, padding: '16px 20px', marginBottom: 20,
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 8,
        }}>Le fichier ne quitte pas votre machine</div>
        <p style={{ margin: '0 0 8px', fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          L’empreinte et les métadonnées sont calculées <strong>dans votre navigateur</strong>.
          Aucun octet n’est transmis, rien n’est stocké, rien n’est journalisé sur un serveur.
          Vous pouvez couper le réseau et l’outil fonctionnera toujours.
        </p>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          L’empreinte SHA-256 établit qu’un fichier <strong>n’a pas changé</strong> depuis que
          vous l’avez déclarée. Elle n’établit <strong>ni</strong> qu’il sort d’un appareil,{' '}
          <strong>ni</strong> la date de la prise de vue.
        </p>
      </div>

      {/* ── Dépôt ── */}
      <div
        onDragOver={(ev) => { ev.preventDefault(); setSurvol(true); }}
        onDragLeave={() => setSurvol(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(ev) => { if (ev.key === 'Enter' || ev.key === ' ') inputRef.current?.click(); }}
        style={{
          border: `2px dashed ${survol ? ACCENT : 'var(--border)'}`,
          background: survol ? dash.cyanSoft : 'var(--card)',
          borderRadius: 12, padding: '38px 24px', textAlign: 'center',
          cursor: 'pointer', marginBottom: 18, transition: 'all .15s',
        }}
      >
        <div style={{ fontSize: 30, marginBottom: 10 }}>🔒</div>
        <p style={{ margin: '0 0 6px', fontSize: 15, fontWeight: 600, color: 'var(--ink)' }}>
          {enCours ? 'Calcul en cours…' : 'Déposez un fichier, ou cliquez pour le choisir'}
        </p>
        <p style={{ margin: 0, fontSize: 12.5, color: 'var(--ink-muted)' }}>
          JPEG pour la lecture EXIF. N’importe quel fichier pour l’empreinte seule.
          Jusqu’à {fmtTaille(TAILLE_MAX)}.
        </p>
        <input
          ref={inputRef} type="file" style={{ display: 'none' }}
          onChange={(ev) => { const f = ev.target.files?.[0]; if (f) void traiter(f); ev.target.value = ''; }}
        />
      </div>

      {erreur && (
        <div style={{
          background: 'var(--card)', border: `1px solid ${dash.rose}60`,
          borderLeft: `3px solid ${dash.rose}`, borderRadius: 8,
          padding: '14px 18px', marginBottom: 16,
        }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
            <strong>Refusé.</strong> {erreur}
          </p>
        </div>
      )}

      {rapport && (
        <>
          <Bloc num="01" titre="Fichier et empreinte">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                <Ligne cle="Nom du fichier" val={rapport.nom} mono={false} />
                <Ligne cle="Taille" val={`${fmtTaille(rapport.tailleOctets)} — ${rapport.tailleOctets.toLocaleString('fr-FR')} octets`} />
                <Ligne cle="Type déclaré par le navigateur" val={rapport.typeDeclare} />
              </tbody>
            </table>
            <div style={{
              marginTop: 12, padding: '12px 14px', borderRadius: 8,
              background: dash.cyanSoft, border: `1px solid ${ACCENT}40`,
            }}>
              <div style={{
                fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700,
                letterSpacing: '0.1em', color: ACCENT, textTransform: 'uppercase',
                marginBottom: 6, display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', gap: 10,
              }}>
                <span>Empreinte SHA-256</span>
                <button
                  onClick={(ev) => { ev.stopPropagation(); copier(); }}
                  style={{
                    fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.06em',
                    padding: '3px 8px', cursor: 'pointer', background: 'var(--card)',
                    color: ACCENT, border: `1px solid ${ACCENT}60`, borderRadius: 4,
                  }}
                >{copie ? 'copiée' : 'copier'}</button>
              </div>
              <code style={{
                display: 'block', fontFamily: dash.fontMono, fontSize: 12.5,
                lineHeight: 1.65, wordBreak: 'break-all', color: dash.ink,
              }}>{rapport.empreinte}</code>
              {!empreinteValide(rapport.empreinte) && (
                <p style={{ margin: '6px 0 0', fontSize: 12, color: dash.rose }}>
                  Empreinte mal formée : ce résultat ne doit pas être utilisé.
                </p>
              )}
            </div>
            <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
              Pour que cette empreinte serve à quelque chose, elle doit être{' '}
              <strong>déposée le jour même auprès d’un tiers qui la date</strong> — horodatage
              électronique, publication datée, registre public. Sans cela, la date de calcul
              n’est que votre propre déclaration, et le protocole demande de le dire (§17.1).
            </p>
          </Bloc>

          {rapport.exif ? (
            <>
              <Bloc num="02" titre="Métadonnées EXIF lues">
                <BlocExif d={rapport.exif} />
                <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                  Un champ marqué <em>{NON_ECRIT}</em> n’a pas été trouvé dans le fichier. Ce
                  n’est pas la même chose qu’une valeur nulle, et ce n’est jamais complété par
                  une valeur plausible. Seuls les champs que le protocole utilise sont lus : ce
                  n’est pas un explorateur EXIF complet.
                </p>
              </Bloc>

              <Bloc num="03" titre="Champs d’ingestion">
                <BlocExifEtendu d={rapport.exif} />
                <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                  Les codes sont rendus avec leur libellé, jamais remplacés par lui : un libellé
                  est une interprétation, le code est ce que l’appareil a écrit. Un{' '}
                  <strong>logiciel déclaré</strong> n’établit pas qu’il y a eu retouche — un
                  simple convertisseur de format écrit son nom — et son absence n’établit pas
                  qu’il n’y en a pas eu.
                </p>
              </Bloc>

              <Bloc num="04" titre="Position enregistrée">
                {gps ? (
                  <>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <tbody>
                        <Ligne cle="Latitude" val={`${gps.latitudeDeg.toLocaleString('fr-FR', { minimumFractionDigits: 6, maximumFractionDigits: 6 })} °`} />
                        <Ligne cle="Longitude" val={`${gps.longitudeDeg.toLocaleString('fr-FR', { minimumFractionDigits: 6, maximumFractionDigits: 6 })} °`} />
                        <Ligne cle="Altitude" val={fmtNb(gps.altitudeM, 1, 'm')} />
                        <Ligne cle="Incertitude annoncée" val={fmtNb(gps.incertitudeM, 1, 'm')} />
                        <Ligne cle="Source" val={gps.source} mono={false} />
                      </tbody>
                    </table>
                    {gps.incertitudeM === null && (
                      <p style={{ margin: '10px 0 0', fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink-soft)' }}>
                        L’appareil n’a pas écrit <code style={{ fontSize: 11.5 }}>GPSHPositioningError</code> :
                        c’est le cas de la plupart des boîtiers. L’incertitude de position reste
                        donc <strong>{INDISPONIBLE}</strong>, et le protocole interdit de la
                        combler par une valeur supposée. Elle doit venir d’ailleurs — le relevé du
                        récepteur, ou un point géodésique.
                      </p>
                    )}
                    <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                      Cette position est celle que l’appareil a écrite. Elle n’est pas une position
                      certifiée au sens du protocole, qui demande un relevé satellitaire assorti de
                      son incertitude, ou un relèvement sur deux repères de position connue,
                      confirmé par une vue grand-angle.
                    </p>
                  </>
                ) : (
                  <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
                    Aucune position n’est enregistrée dans ce fichier. Ce n’est ni une anomalie ni
                    une preuve : beaucoup d’appareils n’écrivent pas de GPS, et beaucoup d’outils
                    de transfert le retirent. La position devra être établie autrement, et
                    déclarée comme telle.
                  </p>
                )}
              </Bloc>
            </>
          ) : (
            <Bloc num="02" titre="Métadonnées EXIF">
              <p style={{ margin: '0 0 10px', fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
                <strong>Aucune métadonnée EXIF n’a pu être lue.</strong> L’empreinte ci-dessus
                reste valide : les deux sont indépendantes.
              </p>
              <div style={{
                padding: '10px 12px', borderRadius: 6, background: 'var(--bg)',
                border: '1px solid var(--border)',
              }}>
                <div style={{
                  fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                  color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 5,
                }}>Motif rapporté par le lecteur</div>
                <code style={{ fontSize: 12.5, fontFamily: dash.fontMono, color: 'var(--ink)', lineHeight: 1.5 }}>
                  {rapport.motifExifAbsent ?? INDISPONIBLE}
                </code>
              </div>
              <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                Les causes courantes : le fichier n’est pas un JPEG, l’EXIF a été retiré par un
                service de messagerie ou de partage, ou le fichier est un format brut que ce
                lecteur ne couvre pas. Le motif exact est affiché ci-dessus plutôt que résumé.
              </p>
            </Bloc>
          )}

          {rapport.exif?.miniature && (
            <Bloc num="05" titre="Miniature intégrée">
              <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                {urlMiniature && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={urlMiniature}
                    alt="Miniature extraite de l’IFD1 du fichier"
                    style={{
                      maxWidth: 220, height: 'auto', borderRadius: 6,
                      border: '1px solid var(--border)',
                    }}
                  />
                )}
                <div style={{ flex: '1 1 260px', minWidth: 0 }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      <Ligne cle="Position dans le flux" val={`octet ${rapport.exif.miniature.offset}`} />
                      <Ligne cle="Taille" val={fmtTaille(rapport.exif.miniature.longueur)} />
                      <Ligne cle="Format" val={rapport.exif.miniature.estJpeg ? 'JPEG' : 'non reconnu'} />
                      <Ligne cle="Code de compression" val={fmtNb(rapport.exif.miniature.compression, 0)} />
                    </tbody>
                  </table>
                  {empreinteMiniature && (
                    <div style={{
                      marginTop: 10, padding: '10px 12px', borderRadius: 6,
                      background: 'var(--bg)', border: '1px solid var(--border)',
                    }}>
                      <div style={{
                        fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                        color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 5,
                      }}>SHA-256 de la miniature seule</div>
                      <code style={{
                        fontSize: 11.5, fontFamily: dash.fontMono, color: 'var(--ink)',
                        lineHeight: 1.5, wordBreak: 'break-all',
                      }}>{empreinteMiniature}</code>
                    </div>
                  )}
                </div>
              </div>
              <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                La miniature est affichée depuis <strong>ses propres octets</strong>, jamais
                depuis l’image principale réduite : c’est leur écart qui aurait valeur.
                Comparez-la à l’original. Un <strong>écart</strong> est un fait — la vignette
                n’a pas été régénérée après une retouche. Une <strong>concordance</strong>
                n’établit rien : tout éditeur qui régénère la vignette efface la trace.
              </p>
            </Bloc>
          )}

          {provenance && (
            <Bloc num="06" titre="Provenance déclarée — C2PA">
              {provenance.c2pa.present ? (
                <>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      <Ligne cle="Conteneur" val={provenance.c2pa.conteneur ?? INDISPONIBLE} />
                      <Ligne cle="Taille du manifeste" val={fmtTaille(provenance.c2pa.octets)} />
                      <Ligne cle="Nombre de manifestes" val={String(provenance.c2pa.manifestes.length)} />
                      <Ligne cle="Signature vérifiée" val="non — voir ci-dessous" mono={false} />
                    </tbody>
                  </table>
                  {provenance.c2pa.manifestes.map((m) => (
                    <div key={m.label} style={{
                      marginTop: 12, padding: '12px 14px', borderRadius: 6,
                      background: 'var(--bg)', border: '1px solid var(--border)',
                    }}>
                      <div style={{
                        fontSize: 11, fontFamily: dash.fontMono, color: 'var(--ink-soft)',
                        wordBreak: 'break-all', marginBottom: 8,
                      }}>{m.label}</div>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <tbody>
                          <Ligne cle="Générateur déclaré" val={m.generateur ?? NON_ECRIT} mono={false} />
                          <Ligne cle="Algorithme déclaré" val={m.algorithmeSignature ?? NON_ECRIT} />
                          <Ligne cle="Bloc de signature" val={m.signaturePresente ? 'présent' : 'absent'} mono={false} />
                          <Ligne cle="Assertions" val={Object.keys(m.assertions).join(', ') || '—'} mono={false} />
                        </tbody>
                      </table>
                      {m.actions.length > 0 && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{
                            fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                            color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 6,
                          }}>Actions de retouche déclarées</div>
                          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, lineHeight: 1.7, color: 'var(--ink)' }}>
                            {m.actions.map((a, i) => (
                              <li key={i}>
                                <code style={{ fontSize: 11.5 }}>{String(a.action ?? '?')}</code>
                                {a.softwareAgent ? ` — ${String(a.softwareAgent)}` : ''}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </>
              ) : (
                <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
                  <strong>Aucun manifeste C2PA dans ce fichier.</strong> Ce n’est ni une anomalie
                  ni un indice : la quasi-totalité des appareils n’en écrivent pas, et la plupart
                  des retouches et des partages effacent ceux qui existaient.
                </p>
              )}
              <div style={{
                marginTop: 12, padding: '12px 14px', borderRadius: 6,
                background: dash.roseSoft, border: `1px solid ${dash.rose}40`,
              }}>
                <div style={{
                  fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
                  color: dash.rose, textTransform: 'uppercase', marginBottom: 6,
                }}>Ce que cette lecture n’établit pas</div>
                <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.65, color: dash.ink }}>
                  {AVERTISSEMENT_C2PA}
                </p>
              </div>
            </Bloc>
          )}

          {provenance && (provenance.xmp.length > 0 || provenance.iptc.length > 0) && (
            <Bloc num="07" titre="XMP et IPTC">
              {provenance.xmp.map((b, i) => (
                <div key={i} style={{ marginBottom: 14 }}>
                  <div style={{
                    fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                    color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 6,
                  }}>{b.conteneur} — {fmtTaille(b.octets)}</div>
                  {Object.keys(b.champs).length > 0 ? (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <tbody>
                        {Object.entries(b.champs).map(([nom, val]) => (
                          <Ligne key={nom} cle={nom} val={val} mono={false} />
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p style={{ margin: 0, fontSize: 12.5, color: 'var(--ink-muted)' }}>
                      Paquet présent, aucun des champs relevés par cet outil n’y figure.
                    </p>
                  )}
                </div>
              ))}
              {provenance.iptc.length > 0 && (
                <>
                  <div style={{
                    fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                    color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 6,
                  }}>IPTC-IIM (APP13)</div>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      {provenance.iptc.map((e, i) => (
                        <Ligne key={i} cle={e.libelle} val={e.valeur} mono={false} />
                      ))}
                    </tbody>
                  </table>
                </>
              )}
              <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                XMP et IPTC sont des champs <strong>rédactionnels</strong> : n’importe qui peut
                les écrire, les modifier ou les effacer avec un éditeur de texte. Ils documentent
                une intention déclarée, ils n’attestent de rien.
              </p>
            </Bloc>
          )}

          {provenance && provenance.chaines.length > 0 && (
            <Bloc num="08" titre="Chaînes lisibles des en-têtes">
              {provenance.marqueursLogiciels.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{
                    fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em',
                    color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 6,
                  }}>Marqueurs logiciels reconnus</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {provenance.marqueursLogiciels.map((m) => (
                      <span key={m} style={{
                        fontSize: 11.5, fontFamily: dash.fontMono, padding: '3px 9px',
                        borderRadius: 4, background: dash.saffronSoft,
                        border: `1px solid ${dash.saffron}50`, color: dash.ink,
                      }}>{m}</span>
                    ))}
                  </div>
                </div>
              )}
              <details>
                <summary style={{ cursor: 'pointer', fontSize: 12.5, color: 'var(--ink-soft)' }}>
                  {provenance.chaines.length} chaîne{provenance.chaines.length > 1 ? 's' : ''} relevée
                  {provenance.chaines.length > 1 ? 's' : ''} avant le début des données d’image
                </summary>
                <div style={{
                  marginTop: 10, maxHeight: 320, overflowY: 'auto', borderRadius: 6,
                  border: '1px solid var(--border)', background: 'var(--bg)', padding: '8px 10px',
                }}>
                  {provenance.chaines.map((c, i) => (
                    <div key={i} style={{
                      fontFamily: dash.fontMono, fontSize: 11.5, lineHeight: 1.6,
                      color: c.marqueur ? dash.ink : 'var(--ink-muted)',
                      wordBreak: 'break-all', padding: '2px 0',
                    }}>
                      <span style={{ color: 'var(--ink-ghost)' }}>
                        {String(c.offset).padStart(6, '0')} {c.encodage === 'UTF-16LE' ? 'u16' : 'asc'}{' '}
                      </span>
                      {c.texte}
                    </div>
                  ))}
                </div>
              </details>
              <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                Le relevé s’arrête au début des données d’image : au-delà, toute suite « lisible »
                est un artefact de compression, pas un texte. Un marqueur reconnu n’établit{' '}
                <strong>pas</strong> qu’il y a eu retouche — un convertisseur de format écrit son
                nom sans toucher au contenu visible — et son absence n’établit pas le contraire.
              </p>
            </Bloc>
          )}

          {document_ && (
            <Bloc num="09" titre="Synthèse d’ingestion">
              <p style={{ margin: '0 0 12px', fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
                Tout ce que le fichier déclare, en un document JSON destiné au dossier
                d’audit : <code style={{ fontSize: 12 }}>file_info</code>,{' '}
                <code style={{ fontSize: 12 }}>exif</code>,{' '}
                <code style={{ fontSize: 12 }}>c2pa</code>,{' '}
                <code style={{ fontSize: 12 }}>thumbnail</code>, plus XMP, IPTC et les
                marqueurs de chaînes.
              </p>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                <button
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(document_, null, 2)],
                      { type: 'application/json' });
                    const a = window.document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = `${rapport.nom.replace(/\.[^.]+$/, '')}-ingestion.json`;
                    a.click();
                    URL.revokeObjectURL(a.href);
                  }}
                  style={{
                    padding: '8px 14px', fontSize: 12, fontWeight: 600, cursor: 'pointer',
                    borderRadius: 4, border: `1px solid ${ACCENT}`,
                    background: ACCENT + '14', color: ACCENT,
                  }}
                >Télécharger la synthèse (JSON)</button>
              </div>
              <details>
                <summary style={{ cursor: 'pointer', fontSize: 12.5, color: 'var(--ink-soft)' }}>
                  Voir le document
                </summary>
                <pre style={{
                  marginTop: 10, maxHeight: 380, overflow: 'auto', borderRadius: 6,
                  border: '1px solid var(--border)', background: 'var(--bg)',
                  padding: '10px 12px', fontSize: 11.5, lineHeight: 1.55,
                  fontFamily: dash.fontMono, color: 'var(--ink)',
                }}>{JSON.stringify(document_, null, 2)}</pre>
              </details>
              <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
                Quatre points du schéma d’origine sont rendus autrement, et le document le
                montre : l’horodatage ne porte un fuseau que si l’appareil a écrit{' '}
                <code style={{ fontSize: 11.5 }}>OffsetTimeOriginal</code> — sinon{' '}
                <code style={{ fontSize: 11.5 }}>offset_declare</code> vaut faux et l’heure
                reste locale ; <code style={{ fontSize: 11.5 }}>dpi</code> n’est un scalaire
                que si les deux axes coïncident ; <code style={{ fontSize: 11.5 }}>camera</code>{' '}
                concatène, mais <code style={{ fontSize: 11.5 }}>make</code> et{' '}
                <code style={{ fontSize: 11.5 }}>model</code> restent séparés ; et{' '}
                <code style={{ fontSize: 11.5 }}>c2pa.signature</code> porte l’identité{' '}
                <strong>déclarée</strong>, jamais vérifiée.
              </p>
            </Bloc>
          )}

          <div style={{
            background: 'var(--card)', border: '1px solid var(--border)',
            borderLeft: `3px solid ${dash.saffron}`, borderRadius: 8,
            padding: '14px 18px', marginBottom: 16,
          }}>
            <p style={{ margin: '0 0 8px', fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
              <strong>Ce que cet outil n’établit pas.</strong> Les métadonnées EXIF s’écrivent :
              elles documentent la chaîne de traitement, elles ne prouvent pas l’origine d’un
              fichier. L’authenticité repose sur des concordances externes que le fichier ne peut
              pas fabriquer — position du Soleil déduite des ombres, hauteur de marée, registre
              horodaté d’un navire, météo observée, présence des repères attendus dans le champ.
            </p>
            <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
              Cet outil ne cherche pas non plus de trace de retouche. La détection de bruit de
              capteur et l’analyse du niveau d’erreur de compression existent dans le paquet de
              référence, mais elles sont hors du périmètre du protocole et ne concluent jamais
              seules : elles ne sont pas exposées ici.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
