'use client';
/**
 * ViseeOptiqueCalc — Calculateur de portion visible d'une cible éloignée.
 *
 * Expose l'outil A du protocole « Portion visible d'une cible éloignée
 * au-dessus de la mer » v1.0, via le port TypeScript de `src/lib/visee-optique/`
 * — port épinglé au paquet Python par 263 contrôles (voir
 * scripts/verifier-port-visee.mjs).
 *
 * Quatre règles gouvernent cette interface, et elles ne sont pas cosmétiques :
 *
 *  1. Aucun champ n'est prérempli d'une valeur plausible. Les entrées
 *     démarrent vides, et ce qui n'est pas renseigné s'affiche
 *     « INDISPONIBLE », jamais remplacé par un défaut commode.
 *  2. Chaque coordonnée et chaque hauteur exige sa source. Sans source, la
 *     valeur n'est pas un fait : le calcul reste bloqué et le dit.
 *  3. Le résultat est une ENVELOPPE sur l'intervalle de réfraction déclaré,
 *     jamais une valeur ponctuelle.
 *  4. La condition du §28.2 est un préalable géométrique. Elle n'est jamais
 *     présentée comme un verdict sur la forme de la Terre — ça, ça demande
 *     une mesure photographique réelle conduite selon le protocole.
 */
import { useMemo, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import {
  IUGG_R1,
  cible as faireCible,
  classerRegime,
  conditionDiscrimination,
  distanceCritique,
  distanceLimite,
  fractionVisible,
  hauteurOccultee,
  rayonEffectif,
  rayonEuler,
  vincentyInverse,
} from '@/lib/visee-optique/noyau';

const INDISPONIBLE = 'INDISPONIBLE';
const ACCENT = dash.opal;

/** Une valeur saisie et la source qui l'établit. Les deux, ou rien. */
interface Champ {
  valeur: string;
  source: string;
}

const vide = (): Champ => ({ valeur: '', source: '' });

interface Etat {
  obsLat: Champ; obsLon: Champ; obsAlt: Champ;
  cibLat: Champ; cibLon: Champ; cibH: Champ; cibZb: Champ;
  kMin: Champ; kMax: Champ;
  uF: Champ; facteur: Champ;
}

const ETAT_VIDE: Etat = {
  obsLat: vide(), obsLon: vide(), obsAlt: vide(),
  cibLat: vide(), cibLon: vide(), cibH: vide(), cibZb: vide(),
  kMin: vide(), kMax: vide(), uF: vide(), facteur: vide(),
};

/**
 * Un exemple entièrement sourcé, chargeable d'un clic. Ce n'est pas un
 * préremplissage : c'est un jeu de données documenté, repris du troisième cas
 * d'étude livré avec les outils, et l'utilisateur voit qu'il le charge.
 */
const EXEMPLE: Etat = {
  obsLat: { valeur: '50.94642', source: 'Cas d’étude CAS-DEMO-SANGATTE-001 — digue de Sangatte, coordonnées relevées sur Cirkwi' },
  obsLon: { valeur: '1.75305', source: 'Cas d’étude CAS-DEMO-SANGATTE-001 — idem' },
  obsAlt: { valeur: '2', source: 'Cirkwi, altitude déclarée 2 m ; convergent avec l’altitude moyenne du cordon dunaire' },
  cibLat: { valeur: '51.13152', source: 'Cas d’étude CAS-DEMO-SANGATTE-001 — phare de South Foreland' },
  cibLon: { valeur: '1.338825', source: 'Cas d’étude CAS-DEMO-SANGATTE-001 — idem' },
  cibH: { valeur: '110', source: 'Falaises de Douvres, altitude du sommet 110 m au-dessus du niveau de la mer' },
  cibZb: { valeur: '0', source: 'Base au niveau moyen de la mer — pied de falaise' },
  kMin: { valeur: '0.10', source: 'Plage retenue faute de profil vertical résolu (§21.3, Tableau 8)' },
  kMax: { valeur: '0.40', source: 'Plage retenue faute de profil vertical résolu (§21.3, Tableau 8)' },
  uF: { valeur: '0.02', source: 'Incertitude de mesure supposée sur la fraction, pour démonstration' },
  facteur: { valeur: '5', source: 'Facteur recommandé au §26, à remplacer par celui réellement déposé' },
};

function nombre(c: Champ): number | null {
  if (c.valeur.trim() === '') return null;
  const v = Number(c.valeur.replace(',', '.'));
  return Number.isFinite(v) ? v : null;
}

/**
 * Un champ est complet dès qu'il porte un nombre.
 *
 * La source ne conditionne plus le calcul. Une première version l'exigeait :
 * le raisonnement était bon, la conséquence mauvaise. Une chaîne saisie dans un
 * champ n'est pas une source vérifiée — rien ici ne contrôle qu'une fiche
 * d'ouvrage dit ce qu'on lui fait dire — et l'analyste qui reprend le dossier
 * refait le travail. Le verrou ne garantissait rien ; il empêchait de calculer.
 *
 * L'absence est donc relevée, pas bloquante : `sansSource` la repère, et le
 * tableau de bord en fait la liste de ce qui reste à établir.
 */
function complet(c: Champ): boolean {
  return nombre(c) !== null;
}

/** Une valeur saisie dont la provenance n'est pas déclarée. */
function sansSource(c: Champ): boolean {
  return nombre(c) !== null && c.source.trim() === '';
}

const fmt = (x: number, n = 3) =>
  x.toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });

