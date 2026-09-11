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
 * LE RELIEF, À LA DEMANDE ET JAMAIS AUTOMATIQUEMENT
 * ─────────────────────────────────────────────────
 * Le relevé du terrain part sur une action explicite, après la simulation.
 * C'est le seul outil du Lab qui transmet quelque chose — les coordonnées
 * saisies, à l'IGN — et une requête automatique les enverrait sans que
 * personne l'ait demandé.
 *
 * La simulation, elle, ne l'attend pas et n'en dépend pas : elle a déjà
 * tourné. Un service en panne laisse le résultat entier, et le relief reste
 * « non évalué » — ce qui n'est pas « aucun obstacle ».
 *
 * LA RÈGLE QUI NE SE NÉGOCIE PAS
 * ──────────────────────────────
 * La simulation tourne TOUJOURS sur les coordonnées et hauteurs saisies. Le
 * géocodage ne peut pas l'empêcher : les coordonnées, décimales ou en degrés-
 * minutes-secondes, sont lues sans qu'aucune requête ne parte.
 */
import { useCallback, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import ResultatVisee, { type EtatRelief, type Simulation } from './ResultatVisee';
import {
  cible as faireCible,
  hauteurOccultee,
  rayonEffectif,
  rayonEuler,
  vincentyInverse,
} from '@/lib/visee-optique/noyau';
import { resoudrePosition } from '@/lib/visee-optique/geocodage-ign';
import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  K_STANDARD,
  juger,
  pasEchantillonnageM,
  verifierK,
} from '@/lib/visee-optique/simulation';
import { analyserRelief, grouperOcclusions } from '@/lib/visee-optique/relief';
import { profilDepuisIgn } from '@/lib/visee-optique/altimetrie-ign';

const ACCENT = dash.opal;

/**
 * DEUX DONNÉES PAR POINT, PAS QUATRE
 * ──────────────────────────────────
 * Une version antérieure séparait l'altitude du sol et la hauteur de
 * l'ouvrage, pour coller à ce que donne Google Earth. Le gain de précision ne
 * payait pas la surcharge : sur une visée d'observation, ce qui compte est la
 * hauteur de l'objet observé au-dessus de sa base.
 *
 * Conséquence assumée, et c'est la seule : la base de la cible est prise à la
 * surface de référence. Une cible posée sur une falaise n'est donc pas
 * modélisée comme telle — il faut alors saisir la hauteur totale depuis le
 * niveau de la mer dans le champ de hauteur.
 */
interface Saisie {
  obsPosition: string;
  obsHauteur: string;
  cibPosition: string;
  cibHauteur: string;
  kPersonnalise: boolean;
  k: string;
}

const VIDE: Saisie = {
  obsPosition: '', obsHauteur: '', cibPosition: '', cibHauteur: '',
  kPersonnalise: false, k: String(K_STANDARD),
};

