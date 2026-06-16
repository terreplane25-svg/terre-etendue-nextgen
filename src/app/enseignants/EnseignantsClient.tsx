'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

const fade = (i: number) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: 0.08 + i * 0.06 },
});

const ACCENT = '#2B7A5F';
const ACCENT_SOFT = '#2B7A5F12';

const FICHES = [
  {
    niveau: 'Cycle 3 (CM1–CM2–6e)',
    color: '#3B8FD4',
    items: [
      {
        titre: 'Le système solaire : modèles et histoire',
        programme: 'Sciences — Situer la Terre dans le système solaire',
        description: 'Comment les modèles du système solaire ont évolué, de Ptolémée à aujourd\'hui. Pourquoi on parle de "modèle" et pas de "vérité".',
        activite: 'Activité : construire deux maquettes (géocentrique et héliocentrique) et comparer.',
      },
      {
        titre: 'Fait et modèle : l\'exemple de l\'atome',
        programme: 'Sciences — La matière',
        description: 'Le modèle de l\'atome a changé 5 fois en 100 ans. C\'est un excellent cas pour montrer que les modèles évoluent.',
        activite: 'Activité : classer des affirmations en "fait observable" ou "modèle explicatif".',
      },
      {
        titre: 'L\'eau, la glace et la vapeur : faits reproductibles',
        programme: 'Sciences — Les états de la matière',
        description: 'Un cas où le fait et le modèle se rejoignent : les changements d\'état sont observables, mesurables, reproductibles. Exemple de certitude scientifique.',
        activite: 'Activité : mesurer les températures de changement d\'état en classe.',
      },
    ],
  },
  {
    niveau: 'Cycle 4 (5e–4e–3e)',
    color: '#8B7EC8',
    items: [
      {
        titre: 'La gravitation : ce que Newton a décrit — et ce qu\'il n\'a pas expliqué',
        programme: 'Physique-Chimie — La gravitation universelle',
        description: 'Newton a décrit le comportement des objets, pas le mécanisme. 300 ans plus tard, le mécanisme reste un sujet de recherche actif.',
        activite: 'Activité : lire la citation de Newton à Bentley (1693) et discuter en classe.',
        simulateur: { id: 'density', label: 'Simulateur de densité' },
      },
      {
        titre: 'Perspective et optique : pourquoi les objets semblent disparaître',
        programme: 'Physique-Chimie — La lumière, modèle de propagation',
        description: 'La diminution angulaire, la limite de résolution de l\'œil et la diffusion atmosphérique. Trois faits optiques vérifiables.',
        activite: 'Activité : mesurer la taille apparente d\'un objet à différentes distances.',
        simulateur: { id: 'perspective', label: 'Simulateur de perspective' },
      },
      {
        titre: 'L\'Univers : le modèle du Big Bang, ses forces et ses questions ouvertes',
        programme: 'Physique-Chimie — L\'Univers, structure et échelle',
        description: 'Le Big Bang explique beaucoup de choses. Mais 95% de l\'Univers prédit reste non détecté. Les cosmologistes eux-mêmes parlent de "crise".',
        activite: 'Activité : comparer deux articles de Nature (résultats Planck vs JWST).',
      },
      {
        titre: 'Mesurer sans toucher : comment estime-t-on les distances cosmiques ?',
        programme: 'Physique-Chimie — Distances dans l\'Univers',
        description: 'La parallaxe, les céphéides, les supernovæ : une chaîne de méthodes indirectes où chaque barreau dépend du précédent.',
        activite: 'Activité : expérience de parallaxe avec un doigt et les deux yeux.',
      },
      {
        titre: 'L\'évolution : théorie vivante et débats internes',
        programme: 'SVT — Évolution des espèces',
        description: 'Sélection naturelle, dérive génétique, équilibres ponctués, symbiogenèse. La théorie de l\'évolution évolue elle-même.',
        activite: 'Activité : comparer le modèle gradualiste de Darwin et les équilibres ponctués de Gould.',
      },
    ],
  },
];

