'use client';

/**
 * FicheTerrainPanneau — La fiche protocole terrain, à l'écran et sur papier.
 *
 * CE QUE CE COMPOSANT FAIT, ET CE QU'IL NE CALCULE PAS
 * ───────────────────────────────────────────────────
 * Il n'établit rien. Tout le contenu vient de `construireFiche`, port épinglé
 * du paquet Python : les chiffres, les motifs, l'ordre des blocs et jusqu'aux
 * coupures de ligne du rendu texte. Ce fichier ne fait que présenter, et c'est
 * délibéré — un composant d'interface qui calculerait échapperait aux vecteurs
 * d'or.
 *
 * TROIS SORTIES, ET POURQUOI PAS DE BIBLIOTHÈQUE PDF
 * ──────────────────────────────────────────────────
 * Le texte pur se télécharge, la page s'imprime, et l'impression du navigateur
 * sait déjà écrire un PDF (« Enregistrer au format PDF » dans la boîte
 * d'impression). Ajouter un générateur de PDF embarqué pèserait quelques
 * centaines de kilooctets, ne saurait pas mieux couper les pages, et
 * remplacerait des polices système par des polices incorporées. Le bouton
 * s'appelle donc « Imprimer / PDF » : il ne promet rien qu'il ne fasse.
 *
 * L'IMPRESSION NE SORT QUE LA FICHE
 * ─────────────────────────────────
 * Un `window.print()` sur cette page imprimerait l'en-tête du site, le menu et
 * le simulateur entier. Le composant pose donc un attribut sur `<body>` le
 * temps de l'impression, et `globals.css` masque tout le reste sous
 * `@media print`. L'attribut est retiré dans un `finally` : laissé en place, il
 * rendrait invisible toute impression ultérieure de n'importe quelle page.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import {
  MILIEUX,
  MOTIF_AVEUGLE,
  type FicheTerrain,
  construireFiche,
  nomFichier,
  rendreTxt,
} from '@/lib/visee-optique/fiche-terrain';
import type { Simulation } from './ResultatVisee';

const ACCENT = dash.opal;

/** L'ordre d'affichage des milieux. Le plus favorable d'abord. */
const ORDRE_MILIEUX = ['lac', 'mer', 'terre'] as const;

