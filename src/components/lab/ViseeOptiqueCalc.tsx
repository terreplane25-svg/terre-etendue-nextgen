'use client';
/**
 * ViseeOptiqueCalc — Le Simulateur de Visée.
 *
 * QUATRE CHAMPS, UN BOUTON
 * ────────────────────────
 * Une version antérieure demandait onze valeurs, dont l'intervalle de
 * réfraction, une incertitude de mesure et un facteur d'admission, et
 * renvoyait le visiteur à des paragraphes d'un document qu'il n'a pas lu.
 * Elle était juste et inutilisable : un outil qu'il faut avoir compris avant
 * de s'en servir ne sert qu'à ceux qui n'en ont pas besoin.
 *
 * Ce qui a été retiré de l'ÉCRAN n'a pas été retiré du CALCUL. La réfraction
 * est toujours traitée en enveloppe, la géodésique est toujours celle de
 * Vincenty sur l'ellipsoïde, le relief est toujours distingué de la courbure.
 * Ces choix sont désormais pris par le moteur et énoncés en prose dans un
 * bloc rétractable — ils sont donc encore contestables, ce qui était le point.
 *
 * DEUX RÈGLES QUI NE SE NÉGOCIENT PAS
 * ───────────────────────────────────
 *  1. La simulation tourne TOUJOURS sur les coordonnées et hauteurs saisies.
 *     Ni le géocodage ni l'altimétrie ne peuvent l'empêcher : quand ces
 *     services manquent, le résultat est rendu avec ce qui manque écrit
 *     dessus, jamais remplacé par une valeur commode.
 *  2. « Relief non évalué » n'est jamais affiché comme « aucun obstacle ».
 *     Confondre les deux attribuerait à la forme de la Terre ce qui revient à
 *     un talus, et l'erreur va dans les deux sens.
 */
import { useCallback, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import ResultatSimulation, { type Simulation } from './SimulationRelief';
import {
  cible as faireCible,
  rayonEffectif,
  rayonEuler,
  vincentyInverse,
} from '@/lib/visee-optique/noyau';
import { analyserRelief } from '@/lib/visee-optique/relief';
import { profilDepuisIgn } from '@/lib/visee-optique/altimetrie-ign';
import { resoudrePosition } from '@/lib/visee-optique/geocodage-ign';
import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  juger,
  pasEchantillonnageM,
} from '@/lib/visee-optique/simulation';

const ACCENT = dash.opal;

interface Saisie {
  obsPosition: string;
  obsHauteur: string;
  cibPosition: string;
  cibHauteur: string;
}

const VIDE: Saisie = { obsPosition: '', obsHauteur: '', cibPosition: '', cibHauteur: '' };

/** Un exemple réel, chargeable d'un clic : Sangatte vers les falaises de Douvres. */
const EXEMPLE: Saisie = {
  obsPosition: '50.94642, 1.75305',
  obsHauteur: '2',
  cibPosition: '51.13152, 1.338825',
  cibHauteur: '110',
};

function nombre(s: string): number | null {
  if (s.trim() === '') return null;
  const v = Number(s.replace(',', '.'));
  return Number.isFinite(v) ? v : null;
}

function Champ({
  label, aide, valeur, onChange, placeholder, large,
}: {
  label: string; aide: string; valeur: string;
  onChange: (v: string) => void; placeholder: string; large?: boolean;
}) {
  return (
    <div style={{ flex: large ? '2 1 260px' : '1 1 150px', minWidth: 0 }}>
      <label style={{
        display: 'block', fontSize: 12.5, fontWeight: 600,
        color: 'var(--ink)', marginBottom: 5,
      }}>{label}</label>
      <input
        type="text"
        value={valeur}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={label}
        style={{
          width: '100%', minHeight: 44, padding: '10px 12px', fontSize: 15,
          fontFamily: large ? 'inherit' : dash.fontMono,
          background: 'var(--card)', color: 'var(--ink)',
          border: `1px solid ${valeur.trim() === '' ? 'var(--border)' : `${ACCENT}80`}`,
          borderRadius: 6, outline: 'none',
        }}
      />
      <p style={{ margin: '4px 0 0', fontSize: 11.5, lineHeight: 1.45, color: 'var(--ink-muted)' }}>
        {aide}
      </p>
    </div>
  );
}