const SIMULATEURS = [
  {
    id: 'perspective',
    titre: 'Comment la taille apparente change avec la distance',
    description: 'Deux modèles côte à côte : disparition par perspective vs occultation par courbure. L\'élève manipule et observe la différence.',
    usage: 'Montrer que la diminution angulaire fait "disparaître" un objet avant qu\'il ne soit physiquement caché. Question : "À partir de quelle distance ne voit-on plus le bateau ?"',
    programme: 'Cycle 4 — Optique, propagation de la lumière',
    icon: '👁️',
    color: '#8B7EC8',
  },
  {
    id: 'density',
    titre: 'Pourquoi les objets flottent ou coulent',
    description: 'Colonne de fluides interactive. Lâchez des objets de différentes densités et observez leur comportement.',
    usage: 'Démontrer que la flottabilité dépend de la densité relative, pas d\'une "force" mystérieuse. Question : "Pourquoi le bois flotte et le fer coule ?"',
    programme: 'Cycle 3/4 — La matière, masse et volume',
    icon: '⚗️',
    color: '#3D9E7C',
  },
  {
    id: 'visualfield',
    titre: 'Les limites de résolution de l\'œil humain',
    description: 'Taille angulaire, arc-minute et distance maximale de visibilité. Pourquoi un objet peut disparaître sans être "caché".',
    usage: 'Montrer que l\'œil a une limite physique de résolution (~1 arc-minute). Question : "À quelle distance un objet de 1m devient-il invisible ?"',
    programme: 'Cycle 4 — Optique, SVT (l\'œil)',
    icon: '🔬',
    color: '#C45E6A',
  },
  {
    id: 'curvature',
    titre: 'Calculateur de courbure théorique',
    description: 'Entrez une distance et un indice de réfraction. Le calculateur affiche la chute théorique attendue sur une sphère.',
    usage: 'Comparer la prédiction théorique avec des observations réelles (bâtiments, îles visibles). Question : "Ce résultat correspond-il à ce qu\'on observe ?"',
    programme: 'Cycle 4 — Mathématiques (géométrie), Physique',
    icon: '📐',
    color: '#3D9E7C',
  },
  {
    id: 'geo',
    titre: 'Le système solaire en 3D',
    description: '8 planètes avec orbites, anneaux de Saturne, vitesses réelles. Mode classique (héliocentrique) ou vortex.',
    usage: 'Visualiser les échelles et les vitesses. Montrer que "modèle" signifie "représentation", pas "photographie". Question : "Pourquoi y a-t-il deux modes d\'affichage ?"',
    programme: 'Cycle 3 — Le système solaire',
    icon: '🪐',
    color: '#D4943A',
  },
  {
    id: 'laser',
    titre: 'Expérience laser sur plan d\'eau',
    description: 'Simulation d\'une expérience laser sur une surface d\'eau calme. Trajectoire droite vs écart de courbure prédit.',
    usage: 'Montrer le protocole d\'une expérience reproductible. Question : "Comment pourriez-vous faire cette expérience vous-mêmes ?"',
    programme: 'Cycle 4 — Optique, propagation rectiligne',
    icon: '🔴',
    color: '#C45E6A',
  },
];

const FAQ = [
  {
    q: 'Ce site est-il "anti-science" ?',
    a: 'Non. Toutes les sources citées proviennent de la littérature scientifique mainstream : Nature, Science, The Astrophysical Journal, prix Nobel. L\'objectif est d\'enseigner la science avec plus de rigueur, pas de la rejeter.',
  },
  {
    q: 'Puis-je utiliser ces ressources en classe ?',
    a: 'Oui. Les fiches et simulateurs sont conçus pour être utilisés directement. Le livret enseignant est téléchargeable en PDF. Tout est sourcé et vérifiable.',
  },
  {
    q: 'Comment justifier cette approche devant mon inspecteur ?',
    a: 'La distinction fait/modèle/hypothèse est au programme de philosophie de terminale et fait partie des recommandations des didacticiens des sciences (Giordan, De Vecchi, Viennot). Vous ne faites que l\'introduire plus tôt — ce qui est une bonne pratique pédagogique.',
  },
  {
    q: 'Ce site a-t-il un biais idéologique ?',
    a: 'Ce site a un biais explicite : la rigueur épistémologique. Nous pensons qu\'un modèle doit être présenté comme un modèle, une hypothèse comme une hypothèse, et un fait comme un fait. C\'est tout.',
  },
  {
    q: 'Pourquoi certaines formulations des manuels sont-elles problématiques ?',
    a: 'Parce qu\'elles effacent la distinction entre ce qui est observé et ce qui est interprété. Un élève qui apprend que "la gravité est une force prouvée" ne comprend pas que le mécanisme est encore débattu — y compris dans les revues de physique les plus prestigieuses.',
  },
];