export default function FicheTerrainPanneau({ sim }: { sim: Simulation }) {
  const [milieu, setMilieu] = useState<string>('mer');
  const [ouvert, setOuvert] = useState(false);
  // Le scellé est REPLIÉ par défaut, même à l'écran : la fiche existe pour que
  // la prédiction ne soit pas lue avant la prise de vue, et l'afficher
  // d'emblée annulerait le seul dispositif qui la protège.
  const [scelleOuvert, setScelleOuvert] = useState(false);
  const [horodatage, setHorodatage] = useState<string | null>(null);
  const zone = useRef<HTMLDivElement>(null);

  // L'horodatage est pris UNE FOIS, à l'ouverture, puis figé. Le relire à
  // chaque rendu ferait varier la fiche entre l'écran et le fichier
  // téléchargé, et un dépôt dont l'heure bouge ne dépose rien.
  useEffect(() => {
    if (ouvert && horodatage === null) {
      setHorodatage(new Date().toISOString().replace(/\.\d+Z$/, 'Z'));
    }
  }, [ouvert, horodatage]);

  const fiche = useMemo<FicheTerrain | null>(() => {
    if (!ouvert || horodatage === null) return null;
    return construireFiche({
      milieu,
      horodatage,
      obsLatitude: sim.positionObs.latitude,
      obsLongitude: sim.positionObs.longitude,
      obsLibelle: sim.positionObs.libelle ?? null,
      cibleLatitude: sim.positionCible.latitude,
      cibleLongitude: sim.positionCible.longitude,
      cibleLibelle: sim.positionCible.libelle ?? null,
      distanceM: sim.D,
      azimutDeg: sim.azimutDeg,
      hauteurObservateurM: sim.h,
      hauteurCibleM: sim.cible.H,
      masqueeEnveloppeMinM: sim.masqueeEnveloppeMinM,
      masqueeEnveloppeMaxM: sim.masqueeEnveloppeMaxM,
      kEmploye: sim.kEmploye,
      kPersonnalise: sim.kPersonnalise,
      verdict: sim.verdict,
    });
  }, [ouvert, horodatage, milieu, sim]);

  const telecharger = useCallback(() => {
    if (!fiche) return;
    // Le BOM UTF-8 est délibéré : sans lui, le Bloc-notes de Windows lit le
    // fichier en ANSI et rend « rÃ©fraction ». C'est le format qui doit
    // survivre à tout, jusque-là compris.
    const blob = new Blob(['﻿', rendreTxt(fiche)],
      { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nomFichier(fiche, sim.D);
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }, [fiche, sim.D]);

  const imprimer = useCallback(() => {
    if (!fiche) return;
    document.body.setAttribute('data-impression', 'fiche-terrain');
    try {
      window.print();
    } finally {
      // Dans un `finally` : un attribut laissé en place rendrait invisible
      // toute impression ultérieure, de n'importe quelle page du site.
      document.body.removeAttribute('data-impression');
    }
  }, [fiche]);

  if (!ouvert) {
    return (
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderLeft: `3px solid ${ACCENT}`, borderRadius: 10,
        padding: '16px 18px', marginTop: 18,
      }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--ink)', marginBottom: 6 }}>
          Emporter cette visée sur le terrain
        </div>
        <p style={{ margin: '0 0 13px', fontSize: 13, lineHeight: 1.65, color: 'var(--ink-soft)' }}>
          Une fiche d’une page, tirée de cette simulation : ce qu’il faut mesurer
          sur place, pourquoi chaque mesure est demandée, et comment cadrer. La
          prédiction est reléguée en dernier bloc, à ne lire qu’après la prise de
          vue — sinon l’œil trouve la valeur qu’on lui a annoncée.
        </p>
        <button
          onClick={() => setOuvert(true)}
          style={{
            padding: '11px 22px', fontSize: 14, fontWeight: 700, minHeight: 44,
            cursor: 'pointer', background: ACCENT, color: '#08131b',
            border: 'none', borderRadius: 8,
          }}
        >Générer la fiche protocole terrain</button>
      </div>
    );
  }

  return (
    <div style={{ marginTop: 18 }}>
      {/* ── Les réglages, hors impression ── */}
      <div className="tei-fiche-reglages" style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: '10px 10px 0 0', borderBottom: 'none', padding: '14px 18px',
      }}>
        <div style={{
          fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700,
          letterSpacing: '0.1em', color: ACCENT, textTransform: 'uppercase',
          marginBottom: 11,
        }}>Fiche protocole terrain</div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', marginBottom: 10 }}>
          <span style={{ fontSize: 13, color: 'var(--ink-soft)' }}>Milieu :</span>
          {ORDRE_MILIEUX.map((m) => (
            <button
              key={m}
              onClick={() => setMilieu(m)}
              aria-pressed={milieu === m}
              style={{
                padding: '8px 16px', fontSize: 13.5, minHeight: 40, cursor: 'pointer',
                fontWeight: milieu === m ? 700 : 500,
                background: milieu === m ? ACCENT : 'transparent',
                color: milieu === m ? '#08131b' : 'var(--ink)',
                border: `1px solid ${milieu === m ? ACCENT : 'var(--border)'}`,
                borderRadius: 6,
              }}
            >{MILIEUX[m].nom}</button>
          ))}
        </div>
        <p style={{ margin: '0 0 12px', fontSize: 11.5, lineHeight: 1.5, color: 'var(--ink-muted)' }}>
          Le milieu ne change aucun chiffre : il fixe le niveau auquel les
          hauteurs sont comptées, les grandeurs à relever, et ce que
          l’observation pourra établir.
        </p>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button
            onClick={telecharger}
            style={{
              padding: '10px 18px', fontSize: 13.5, fontWeight: 700, minHeight: 42,
              cursor: 'pointer', background: ACCENT, color: '#08131b',
              border: 'none', borderRadius: 6,
            }}
          >Télécharger en texte (.txt)</button>
          <button
            onClick={imprimer}
            style={{
              padding: '10px 18px', fontSize: 13.5, fontWeight: 700, minHeight: 42,
              cursor: 'pointer', background: 'transparent', color: 'var(--ink)',
              border: '1px solid var(--border)', borderRadius: 6,
            }}
          >Imprimer / PDF</button>
          <button
            onClick={() => setOuvert(false)}
            style={{
              padding: '10px 16px', fontSize: 13, minHeight: 42, cursor: 'pointer',
              background: 'transparent', color: 'var(--ink-muted)',
              border: '1px solid var(--border)', borderRadius: 6,
            }}
          >Fermer</button>
        </div>
      </div>

      {/* ── La fiche elle-même : c'est CE bloc que l'impression conserve ── */}
      <div ref={zone} className="tei-fiche-terrain" style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: '0 0 10px 10px', padding: '20px 22px',
      }}>
        {fiche === null ? (
          <p style={{ margin: 0, fontSize: 13, color: 'var(--ink-muted)' }}>
            Préparation de la fiche…
          </p>
        ) : (
          <>
            <h3 style={{
              margin: '0 0 3px', fontSize: 19, fontWeight: 800, color: 'var(--ink)',
              letterSpacing: '-0.01em',
            }}>{fiche.titre}</h3>
            <p style={{ margin: '0 0 3px', fontSize: 13.5, color: 'var(--ink-soft)' }}>
              {fiche.sousTitre}
            </p>
            <p style={{ margin: '0 0 18px', fontSize: 11.5, color: 'var(--ink-muted)', fontFamily: dash.fontMono }}>
              Simulateur de Visée · générée le {fiche.horodatage}
            </p>

            {fiche.sections.map((s) => (
              <section key={s.numero} style={{ marginBottom: 22 }}>
                <h4 style={{
                  margin: '0 0 10px', fontSize: 14.5, fontWeight: 750, color: 'var(--ink)',
                  display: 'flex', alignItems: 'baseline', gap: 8,
                }}>
                  <span style={{
                    fontFamily: dash.fontMono, fontSize: 12, fontWeight: 700,
                    color: s.sousScelle ? dash.rose : ACCENT,
                  }}>{s.numero}</span>
                  {s.titre}
                </h4>

                {s.sousScelle && (
                  <div style={{
                    background: 'var(--bg)', borderLeft: `3px solid ${dash.rose}`,
                    borderRadius: 6, padding: '11px 14px', marginBottom: 12,
                  }}>
                    <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink)' }}>
                      {MOTIF_AVEUGLE}
                    </p>
                  </div>
                )}

                {/* Le contenu du scellé est masqué à l'écran jusqu'à un clic
                    explicite, mais TOUJOURS présent à l'impression : la feuille
                    qu'on emporte doit le porter, pour être repliée ou découpée. */}
                {s.sousScelle && !scelleOuvert && (
                  <button
                    className="tei-fiche-reglages"
                    onClick={() => setScelleOuvert(true)}
                    style={{
                      padding: '9px 16px', fontSize: 13, minHeight: 40, cursor: 'pointer',
                      background: 'transparent', color: dash.rose,
                      border: `1px solid ${dash.rose}60`, borderRadius: 6,
                    }}
                  >Afficher la prédiction (après la prise de vue)</button>
                )}

                <div className={s.sousScelle && !scelleOuvert ? 'tei-fiche-scelle-cache' : undefined}>
                  {s.releves.length > 0 && (
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                      <tbody>
                        {s.releves.map(([cle, valeur]) => (
                          <tr key={cle}>
                            <td style={{
                              padding: '6px 12px 6px 0', color: 'var(--ink-muted)',
                              verticalAlign: 'top', borderBottom: '1px solid var(--border)',
                              width: '42%',
                            }}>{cle}</td>
                            <td style={{
                              padding: '6px 0', color: 'var(--ink)', verticalAlign: 'top',
                              borderBottom: '1px solid var(--border)',
                            }}>{valeur}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}

                  {s.champs.map((c) => (
                    <div key={c.libelle} style={{
                      borderBottom: '1px solid var(--border)', padding: '11px 0',
                    }}>
                      <div style={{ display: 'flex', gap: 9, alignItems: 'baseline' }}>
                        <span aria-hidden style={{
                          fontFamily: dash.fontMono, fontSize: 13, color: ACCENT,
                        }}>{c.obligatoire ? '[ ]' : '[~]'}</span>
                        <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--ink)' }}>
                          {c.libelle}
                          {c.unite && (
                            <span style={{ color: 'var(--ink-muted)', fontWeight: 400 }}>
                              {' '}({c.unite})
                            </span>
                          )}
                          {!c.obligatoire && (
                            <span style={{ color: 'var(--ink-muted)', fontWeight: 400, fontSize: 12 }}>
                              {' '}— si possible
                            </span>
                          )}
                        </span>
                      </div>
                      {/* La ligne à remplir : c'est une fiche, elle s'écrit. */}
                      <div aria-hidden style={{
                        margin: '8px 0 7px 30px', height: 20,
                        borderBottom: '1px dashed var(--border)',
                      }} />
                      <p style={{
                        margin: '0 0 0 30px', fontSize: 12, lineHeight: 1.6,
                        color: 'var(--ink-soft)',
                      }}>{c.pourquoi}</p>
                    </div>
                  ))}

                  {s.consignes.length > 0 && (
                    <ol style={{ margin: 0, paddingLeft: 22 }}>
                      {s.consignes.map((texte, i) => (
                        <li key={i} style={{
                          fontSize: 13, lineHeight: 1.65, color: 'var(--ink)',
                          marginBottom: 9, paddingLeft: 4,
                        }}>{texte}</li>
                      ))}
                    </ol>
                  )}

                  {s.reserves
                    // L'avertissement d'aveuglement est déjà rendu en tête du
                    // bloc : le répéter ici le ferait paraître deux fois.
                    .filter((t) => !(s.sousScelle && t === MOTIF_AVEUGLE))
                    .map((texte, i) => (
                      <p key={i} style={{
                        margin: '10px 0 0', padding: '10px 13px', borderRadius: 6,
                        background: 'var(--bg)',
                        borderLeft: `3px solid ${s.sousScelle ? dash.rose : dash.saffron}`,
                        fontSize: 12.5, lineHeight: 1.65, color: 'var(--ink)',
                      }}>{texte}</p>
                    ))}
                </div>
              </section>
            ))}

            <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14 }}>
              <h4 style={{
                margin: '0 0 10px', fontSize: 13.5, fontWeight: 750, color: 'var(--ink)',
              }}>Ce que cette fiche ne demande pas, et pourquoi</h4>
              {fiche.champsEcartes.map(([titre, motif]) => (
                <p key={titre} style={{
                  margin: '0 0 9px', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-soft)',
                }}>
                  <strong style={{ color: 'var(--ink)' }}>{titre}.</strong> {motif}
                </p>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