/** Exemples réels chargeables d'un clic, défilis dans l'ordre. */
const EXEMPLES: Array<{ nom: string } & Saisie> = [
  {
    nom: 'Sangatte → Douvres (28 km)',
    obsPosition: '50.94642, 1.75305',
    obsHauteur: '2',
    cibPosition: '51.13152, 1.338825',
    cibHauteur: '110',
    kPersonnalise: false,
    k: String(K_STANDARD),
  },
  {
    nom: 'Finestrelles → Barre des Écrins (443 km)',
    obsPosition: '42.4827, 0.7521',
    obsHauteur: '2820',
    cibPosition: '44.9243, 6.3572',
    cibHauteur: '4102',
    kPersonnalise: true,
    k: '0.14',
  },
  {
    nom: 'Karagöl (Munzur) → Elbrouz (493 km)',
    obsPosition: '39.45, 39.65',
    obsHauteur: '3107',
    cibPosition: '43.355, 42.439',
    cibHauteur: '5642',
    kPersonnalise: true,
    k: '0.18',
  },
  {
    nom: 'Ol Doinyo Lengai → Kilimandjaro (170 km)',
    obsPosition: '-2.764, 35.914',
    obsHauteur: '2878',
    cibPosition: '-3.067, 37.355',
    cibHauteur: '5895',
    kPersonnalise: false,
    k: String(K_STANDARD),
  },
];

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
  const [exempleIdx, setExempleIdx] = useState(-1);
  const [sim, setSim] = useState<Simulation | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  // Le relevé du terrain est SÉPARÉ de la simulation, et il part sur une
  // action explicite : il transmet les coordonnées saisies à un service tiers,
  // ce qu'aucun autre outil du Lab ne fait. Une requête automatique enverrait
  // ces coordonnées sans que personne l'ait demandé.
  const [relief, setRelief] = useState<EtatRelief>({ etat: 'inactif' });

  const maj = (cle: keyof Saisie) => (v: string) => setS((p) => ({ ...p, [cle]: v }));

  const lancer = useCallback(async () => {
    setEnCours(true);
    setErreur(null);
    setSim(null);
    // Un relevé appartient à UNE visée. Le garder d'une simulation à l'autre
    // afficherait le relief d'un trajet sous le résultat d'un autre.
    setRelief({ etat: 'inactif' });
    try {
      const hObs = nombre(s.obsHauteur);
      const hCib = nombre(s.cibHauteur);
      if (hObs === null) throw new Error('La hauteur de l’observateur manque.');
      if (hCib === null) throw new Error('La hauteur de la cible manque.');
      if (hCib <= 0) throw new Error('La hauteur de la cible doit être supérieure à zéro.');
      if (hObs < 0) {
        throw new Error(
          'La hauteur de l’observateur ne peut pas être négative : elle est comptée '
          + 'au-dessus de la surface de référence.',
        );
      }

      // Le coefficient de réfraction : la moyenne standard, ou celui que
      // l'analyste déclare. Le refus vient du module de référence, pas d'ici.
      const k = s.kPersonnalise ? nombre(s.k) : K_STANDARD;
      if (k === null) throw new Error('Le coefficient de réfraction saisi n’est pas un nombre.');
      verifierK(k);

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
      // La base de la cible est prise à la surface de référence : le
      // formulaire ne demande qu'une hauteur, et l'inventer autrement
      // reviendrait à combler un champ qu'on n'a pas.
      const ci = faireCible(hCib, 0);

      // ── L'occultation à la base, sur la seule géométrie ───────────────────
      //
      // Le verdict est rendu au gradient MOYEN. L'enveloppe sert à afficher
      // l'écart que laisse l'ignorance du profil vertical de température :
      // rendre un chiffre unique le ferait passer pour mieux connu qu'il ne
      // l'est, mais juger sur l'enveloppe serait plus sévère que ce qui est
      // annoncé à l'écran.
      const masquee = (k: number) =>
        hauteurOccultee(geo.distanceM, hObs, ci, rayonEffectif(REuler, k));
      const masqueeStandard = masquee(k);
      // L'enveloppe n'a de sens que si l'on IGNORE la réfraction. Quand
      // l'analyste la déclare, l'afficher quand même contredirait ce qu'il
      // affirme ; les bornes valent alors la valeur employée.
      const bornes = s.kPersonnalise
        ? [masqueeStandard, masqueeStandard]
        : [masquee(K_ENVELOPPE_MIN), masquee(K_ENVELOPPE_MAX)].sort((x, y) => x - y);

      setSim({
        D: geo.distanceM,
        azimutDeg: geo.azimutDepartDeg,
        positionObs: a,
        positionCible: b,
        masqueeStandardM: masqueeStandard,
        masqueeEnveloppeMinM: bornes[0],
        masqueeEnveloppeMaxM: bornes[1],
        kEmploye: k,
        kPersonnalise: s.kPersonnalise,
        verdict: juger(masqueeStandard, hCib),
        cible: ci,
        h: hObs,
        rTrace: rayonEffectif(REuler, k),
      });
    } catch (err) {
      setErreur(err instanceof Error ? err.message : String(err));
    } finally {
      setEnCours(false);
    }
  }, [s]);

  /**
   * Le relevé du terrain, à la demande.
   *
   * Il ne touche jamais `sim` : la géométrie reste ce qu'elle était, et un
   * échec du service laisse le résultat entier. C'était la règle posée quand
   * le modèle de terrain avait été retiré, et elle vaut aussi pour son retour.
   */
  const relever = useCallback(async () => {
    if (sim === null) return;
    setRelief({ etat: 'en-cours' });
    try {
      // Le pas suit la DISTANCE : aucune visée n'est refusée pour sa longueur,
      // mais un pas fixe de 250 m sur 2 000 km demanderait 8 000 altitudes.
      const pasM = pasEchantillonnageM(sim.D);
      const r = await profilDepuisIgn(
        sim.positionObs.latitude, sim.positionObs.longitude,
        sim.positionCible.latitude, sim.positionCible.longitude,
        { pasM },
      );
      const analyse = analyserRelief(sim.D, sim.h, sim.cible, sim.rTrace, r.profil, 'sphérique', 0);
      setRelief({
        etat: 'fait',
        releve: {
          analyse,
          occlusions: grouperOcclusions(analyse.obstacles, r.profil.pasM),
          pasM: r.profil.pasM,
          source: r.profil.source,
          lacunesM: r.lacunesM,
          reserve: r.reserve,
        },
      });
    } catch (err) {
      setRelief({
        etat: 'echec',
        motif: err instanceof Error ? err.message : String(err),
      });
    }
  }, [sim]);

  const pret = s.obsPosition.trim() !== '' && s.cibPosition.trim() !== ''
    && nombre(s.obsHauteur) !== null && nombre(s.cibHauteur) !== null
    && (!s.kPersonnalise || nombre(s.k) !== null);

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
            aide="Degrés décimaux, degrés-minutes-secondes (50°52'47.56&quot;N 1°38'46.91&quot;E), ou une adresse."
          />
          <Champ
            label="Hauteur"
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
            aide="Degrés décimaux, degrés-minutes-secondes, ou une adresse."
          />
          <Champ
            label="Hauteur"
            valeur={s.cibHauteur} onChange={maj('cibHauteur')}
            placeholder="110"
            aide="Sa taille totale en mètres, de sa base à son sommet."
          />
        </div>
      </div>

      {/* ── L'option avancée : le coefficient de réfraction ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '13px 18px', marginBottom: 16,
      }}>
        <label style={{
          display: 'flex', alignItems: 'center', gap: 9, cursor: 'pointer',
          fontSize: 13, color: 'var(--ink)',
        }}>
          <input
            type="checkbox"
            checked={s.kPersonnalise}
            onChange={(e) => setS((p) => ({ ...p, kPersonnalise: e.target.checked }))}
            style={{ width: 16, height: 16, cursor: 'pointer', accentColor: ACCENT }}
          />
          Spécifier le coefficient <em>k</em> de réfraction
        </label>
        {!s.kPersonnalise && (
          <p style={{ margin: '6px 0 0 25px', fontSize: 11.5, lineHeight: 1.5, color: 'var(--ink-muted)' }}>
            Sans cela, le calcul emploie la moyenne standard <strong>k = 0,13</strong>, celle
            d’une atmosphère bien mélangée, et affiche l’écart que laisse cette ignorance.
          </p>
        )}
        {s.kPersonnalise && (
          <div style={{ marginTop: 11, marginLeft: 25 }}>
            <input
              type="text" inputMode="decimal"
              value={s.k}
              onChange={(e) => setS((p) => ({ ...p, k: e.target.value }))}
              aria-label="Coefficient de réfraction k"
              style={{
                width: 110, minHeight: 40, padding: '9px 11px', fontSize: 15,
                fontFamily: dash.fontMono, background: 'var(--bg)', color: 'var(--ink)',
                border: `1px solid ${ACCENT}80`, borderRadius: 6, outline: 'none',
              }}
            />
            <p style={{ margin: '6px 0 0', fontSize: 11.5, lineHeight: 1.5, color: 'var(--ink-muted)' }}>
              0,08 pour une réfraction faible, 0,13 en moyenne, 0,20 et au-delà par forte
              inversion — les mirages. Le calcul tournera sur cette valeur seule, sans
              enveloppe : vous affirmez la connaître, c’est à vous de la justifier par un
              relevé du profil de température sur le trajet.
            </p>
          </div>
        )}
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
          onClick={() => {
            const idx = (exempleIdx + 1) % EXEMPLES.length;
            const { nom: _nom, ...saisie } = EXEMPLES[idx];
            setExempleIdx(idx);
            setS(saisie);
            setSim(null);
            setErreur(null);
          }}
          style={{
            padding: '11px 20px', fontSize: 13.5, minHeight: 44, cursor: 'pointer',
            background: `${ACCENT}18`,
            color: 'var(--ink)',
            border: `1.5px solid ${ACCENT}70`,
            borderRadius: 6, fontWeight: 600,
          }}
        >
          {exempleIdx < 0
            ? `Charger un exemple`
            : `→ ${EXEMPLES[(exempleIdx + 1) % EXEMPLES.length].nom}`}
        </button>
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

      {sim && <ResultatVisee sim={sim} relief={relief} onRelever={() => void relever()} />}
    </div>
  );
}