const REFERENCES = [
  { auteur: 'Karl Popper', titre: 'La Logique de la découverte scientifique', annee: '1934', note: 'Le critère de réfutabilité' },
  { auteur: 'Thomas Kuhn', titre: 'La Structure des révolutions scientifiques', annee: '1962', note: 'Les paradigmes' },
  { auteur: 'André Giordan', titre: 'Apprendre !', annee: '1998', note: 'Didactique des sciences' },
  { auteur: 'Gérard De Vecchi', titre: 'Enseigner le vrai ou le vraisemblable ?', annee: '2006', note: 'Pédagogie critique' },
  { auteur: 'Lee Smolin', titre: 'Rien ne va plus en physique', annee: '2006', note: 'Problèmes ouverts' },
  { auteur: 'Sabine Hossenfelder', titre: 'Lost in Math', annee: '2018', note: 'Biais esthétiques en physique' },
];

export default function EnseignantsClient() {
  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(135deg, #0D2818 0%, #1A3A2A 50%, #0D2818 100%)',
        padding: '64px 24px 56px',
        borderBottom: `3px solid ${ACCENT}`,
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase',
            color: ACCENT, marginBottom: 16,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Espace enseignants
          </div>
          <h1 style={{
            fontSize: 38, fontWeight: 900, color: '#E8EDF4', letterSpacing: '-0.02em',
            lineHeight: 1.2, marginBottom: 16,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            Enseigner la science<br />comme elle est réellement
          </h1>
          <p style={{
            fontSize: 17, color: '#8A95A8', lineHeight: 1.65, maxWidth: 620,
            margin: '0 auto 32px',
          }}>
            Ressources pédagogiques pour distinguer <strong style={{ color: '#C8D8E8' }}>fait</strong>, <strong style={{ color: '#C8D8E8' }}>modèle</strong> et <strong style={{ color: '#C8D8E8' }}>hypothèse</strong> en classe. Fiches alignées sur les programmes, simulateurs interactifs et guide téléchargeable.
          </p>

          <a
            href="/livret-enseignant.pdf"
            download
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 10,
              padding: '14px 28px', borderRadius: 8,
              background: ACCENT, color: '#fff',
              fontSize: 15, fontWeight: 700,
              textDecoration: 'none',
              transition: 'opacity 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.opacity = '0.9'; }}
            onMouseLeave={e => { e.currentTarget.style.opacity = '1'; }}
          >
            📄 Télécharger le livret enseignant (PDF)
          </a>
          <div style={{ fontSize: 12, color: '#607890', marginTop: 10, fontFamily: "'JetBrains Mono', monospace" }}>
            30 pages · 6 études de cas · 2 activités en classe · Sources vérifiables
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '48px 24px 80px' }}>

        {/* ═══ POURQUOI ═══ */}
        <motion.section {...fade(0)}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: ACCENT }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Pourquoi cet espace existe</h2>
          </div>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, padding: '28px 24px' }}>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, marginBottom: 16 }}>
              Les manuels scolaires présentent régulièrement des <strong style={{ color: 'var(--ink)' }}>modèles comme des faits</strong> et des <strong style={{ color: 'var(--ink)' }}>hypothèses comme des certitudes</strong>. Ce n'est pas un reproche — c'est un constat documenté par les didacticiens des sciences (Giordan, De Vecchi, Viennot).
            </p>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, marginBottom: 16 }}>
              Or la <strong style={{ color: 'var(--ink)' }}>distinction entre fait, modèle et hypothèse</strong> est le fondement même de la méthode scientifique. Un élève qui ne la maîtrise pas apprend un rapport d'autorité à la science — pas un rapport de méthode.
            </p>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, margin: 0 }}>
              Cet espace propose des outils concrets pour réintroduire cette rigueur dans l'enseignement — <strong style={{ color: 'var(--ink)' }}>sans rejeter les modèles enseignés</strong>, mais en les présentant pour ce qu'ils sont réellement.
            </p>
          </div>
        </motion.section>

        {/* ═══ LES 3 RÉFLEXES ═══ */}
        <motion.section {...fade(1)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3B8FD4' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Les 3 questions réflexes à enseigner</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
            {[
              { num: '1', q: 'Est-ce une observation ou une interprétation ?', ex: '« Les objets tombent » → observation. « C\'est la gravité » → interprétation.', color: '#3B8FD4' },
              { num: '2', q: 'Peut-on le vérifier soi-même ?', ex: '« L\'eau bout à 100°C » → oui. « Le Soleil est à 150M km » → non, c\'est un calcul.', color: '#8B7EC8' },
              { num: '3', q: 'Y a-t-il d\'autres explications possibles ?', ex: 'Chercher des alternatives n\'est pas du relativisme — c\'est la base de la méthode scientifique.', color: '#C45E6A' },
            ].map((r, i) => (
              <motion.div key={i} {...fade(i + 2)} style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
                padding: '22px 20px',
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8, background: `${r.color}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 14, fontWeight: 800, color: r.color,
                  fontFamily: "'JetBrains Mono', monospace", marginBottom: 12,
                }}>{r.num}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--ink)', marginBottom: 8, lineHeight: 1.35 }}>{r.q}</div>
                <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, margin: 0 }}>{r.ex}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ FICHES PAR NIVEAU ═══ */}
        <motion.section {...fade(2)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#8B7EC8' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Fiches par niveau et chapitre du programme</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 24, lineHeight: 1.6 }}>
            Chaque fiche est alignée sur le programme officiel (Éducation nationale — France). Utilisable telle quelle en séquence pédagogique.
          </p>

          {FICHES.map((groupe, gi) => (
            <div key={gi} style={{ marginBottom: 36 }}>
              <div style={{
                fontSize: 13, fontWeight: 700, color: groupe.color, letterSpacing: '0.04em',
                textTransform: 'uppercase', marginBottom: 14,
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                {groupe.niveau}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {groupe.items.map((fiche, fi) => (
                  <motion.div key={fi} {...fade(gi * 3 + fi + 3)} style={{
                    background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
                    padding: '22px 24px',
                  }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: groupe.color, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6, fontFamily: "'JetBrains Mono', monospace" }}>
                      {fiche.programme}
                    </div>
                    <div style={{ fontSize: 16, fontWeight: 750, color: 'var(--ink)', marginBottom: 8, lineHeight: 1.35 }}>
                      {fiche.titre}
                    </div>
                    <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, marginBottom: 10 }}>
                      {fiche.description}
                    </p>
                    <div style={{
                      fontSize: 13, color: ACCENT, fontWeight: 600,
                      padding: '8px 12px', background: ACCENT_SOFT, borderRadius: 6,
                      display: 'inline-block',
                    }}>
                      🧪 {fiche.activite}
                    </div>
                    {fiche.simulateur && (
                      <div style={{ marginTop: 10 }}>
                        <Link href={`/lab?tool=${fiche.simulateur.id}`} style={{
                          fontSize: 12, fontWeight: 600, color: '#8B7EC8',
                        }}>
                          🖥️ Ouvrir le {fiche.simulateur.label} →
                        </Link>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </motion.section>

        {/* ═══ SIMULATEURS ═══ */}
        <motion.section {...fade(3)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3D9E7C' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Simulateurs interactifs</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 24, lineHeight: 1.6 }}>
            6 outils manipulables en classe, sur tableau interactif ou en salle informatique. Chacun est accompagné d'une suggestion d'utilisation pédagogique.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 }}>
            {SIMULATEURS.map((sim, i) => (
              <motion.div key={sim.id} {...fade(i + 4)}>
                <Link href={`/lab?tool=${sim.id}`} style={{
                  display: 'block', background: 'var(--card)', border: '1px solid var(--border)',
                  borderRadius: 10, padding: '22px 20px', height: '100%',
                  transition: 'box-shadow 0.2s, border-color 0.2s',
                }}
                className="carousel-card"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <span style={{ fontSize: 22 }}>{sim.icon}</span>
                    <span style={{
                      fontSize: 10, fontWeight: 700, color: sim.color, letterSpacing: '0.08em',
                      padding: '3px 8px', border: `1px solid ${sim.color}30`, borderRadius: 4,
                      fontFamily: "'JetBrains Mono', monospace", textTransform: 'uppercase',
                    }}>
                      {sim.programme}
                    </span>
                  </div>
                  <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 6, lineHeight: 1.35 }}>
                    {sim.titre}
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, marginBottom: 10 }}>
                    {sim.description}
                  </p>
                  <div style={{
                    fontSize: 12, color: 'var(--ink-muted)', lineHeight: 1.5,
                    padding: '8px 10px', background: 'var(--bg)', borderRadius: 6,
                    borderLeft: `3px solid ${sim.color}`,
                  }}>
                    <strong style={{ color: 'var(--ink-soft)' }}>En classe :</strong> {sim.usage}
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ AVANT / APRÈS ═══ */}
        <motion.section {...fade(4)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#D4943A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Reformuler avec rigueur</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Même contenu. Même programme. Vocabulaire plus juste.
          </p>

          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '2px solid var(--border)' }}>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: '#C45E6A', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>
                ✗ Formulation courante
              </div>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: '#3D9E7C', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace", borderLeft: '1px solid var(--border)' }}>
                ✓ Formulation rigoureuse
              </div>
            </div>
            {[
              ['La gravité attire les objets.', 'Les objets tombent. Le modèle gravitationnel décrit ce comportement — le mécanisme exact reste étudié.'],
              ['La Terre tourne autour du Soleil.', 'Dans le modèle héliocentrique, la Terre tourne autour du Soleil. Ce modèle permet des prédictions précises.'],
              ['L\'Univers a 13,8 milliards d\'années.', 'Selon le modèle du Big Bang, l\'Univers aurait 13,8 milliards d\'années. Certaines observations récentes questionnent ce chiffre.'],
              ['Ératosthène a prouvé que la Terre est ronde.', 'Ératosthène a mesuré un angle et estimé une circonférence — dans le cadre d\'un modèle sphérique avec Soleil lointain.'],
              ['L\'homme descend du singe.', 'La théorie de l\'évolution propose que les humains et les grands singes partagent un ancêtre commun.'],
              ['Rien ne va plus vite que la lumière.', 'Selon la relativité d\'Einstein, rien ne dépasse la vitesse de la lumière. C\'est un postulat du modèle, confirmé expérimentalement.'],
            ].map(([avant, apres], i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '1px solid var(--border)' }}>
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55 }}>
                  {avant}
                </div>
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55, borderLeft: '1px solid var(--border)' }}>
                  {apres}
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ FAQ ═══ */}
        <motion.section {...fade(5)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#C45E6A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Questions fréquentes</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {FAQ.map((f, i) => (
              <motion.div key={i} {...fade(i + 6)} style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
                padding: '22px 24px',
              }}>
                <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 8 }}>{f.q}</div>
                <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0 }}>{f.a}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ RÉFÉRENCES ═══ */}
        <motion.section {...fade(6)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: 'var(--ink-ghost)' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Références</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
            {REFERENCES.map((r, i) => (
              <div key={i} style={{
                padding: '14px 18px', background: 'var(--bg)', borderRadius: 8,
                borderLeft: `3px solid var(--border)`,
              }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--ink)', marginBottom: 2 }}>{r.auteur}</div>
                <div style={{ fontSize: 13, color: 'var(--ink-soft)', fontStyle: 'italic' }}>{r.titre} ({r.annee})</div>
                <div style={{ fontSize: 11, color: 'var(--ink-muted)', marginTop: 4 }}>{r.note}</div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ CTA FINAL ═══ */}
        <motion.section {...fade(7)} style={{ marginTop: 56 }}>
          <div style={{
            padding: '36px 28px', background: 'linear-gradient(135deg, #0D2818, #1A3A2A)',
            borderRadius: 12, textAlign: 'center',
          }}>
            <p style={{ fontSize: 20, fontWeight: 700, color: '#E8EDF4', marginBottom: 8 }}>
              La science n'est pas un dogme. C'est une méthode.
            </p>
            <p style={{ fontSize: 15, color: '#8A95A8', marginBottom: 24, lineHeight: 1.6 }}>
              Enseignons la méthode.
            </p>
            <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
              <a
                href="/livret-enseignant.pdf"
                download
                style={{
                  padding: '12px 24px', borderRadius: 8,
                  background: ACCENT, color: '#fff',
                  fontSize: 14, fontWeight: 700, textDecoration: 'none',
                }}
              >
                📄 Télécharger le livret
              </a>
              <Link
                href="/lab"
                style={{
                  padding: '12px 24px', borderRadius: 8,
                  background: 'rgba(255,255,255,0.1)', color: '#C8D8E8',
                  border: '1px solid rgba(255,255,255,0.15)',
                  fontSize: 14, fontWeight: 700, textDecoration: 'none',
                }}
              >
                🖥️ Explorer les simulateurs
              </Link>
            </div>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