export default function ViseeOptiqueCalc() {
  const [s, setS] = useState<Saisie>(VIDE);
  const [sim, setSim] = useState<Simulation | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const maj = (cle: keyof Saisie) => (v: string) => setS((p) => ({ ...p, [cle]: v }));

  const lancer = useCallback(async () => {
    setEnCours(true);
    setErreur(null);
    setSim(null);
    try {
      const hObs = nombre(s.obsHauteur);
      const hCib = nombre(s.cibHauteur);
      if (hObs === null) throw new Error('La hauteur de l’œil de l’observateur manque.');
      if (hCib === null) throw new Error('La hauteur totale de la cible manque.');
      if (hCib <= 0) throw new Error('La hauteur de la cible doit être supérieure à zéro.');
      if (hObs < 0) throw new Error('La hauteur de l’œil ne peut pas être négative.');

      // Le géocodage d'abord, parce qu'il peut échouer et qu'il vaut mieux
      // l'apprendre avant d'avoir attendu l'altimétrie.
      const [a, b] = await Promise.all([
        resoudrePosition(s.obsPosition),
        resoudrePosition(s.cibPosition),
      ]);

      const geo = vincentyInverse(a.latitude, a.longitude, b.latitude, b.longitude);
      if (geo.distanceM === 0) {
        throw new Error('Les deux points sont confondus : il n’y a pas de visée.');
      }
      const REuler = rayonEuler((a.latitude + b.latitude) / 2, geo.azimutDepartDeg);
      const ci = faireCible(hCib, 0);

      // ── Le relief, s'il est disponible ────────────────────────────────────
      //
      // L'échec de l'altimétrie ne fait PAS tomber la simulation : elle
      // repart sur la surface de référence, et le motif est rendu avec. Un
      // profil manquant n'est jamais « aucun obstacle » — c'est « on ne sait
      // pas », ce qui n'est pas la même chose et ne se dit pas pareil.
      // Le pas suit la DISTANCE : aucune visée n'est refusée pour sa
      // longueur, mais un pas fixe de 250 m sur 2 000 km demanderait 8 000
      // altitudes. Le pas retenu est rendu au visiteur, parce qu'il décide de
      // ce qu'on peut manquer : une colline étroite peut passer entre deux
      // points de mesure.
      const pasM = pasEchantillonnageM(geo.distanceM);
      let profil = null;
      let reserveIgn: string | null = null;
      let motifProfil: string | null = null;
      let lacunes: number[] = [];
      try {
        const r = await profilDepuisIgn(
          a.latitude, a.longitude, b.latitude, b.longitude, { pasM },
        );
        profil = r.profil;
        reserveIgn = r.reserve;
        lacunes = r.lacunesM;
      } catch (err) {
        motifProfil = err instanceof Error ? err.message : String(err);
      }

      const analyse = (k: number) => analyserRelief(
        geo.distanceM, hObs, ci, rayonEffectif(REuler, k), profil, 'sphérique', 0,
      );
      const globeMin = analyse(K_ENVELOPPE_MIN);
      const globeMax = analyse(K_ENVELOPPE_MAX);

      setSim({
        D: geo.distanceM,
        azimutDeg: geo.azimutDepartDeg,
        pasDemandeM: pasM,
        positionObs: a,
        positionCible: b,
        profil,
        motifProfil,
        reserveIgn,
        lacunesM: lacunes,
        globeMin,
        globeMax,
        plan: analyserRelief(geo.distanceM, hObs, ci, null, profil, 'plan', 0),
        verdict: juger(globeMin, globeMax, hCib),
        cible: ci,
        h: hObs,
        rTrace: rayonEffectif(REuler, (K_ENVELOPPE_MIN + K_ENVELOPPE_MAX) / 2),
      });
    } catch (err) {
      setErreur(err instanceof Error ? err.message : String(err));
    } finally {
      setEnCours(false);
    }
  }, [s]);

  const pret = s.obsPosition.trim() !== '' && s.cibPosition.trim() !== ''
    && nombre(s.obsHauteur) !== null && nombre(s.cibHauteur) !== null;

  return (
    <div style={{ maxWidth: 940, margin: '0 auto' }}>

      {/* La fenêtre du Lab a un fond sombre : un paragraphe posé dessus sans
          conteneur serait du texte sombre sur fond sombre. */}
      <div style={{
        background: dash.opalSoft, border: `1px solid ${ACCENT}40`,
        borderRadius: 10, padding: '15px 20px', marginBottom: 18,
      }}>
        <p style={{ margin: 0, fontSize: 14.5, lineHeight: 1.65, color: dash.ink }}>
          Deux points, deux hauteurs. Le simulateur calcule ce que chaque modèle de
          Terre — <strong>sphérique</strong> et <strong>plate</strong> — prédit que vous
          devriez voir, et vous dit si la différence entre les deux est assez grande
          pour être photographiée.
        </p>
      </div>

      {/* ── Observateur ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '16px 18px', marginBottom: 12,
      }}>
        <div style={{
          fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 12,
        }}>Observateur</div>
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <Champ
            label="Où vous êtes" large
            valeur={s.obsPosition} onChange={maj('obsPosition')}
            placeholder="50.94642, 1.75305 — ou une adresse"
            aide="Coordonnées « latitude, longitude », ou une adresse française."
          />
          <Champ
            label="Hauteur de l’œil"
            valeur={s.obsHauteur} onChange={maj('obsHauteur')}
            placeholder="2"
            aide="En mètres au-dessus du niveau de la mer, appareil compris."
          />
        </div>
      </div>

      {/* ── Cible ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '16px 18px', marginBottom: 16,
      }}>
        <div style={{
          fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 12,
        }}>Cible</div>
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <Champ
            label="Ce que vous regardez" large
            valeur={s.cibPosition} onChange={maj('cibPosition')}
            placeholder="51.13152, 1.338825 — ou une adresse"
            aide="Coordonnées « latitude, longitude », ou une adresse."
          />
          <Champ
            label="Hauteur totale"
            valeur={s.cibHauteur} onChange={maj('cibHauteur')}
            placeholder="110"
            aide="En mètres, du niveau de la mer jusqu’au sommet."
          />
        </div>
      </div>

      {/* ── Le bouton unique ── */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginBottom: 20 }}>
        <button
          onClick={() => void lancer()}
          disabled={!pret || enCours}
          style={{
            padding: '13px 28px', fontSize: 15, fontWeight: 700, minHeight: 48,
            cursor: !pret || enCours ? 'not-allowed' : 'pointer',
            background: !pret || enCours ? 'var(--border)' : ACCENT,
            color: !pret || enCours ? 'var(--ink-muted)' : '#08131b',
            border: 'none', borderRadius: 8,
          }}
        >{enCours ? 'Simulation en cours…' : 'Lancer la simulation'}</button>
        <button
          onClick={() => { setS(EXEMPLE); setSim(null); setErreur(null); }}
          style={{
            padding: '11px 18px', fontSize: 13.5, minHeight: 44, cursor: 'pointer',
            background: 'transparent', color: 'var(--ink-soft)',
            border: '1px solid var(--border)', borderRadius: 6,
          }}
        >Charger un exemple</button>
      </div>

      {erreur && (
        <div style={{
          background: 'var(--card)', border: `1px solid ${dash.rose}60`,
          borderLeft: `3px solid ${dash.rose}`, borderRadius: 8,
          padding: '14px 18px', marginBottom: 16,
        }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>{erreur}</p>
        </div>
      )}

      {sim && <ResultatSimulation sim={sim} />}
    </div>
  );
}
