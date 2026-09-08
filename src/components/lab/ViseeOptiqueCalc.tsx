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
 * GÉOMÉTRIE PURE : PLUS AUCUN MODÈLE DE TERRAIN
 * ─────────────────────────────────────────────
 * Le simulateur ne consulte plus de profil altimétrique et ne cherche plus
 * d'obstacle local. Chercher ce qui bouche la vue depuis un poste donné relève
 * du contrôle de l'analyste SUR L'IMAGE RÉELLE — une haie, un cargo, un
 * bâtiment récent ne figurent dans aucun modèle numérique de terrain.
 *
 * LA RÈGLE QUI NE SE NÉGOCIE PAS
 * ──────────────────────────────
 * La simulation tourne TOUJOURS sur les coordonnées et hauteurs saisies. Le
 * géocodage ne peut pas l'empêcher : les coordonnées, décimales ou en degrés-
 * minutes-secondes, sont lues sans qu'aucune requête ne parte.
 */
import { useCallback, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import ResultatVisee, { type Simulation } from './ResultatVisee';
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
  verifierK,
} from '@/lib/visee-optique/simulation';

const ACCENT = dash.opal;

/**
 * L'ALTITUDE DU SOL ET LA HAUTEUR DE L'OUVRAGE SONT DEUX CHAMPS DISTINCTS
 * ───────────────────────────────────────────────────────────────────────
 * Google Earth affiche l'altitude du TERRAIN sous le curseur. Ce n'est ni la
 * hauteur de l'œil de l'observateur, ni la hauteur d'un phare : il faut
 * ajouter la seconde à la première. Un seul champ « hauteur » invitait à
 * saisir l'une pour l'autre, et l'erreur ne se voit pas dans le résultat —
 * elle le décale simplement.
 *
 * La séparation change aussi la GÉOMÉTRIE, pas seulement l'ergonomie : la
 * base de la cible n'est plus au niveau de la mer mais à l'altitude de son
 * terrain, ce qui recule la distance critique et réduit l'occultation. Une
 * cible posée sur une falaise de 200 m émerge bien plus longtemps qu'une
 * cible posée sur l'eau.
 */
interface Saisie {
  obsPosition: string;
  obsAltitudeSol: string;
  obsHauteurOeil: string;
  cibPosition: string;
  cibAltitudeSol: string;
  cibHauteurOuvrage: string;
  kPersonnalise: boolean;
  k: string;
}

const VIDE: Saisie = {
  obsPosition: '', obsAltitudeSol: '', obsHauteurOeil: '',
  cibPosition: '', cibAltitudeSol: '', cibHauteurOuvrage: '',
  kPersonnalise: false, k: String(K_STANDARD),
};

