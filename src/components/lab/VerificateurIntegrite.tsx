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
  empreinteValide,
} from '@/lib/preuve-image/noyau';

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

// ─────────────────────────────────────────────────────────────────────────────

export default function VerificateurIntegrite() {
  const [rapport, setRapport] = useState<RapportFichier | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [survol, setSurvol] = useState(false);
  const [copie, setCopie] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const traiter = useCallback(async (fichier: File) => {
    setErreur(null);
    setRapport(null);
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
      setRapport(await analyserFichier(fichier.name, fichier.type, octets));
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

              <Bloc num="03" titre="Position enregistrée">
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