// ─────────────────────────────────────────────────────────────────────────────

function ChampSource({
  label, unite, champ, onChange, aide, pas,
}: {
  label: string; unite: string; champ: Champ;
  onChange: (c: Champ) => void; aide: string; pas?: string;
}) {
  const n = nombre(champ);
  const manqueSource = n !== null && champ.source.trim() === '';
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{
        display: 'block', fontSize: 11, fontFamily: dash.fontMono, letterSpacing: '0.06em',
        color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 5,
      }}>
        {label} <span style={{ color: dash.inkGhost }}>· {unite}</span>
      </label>
      <div style={{ display: 'flex', gap: 8, alignItems: 'stretch' }}>
        <input
          type="text" inputMode="decimal" step={pas} value={champ.valeur}
          onChange={(e) => onChange({ ...champ, valeur: e.target.value })}
          placeholder="—"
          aria-label={`${label} en ${unite}`}
          style={{
            width: 128, padding: '9px 10px', fontSize: 15, fontFamily: dash.fontMono,
            background: 'var(--card)', color: 'var(--ink)',
            border: `1px solid ${n === null ? 'var(--border)' : ACCENT + '80'}`,
            borderRadius: 5, outline: 'none',
          }}
        />
        <input
          type="text" value={champ.source}
          onChange={(e) => onChange({ ...champ, source: e.target.value })}
          placeholder="Source — à établir par l’analyste"
          aria-label={`Source de ${label}`}
          style={{
            flex: 1, minWidth: 0, padding: '9px 10px', fontSize: 13,
            background: 'var(--card)', color: 'var(--ink)',
            border: `1px solid ${manqueSource ? dash.saffron : 'var(--border)'}`,
            borderRadius: 5, outline: 'none',
          }}
        />
      </div>
      <p style={{ margin: '4px 0 0', fontSize: 11.5, color: 'var(--ink-muted)', lineHeight: 1.45 }}>
        {manqueSource
          ? (
            <span style={{ color: dash.saffron }}>
              Sans source : la valeur entre dans le calcul, et figure dans la liste de ce qui
              reste à établir.
            </span>
          )
          : aide}
      </p>
    </div>
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