/** Un exemple réel, chargeable d'un clic : Sangatte vers les falaises de Douvres. */
const EXEMPLE: Saisie = {
  obsPosition: '50.94642, 1.75305',
  obsAltitudeSol: '2',
  obsHauteurOeil: '1.7',
  cibPosition: '51.13152, 1.338825',
  cibAltitudeSol: '0',
  cibHauteurOuvrage: '110',
  kPersonnalise: false,
  k: String(K_STANDARD),
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
      const solObs = nombre(s.obsAltitudeSol);
      const oeil = nombre(s.obsHauteurOeil);
      const solCib = nombre(s.cibAltitudeSol);
      const ouvrage = nombre(s.cibHauteurOuvrage);
      if (solObs === null) throw new Error('L’altitude du sol au point d’observation manque.');
      if (oeil === null) throw new Error('La hauteur de l’œil de l’observateur manque.');
      if (solCib === null) throw new Error('L’altitude du sol au pied de la cible manque.');
      if (ouvrage === null) throw new Error('La hauteur de l’ouvrage visé manque.');
      if (ouvrage <= 0) throw new Error('La hauteur de l’ouvrage doit être supérieure à zéro.');
      if (oeil < 0) throw new Error('La hauteur de l’œil ne peut pas être négative.');
      if (solObs < 0 || solCib < 0) {
        throw new Error(
          'Les altitudes doivent être comptées au-dessus du niveau moyen de la mer, '
          + 'donc positives. Un point sous le niveau de la mer sort de la construction '
          + 'géométrique employée ici.',
        );
      }

      // L'altitude de l'axe optique : le sol PLUS la hauteur de l'œil. C'est
      // cette somme qui entre dans la géométrie, et la séparer à la saisie est
      // ce qui empêche de prendre l'une pour l'autre.
      const hObs = solObs + oeil;
      // La base de la cible est à l'altitude de SON terrain, pas au niveau de
      // la mer. C'est ce qui recule la distance critique.
      const hCib = ouvrage;

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
      const ci = faireCible(hCib, solCib);

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
        altitudeSolObsM: solObs,
        hauteurOeilM: oeil,
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

  const pret = s.obsPosition.trim() !== '' && s.cibPosition.trim() !== ''
    && nombre(s.obsAltitudeSol) !== null && nombre(s.obsHauteurOeil) !== null
    && nombre(s.cibAltitudeSol) !== null && nombre(s.cibHauteurOuvrage) !== null
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
            label="Altitude du sol"
            valeur={s.obsAltitudeSol} onChange={maj('obsAltitudeSol')}
            placeholder="2"
            aide="En mètres au-dessus du niveau de la mer, au point où vous vous tenez."
          />
          <Champ
            label="Hauteur de l’œil"
            valeur={s.obsHauteurOeil} onChange={maj('obsHauteurOeil')}
            placeholder="1,7"
            aide="Au-dessus du sol : votre taille, ou la hauteur du trépied."
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
            label="Altitude du sol"
            valeur={s.cibAltitudeSol} onChange={maj('cibAltitudeSol')}
            placeholder="0"
            aide="En mètres au-dessus du niveau de la mer, au PIED de la cible."
          />
          <Champ
            label="Hauteur de l’ouvrage"
            valeur={s.cibHauteurOuvrage} onChange={maj('cibHauteurOuvrage')}
            placeholder="110"
            aide="Au-dessus de son sol : la falaise, le phare, le bâtiment lui-même."
          />
        </div>
      </div>

      {/* ── Comment remplir depuis Google Earth ── */}
      <details style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '13px 18px', marginBottom: 14,
      }}>
        <summary style={{
          cursor: 'pointer', fontSize: 13, fontWeight: 600, color: ACCENT,
          minHeight: 30, display: 'flex', alignItems: 'center',
        }}>Remplir ces champs depuis Google Earth</summary>
        {/* `listStyle` explicite : un reset global mange les marqueurs, et une
            procédure en trois étapes sans ses numéros n'est plus une procédure. */}
        <ol style={{
          margin: '12px 0 0', paddingLeft: 22, fontSize: 13, lineHeight: 1.7,
          color: 'var(--ink)', listStyle: 'decimal outside',
        }}>
          <li>
            Posez un repère et <strong>copiez ses coordonnées</strong> — les deux formats
            sont acceptés, <code>50°52&apos;47&quot;N 1°38&apos;46&quot;E</code> comme{' '}
            <code>50.8798, 1.6464</code>.
          </li>
          <li>
            Lisez l’<strong>altitude du terrain</strong> affichée en bas de la fenêtre, et
            mettez-la dans « Altitude du sol ».
          </li>
          <li>
            Ajoutez <strong>à part</strong> la hauteur de l’œil (votre taille, ou le
            trépied) et la hauteur propre de l’ouvrage visé — 30 m pour un phare, 8 m pour
            une maison. Google Earth ne les connaît pas.
          </li>
        </ol>
        <p style={{
          margin: '12px 0 0', fontSize: 12.5, lineHeight: 1.65, color: 'var(--ink-soft)',
          padding: '10px 12px', borderRadius: 6, background: 'var(--bg)',
          borderLeft: `3px solid ${dash.saffron}`,
        }}>
          <strong>Deux pièges.</strong> Mettre l’altitude du sol dans le champ de hauteur —
          ou l’inverse — décale le résultat sans que rien ne le signale : c’est pour cela que
          les champs sont séparés. Et les altitudes doivent être comptées{' '}
          <strong>au-dessus du niveau moyen de la mer</strong>, comme les donnent Google Earth
          et l’IGN. Une hauteur ellipsoïdale brute de récepteur GNSS diffère de près de 50 m
          en France, et l’écart passerait entier dans le calcul.
        </p>
      </details>

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

      {sim && <ResultatVisee sim={sim} />}
    </div>
  );
}