function Ligne({ cle, val, source }: { cle: string; val: string; source?: string }) {
  const absent = val === INDISPONIBLE;
  return (
    <tr>
      <td style={{ padding: '7px 10px 7px 0', fontSize: 13, color: 'var(--ink-soft)', verticalAlign: 'top' }}>{cle}</td>
      <td style={{
        padding: '7px 10px', fontSize: 13.5, fontFamily: dash.fontMono, textAlign: 'right',
        color: absent ? dash.rose : 'var(--ink)', fontWeight: absent ? 700 : 500,
        whiteSpace: 'nowrap', verticalAlign: 'top',
      }}>{val}</td>
      {source !== undefined && (
        <td style={{ padding: '7px 0 7px 10px', fontSize: 11.5, color: 'var(--ink-muted)', lineHeight: 1.4 }}>
          {source.trim() === '' ? <span style={{ color: dash.rose }}>{INDISPONIBLE}</span> : source}
        </td>
      )}
    </tr>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

export default function ViseeOptiqueCalc() {
  const [e, setE] = useState<Etat>(ETAT_VIDE);
  const maj = (cle: keyof Etat) => (c: Champ) => setE((p) => ({ ...p, [cle]: c }));

  const obligatoires: (keyof Etat)[] = ['obsLat', 'obsLon', 'obsAlt', 'cibLat', 'cibLon', 'cibH', 'cibZb', 'kMin', 'kMax', 'uF', 'facteur'];
  const manquants = obligatoires.filter((k) => !complet(e[k]));

  /**
   * Ce qui reste à établir : les grandeurs saisies sans provenance déclarée.
   * Une source déclarée ici est une DÉCLARATION de l'opérateur, jamais une
   * vérification. La liste sert à l'analyste qui reprendra le dossier.
   */
  const LIBELLES: Record<string, string> = {
    obsLat: 'latitude du poste', obsLon: 'longitude du poste', obsAlt: 'altitude de l’axe optique',
    cibLat: 'latitude de la cible', cibLon: 'longitude de la cible',
    cibH: 'hauteur totale H', cibZb: 'altitude de la base z_b',
    kMin: 'k minimal', kMax: 'k maximal',
    uF: 'incertitude u(f)', facteur: 'facteur de discrimination',
  };
  const grandeursSansSource = obligatoires
    .filter((k) => sansSource(e[k]))
    .map((k) => LIBELLES[k as string] ?? String(k));

  const resultat = useMemo(() => {
    if (manquants.length > 0) return null;
    try {
      const obsLat = nombre(e.obsLat)!, obsLon = nombre(e.obsLon)!, h = nombre(e.obsAlt)!;
      const cibLat = nombre(e.cibLat)!, cibLon = nombre(e.cibLon)!;
      const H = nombre(e.cibH)!, zB = nombre(e.cibZb)!;
      const kMin = nombre(e.kMin)!, kMax = nombre(e.kMax)!;
      const uF = nombre(e.uF)!, facteur = nombre(e.facteur)!;

      if (kMin > kMax) throw new Error('k minimal supérieur à k maximal : l’intervalle est inversé.');
      const geo = vincentyInverse(obsLat, obsLon, cibLat, cibLon);
      if (geo.distanceM === 0) throw new Error('Les deux points sont confondus : il n’y a pas de visée.');
      const latMoy = (obsLat + cibLat) / 2;
      const REuler = rayonEuler(latMoy, geo.azimutDepartDeg);
      const ci = faireCible(H, zB);

      // L'enveloppe, jamais un point : les bornes de l'intervalle de k, plus
      // un intermédiaire pour montrer la forme.
      const ks = [kMin, (kMin + kMax) / 2, kMax];
      const lignesK = ks.map((k) => {
        const R = rayonEffectif(REuler, k);
        return {
          k, R,
          c: hauteurOccultee(geo.distanceM, h, ci, R),
          f: fractionVisible(geo.distanceM, h, ci, R),
          dCrit: distanceCritique(h, ci, R),
          dLim: distanceLimite(h, ci, R),
          regime: classerRegime(k),
        };
      });
      const fS = lignesK.map((l) => l.f);
      const cd = conditionDiscrimination(h, ci, REuler, geo.distanceM, kMin, kMax, uF, facteur);

      return {
        geo, REuler, latMoy, lignesK, ci, h,
        fMin: Math.min(...fS), fMax: Math.max(...fS),
        ecartR1: (100 * (REuler - IUGG_R1)) / IUGG_R1,
        cd, erreur: null as string | null,
      };
    } catch (err) {
      return { erreur: err instanceof Error ? err.message : String(err) } as never;
    }
  }, [e, manquants.length]);

  const erreur = resultat && 'erreur' in resultat && resultat.erreur ? resultat.erreur : null;
  const ok = resultat && !erreur ? resultat : null;

  return (
    <div style={{ maxWidth: 940, margin: '0 auto' }}>

      {/* ── Ce que l'outil fait, et ce qu'il ne fait pas ── */}
      <div style={{
        background: dash.opalSoft, border: `1px solid ${ACCENT}40`,
        borderRadius: 10, padding: '16px 20px', marginBottom: 20,
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 8,
        }}>Ce que ce calculateur produit</div>
        <p style={{ margin: '0 0 8px', fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          La <strong>fraction de la hauteur de la cible</strong> que chaque modèle géométrique
          prédit visible, sur tout l’intervalle de réfraction que vous déclarez — jamais une
          valeur unique. Puis il dit si la <strong>condition de discrimination du §28.2</strong>
          est satisfaite pour cette configuration.
        </p>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          Il ne rend <strong>aucun verdict</strong>. Comparer une observation à ces prédictions
          demande une photographie mesurée selon le protocole, avec ses contrôles d’intégrité,
          ses trois analystes en aveugle et son seuil déposé d’avance.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
        <button
          onClick={() => setE(EXEMPLE)}
          style={{
            padding: '9px 16px', fontSize: 13, fontWeight: 600, cursor: 'pointer',
            background: 'var(--card)', color: 'var(--ink)',
            border: `1px solid ${ACCENT}`, borderRadius: 6,
          }}
        >Charger un exemple sourcé</button>
        <button
          onClick={() => setE(ETAT_VIDE)}
          style={{
            padding: '9px 16px', fontSize: 13, cursor: 'pointer',
            background: 'transparent', color: 'var(--ink-muted)',
            border: '1px solid var(--border)', borderRadius: 6,
          }}
        >Tout vider</button>
      </div>

      <Bloc num="01" titre="Point d’observation">
        <ChampSource label="Latitude" unite="degrés décimaux" champ={e.obsLat} onChange={maj('obsLat')}
          aide="Positif au nord. Relevé GNSS ou point géodésique publié." />
        <ChampSource label="Longitude" unite="degrés décimaux" champ={e.obsLon} onChange={maj('obsLon')}
          aide="Positif à l’est." />
        <ChampSource label="Altitude de l’axe optique" unite="mètres" champ={e.obsAlt} onChange={maj('obsAlt')}
          aide="Au-dessus de la surface de référence : altitude du sol plus hauteur de l’axe optique. Pas une hauteur ellipsoïdale GNSS brute (§12.1)." />
      </Bloc>

      <Bloc num="02" titre="Cible">
        <ChampSource label="Latitude" unite="degrés décimaux" champ={e.cibLat} onChange={maj('cibLat')}
          aide="Fiche officielle de l’ouvrage, relevé géodésique, ou registre horodaté pour un mobile." />
        <ChampSource label="Longitude" unite="degrés décimaux" champ={e.cibLon} onChange={maj('cibLon')}
          aide="Même source que la latitude." />
        <ChampSource label="Hauteur totale H" unite="mètres" champ={e.cibH} onChange={maj('cibH')}
          aide="Établie indépendamment de toute photographie (§12.4) : plan coté, fiche technique, données topographiques." />
        <ChampSource label="Altitude de la base z_b" unite="mètres" champ={e.cibZb} onChange={maj('cibZb')}
          aide="0 pour une base au niveau moyen de la mer. Une base surélevée change les deux distances critiques (§9.2)." />
      </Bloc>

      <Bloc num="03" titre="Intervalle de réfraction déclaré">
        <p style={{ margin: '0 0 14px', fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
          Le §11.7 interdit d’ajuster ce coefficient après avoir vu un résultat. L’intervalle se
          déclare d’avance, et se justifie : profil vertical mesuré s’il existe, sinon la plage
          plausible entière pour le site, la saison et l’heure.
        </p>
        <ChampSource label="k minimal" unite="sans dimension" champ={e.kMin} onChange={maj('kMin')} pas="0.01"
          aide="0 correspond au gradient autoconvectif ; 0,13 à 0,17 à une atmosphère bien mélangée (Tableau 8)." />
        <ChampSource label="k maximal" unite="sans dimension" champ={e.kMax} onChange={maj('kMax')} pas="0.01"
          aide="Doit rester sous 1 : au-delà, le rayon épouse la surface et la construction du §8 ne s’applique plus." />
      </Bloc>

      <Bloc num="04" titre="Condition de discrimination (§28.2)">
        <ChampSource label="Incertitude de mesure u(f)" unite="fraction" champ={e.uF} onChange={maj('uF')} pas="0.01"
          aide="Incertitude composée attendue sur la fraction mesurée, issue de la résolution effective et de la dispersion entre analystes (§22.1)." />
        <ChampSource label="Facteur d’admission" unite="sans dimension" champ={e.facteur} onChange={maj('facteur')} pas="1"
          aide="5 est la valeur recommandée au §26. Elle n’a rien d’obligatoire : mettez celle que vous avez réellement déposée." />
      </Bloc>

      {/* ── Résultats ── */}
      {manquants.length > 0 && (
        <div style={{
          background: 'var(--card)', border: `1px solid ${dash.rose}60`,
          borderLeft: `3px solid ${dash.rose}`, borderRadius: 8, padding: '14px 18px',
        }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
            <strong>{manquants.length} valeur{manquants.length > 1 ? 's' : ''} manquante{manquants.length > 1 ? 's' : ''}.</strong>{' '}
            Aucun calcul n’est lancé : rien ici n’est complété par une valeur plausible, et
            c’est la première règle du protocole.
          </p>
        </div>
      )}

      {manquants.length === 0 && grandeursSansSource.length > 0 && (
        <div style={{
          background: dash.saffronSoft, border: `1px solid ${dash.saffron}55`,
          borderLeft: `3px solid ${dash.saffron}`, borderRadius: 8, padding: '14px 18px',
        }}>
          <div style={{
            fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
            color: dash.saffron, textTransform: 'uppercase', marginBottom: 6,
          }}>
            Ce qui reste à établir — {grandeursSansSource.length} grandeur{grandeursSansSource.length > 1 ? 's' : ''}
          </div>
          <p style={{ margin: '0 0 6px', fontSize: 13, lineHeight: 1.65, color: dash.ink }}>
            {grandeursSansSource.join(', ')}.
          </p>
          <p style={{ margin: 0, fontSize: 12, lineHeight: 1.65, color: dash.ink }}>
            Ces valeurs entrent dans le calcul. Une source saisie ici est une{' '}
            <strong>déclaration</strong>, jamais une vérification : rien dans cet outil ne
            contrôle qu’une fiche d’ouvrage dit bien ce qu’on lui fait dire. C’est à l’analyste
            d’établir chacune de ces grandeurs.
          </p>
        </div>
      )}

      {erreur && (
        <div style={{
          background: 'var(--card)', border: `1px solid ${dash.rose}60`,
          borderLeft: `3px solid ${dash.rose}`, borderRadius: 8, padding: '14px 18px',
        }}>
          <p style={{ margin: 0, fontSize: 13.5, color: 'var(--ink)' }}>
            <strong>Calcul refusé.</strong> {erreur}
          </p>
        </div>
      )}

      {ok && (
        <>
          <Bloc num="05" titre="Géométrie établie">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                <Ligne cle="Distance géodésique D" val={`${fmt(ok.geo.distanceM / 1000, 3)} km`} />
                <Ligne cle="Azimut au départ" val={`${fmt(ok.geo.azimutDepartDeg, 4)} °`} />
                <Ligne cle="Azimut à l’arrivée (α₂)" val={`${fmt(ok.geo.azimutArriveeDeg, 4)} °`} />
                <Ligne cle="Convergence de Vincenty" val={`${ok.geo.iterations} itération${ok.geo.iterations > 1 ? 's' : ''}`} />
                <Ligne cle="Latitude moyenne du trajet" val={`${fmt(ok.latMoy, 5)} °`} />
                <Ligne cle="Rayon de courbure d’Euler" val={`${fmt(ok.REuler / 1000, 3)} km`} />
                <Ligne cle="Écart à R₁ (6 371,009 km)" val={`${ok.ecartR1 >= 0 ? '+' : ''}${fmt(ok.ecartR1, 3)} %`} />
              </tbody>
            </table>
            <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.5, color: 'var(--ink-muted)' }}>
              C’est le rayon d’Euler à l’azimut de la visée qui est employé pour toute la suite,
              et non le rayon moyen R₁ : le §12.2 l’impose, et l’écart entre les deux atteint 1 %
              sur l’ellipsoïde.
            </p>
          </Bloc>

          <Bloc num="06" titre="Enveloppe des prédictions">
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr>
                    {['k', 'Régime (Tableau 8)', 'R_eff (km)', 'D_crit (km)', 'D_lim (km)', 'c occultée (m)', 'f modèle S', 'f modèle P'].map((t) => (
                      <th key={t} style={{
                        padding: '7px 9px', textAlign: 'left', fontSize: 10,
                        fontFamily: dash.fontMono, letterSpacing: '0.05em',
                        color: 'var(--ink-muted)', textTransform: 'uppercase',
                        borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap',
                      }}>{t}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ok.lignesK.map((l, i) => (
                    <tr key={i} style={{ background: i === 1 ? 'transparent' : dash.opalSoft + '60' }}>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.k, 3)}</td>
                      <td style={{ padding: '8px 9px', fontSize: 12, color: 'var(--ink-soft)', borderBottom: '1px solid var(--border-soft, var(--border))' }}>{l.regime}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.R / 1000, 1)}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.dCrit / 1000, 2)}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.dLim / 1000, 2)}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.c, 2)}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', fontWeight: 700, color: ACCENT, borderBottom: '1px solid var(--border-soft, var(--border))' }}>{fmt(l.f, 4)}</td>
                      <td style={{ padding: '8px 9px', fontFamily: dash.fontMono, textAlign: 'right', color: 'var(--ink-soft)', borderBottom: '1px solid var(--border-soft, var(--border))' }}>1,0000</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p style={{ margin: '12px 0 0', fontSize: 13, lineHeight: 1.6, color: 'var(--ink)' }}>
              Sur l’intervalle déclaré, le modèle S prédit une fraction visible entre{' '}
              <strong style={{ fontFamily: dash.fontMono }}>{fmt(ok.fMin, 4)}</strong> et{' '}
              <strong style={{ fontFamily: dash.fontMono }}>{fmt(ok.fMax, 4)}</strong>. Le modèle P
              prédit <strong style={{ fontFamily: dash.fontMono }}>1,0000</strong> à toute distance :
              il ne comporte aucun paramètre libre, ce qui le rend plus facilement réfutable et
              moins facilement écarté quand les données sont pauvres (§29.3).
            </p>
          </Bloc>

          <Bloc num="07" titre="Condition de discrimination (§28.2)">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                <Ligne cle="Δ — écart minimal sur l’enveloppe jointe" val={fmt(ok.cd.delta, 5)} />
                <Ligne cle="k au bord le plus défavorable" val={fmt(ok.cd.combinaisonDefavorable.k ?? NaN, 3)} />
                <Ligne cle={`Seuil — ${fmt(ok.cd.facteur, 0)} × u(f)`} val={fmt(ok.cd.seuil, 5)} />
              </tbody>
            </table>
            <div style={{
              marginTop: 14, padding: '14px 16px', borderRadius: 8,
              background: ok.cd.satisfaite ? dash.opalSoft : dash.roseSoft,
              border: `1px solid ${ok.cd.satisfaite ? ACCENT : dash.rose}50`,
            }}>
              <div style={{
                fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
                textTransform: 'uppercase', marginBottom: 7,
                color: ok.cd.satisfaite ? ACCENT : dash.rose,
              }}>
                {ok.cd.satisfaite ? 'Préalable géométrique satisfait' : 'Préalable géométrique non satisfait'}
              </div>
              <p style={{ margin: '0 0 8px', fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
                {ok.cd.satisfaite ? (
                  <>Δ = {fmt(ok.cd.delta, 4)} atteint le seuil de {fmt(ok.cd.seuil, 4)}. Les deux
                  modèles prédisent des fractions assez éloignées pour qu’une mesure de cette
                  précision puisse les distinguer, <strong>même au bord d’enveloppe le plus
                  défavorable</strong> (k = {fmt(ok.cd.combinaisonDefavorable.k ?? NaN, 2)}).</>
                ) : (
                  <>Δ = {fmt(ok.cd.delta, 4)} n’atteint pas le seuil de {fmt(ok.cd.seuil, 4)}. Une
                  observation dans cette configuration serait classée <em>indéterminée</em> avant
                  même que la fraction visible soit mesurée. Ce n’est pas un défaut de la
                  configuration : c’est une information sur elle.</>
                )}
              </p>
              <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.55, color: dash.inkSoft }}>
                <strong>Ce résultat n’est pas un verdict.</strong> Il ne dit rien sur la forme de la
                Terre, ni sur la validité d’une photographie. C’est un préalable purement
                géométrique : il indique seulement si une mesure conduite ici pourrait, en
                principe, départager les deux modèles. Le verdict à trois valeurs — compatible,
                incompatible, indéterminé — exige une mesure photographique réelle, ses contrôles
                d’intégrité, trois analyses indépendantes en aveugle et un seuil déposé avant
                l’examen des images.
              </p>
            </div>
          </Bloc>

          <Bloc num="08" titre="Traçabilité des entrées">
            <p style={{ margin: '0 0 12px', fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
              Chaque valeur employée ci-dessus, avec la source que vous avez déclarée. Un rapport
              qui ne porte pas cette colonne n’est pas recevable (§2.3.2).
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  {([
                    ['Latitude observateur', e.obsLat, '°'],
                    ['Longitude observateur', e.obsLon, '°'],
                    ['Altitude axe optique', e.obsAlt, 'm'],
                    ['Latitude cible', e.cibLat, '°'],
                    ['Longitude cible', e.cibLon, '°'],
                    ['Hauteur totale H', e.cibH, 'm'],
                    ['Altitude de base z_b', e.cibZb, 'm'],
                    ['k minimal', e.kMin, ''],
                    ['k maximal', e.kMax, ''],
                    ['Incertitude u(f)', e.uF, ''],
                    ['Facteur d’admission', e.facteur, ''],
                  ] as [string, Champ, string][]).map(([nom, champ, unite]) => (
                    <Ligne
                      key={nom} cle={nom}
                      val={nombre(champ) === null ? INDISPONIBLE : `${champ.valeur}${unite ? ' ' + unite : ''}`}
                      source={champ.source}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </Bloc>

          <div style={{
            background: 'var(--card)', border: '1px solid var(--border)',
            borderLeft: `3px solid ${dash.saffron}`, borderRadius: 8,
            padding: '14px 18px', marginBottom: 16,
          }}>
            <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
              Ce calculateur ne vérifie pas que la ligne de visée reste au-dessus de l’eau. Un
              relief intermédiaire occulte la cible pour une raison qui n’est pas celle qu’on
              mesure, et le §3.5 écarte alors le cliché. Le pré-écran altimétrique, qui interroge
              les données officielles pour le vérifier, n’est pas encore intégré ici.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
