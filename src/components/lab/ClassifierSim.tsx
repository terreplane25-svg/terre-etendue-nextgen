'use client';
import { useState, useCallback } from 'react';

interface Statement {
  id: number;
  text: string;
  correct: 'fait' | 'modele' | 'hypothese';
  explanation: string;
  source?: string;
}

const STATEMENT_SETS: { label: string; statements: Statement[] }[] = [
  {
    label: 'Physique & Astronomie',
    statements: [
      { id: 1, text: 'Les objets lâchés dans l\'air tombent vers le sol.', correct: 'fait', explanation: 'C\'est une observation directe, reproductible par tout le monde, partout sur Terre.', source: 'Observable' },
      { id: 2, text: 'La gravité est une force qui attire les masses entre elles.', correct: 'modele', explanation: 'C\'est le modèle de Newton (1687). Einstein a proposé un modèle différent : la courbure de l\'espace-temps. Le mécanisme exact reste étudié.', source: 'Newton, Principia, 1687' },
      { id: 3, text: 'L\'Univers a 13,8 milliards d\'années.', correct: 'modele', explanation: 'C\'est une estimation du modèle ΛCDM (Big Bang). Des observations récentes du télescope James Webb questionnent cette valeur.', source: 'Planck Collaboration, 2018' },
      { id: 4, text: 'L\'eau bout à 100°C au niveau de la mer.', correct: 'fait', explanation: 'C\'est mesurable, reproductible et vérifié indépendamment des millions de fois. Un fait expérimental.', source: 'Mesurable en classe' },
      { id: 5, text: 'La matière noire constitue 27% de l\'Univers.', correct: 'hypothese', explanation: 'La matière noire n\'a jamais été détectée directement. C\'est une hypothèse introduite pour expliquer les courbes de rotation des galaxies.', source: 'Rubin & Ford, 1970' },
      { id: 6, text: 'La Terre tourne autour du Soleil en 365,25 jours.', correct: 'modele', explanation: 'Dans le modèle héliocentrique, oui. Le modèle géocentrique décrivait les mêmes observations autrement. Les prédictions sont équivalentes pour les phénomènes quotidiens.', source: 'Copernic, De Revolutionibus, 1543' },
      { id: 7, text: 'Un objet moins dense que l\'eau flotte.', correct: 'fait', explanation: 'C\'est vérifiable en classe en 10 secondes. Le principe d\'Archimède le décrit depuis 2 300 ans.', source: 'Archimède, ~250 av. J.-C.' },
      { id: 8, text: 'L\'énergie sombre accélère l\'expansion de l\'Univers.', correct: 'hypothese', explanation: 'L\'énergie sombre est une hypothèse pour expliquer l\'accélération observée de l\'expansion. Sa nature est totalement inconnue.', source: 'Perlmutter et al., 1998' },
    ],
  },
  {
    label: 'Sciences de la vie',
    statements: [
      { id: 20, text: 'Les êtres vivants sont composés de cellules.', correct: 'fait', explanation: 'Observable au microscope. Vérifié sur tous les organismes connus depuis Hooke (1665).', source: 'Robert Hooke, Micrographia, 1665' },
      { id: 21, text: 'L\'homme descend du singe.', correct: 'modele', explanation: 'Formulation incorrecte d\'un modèle. La théorie de l\'évolution propose un ancêtre commun, pas une descendance directe.', source: 'Darwin, 1859' },
      { id: 22, text: 'Les plantes utilisent la lumière pour produire du glucose.', correct: 'fait', explanation: 'La photosynthèse est mesurable : on peut quantifier le CO₂ absorbé et l\'O₂ produit. Fait expérimental reproductible.', source: 'Mesurable en classe' },
      { id: 23, text: 'La vie est apparue spontanément dans une soupe primordiale.', correct: 'hypothese', explanation: 'L\'abiogenèse reste une hypothèse. Personne n\'a réussi à créer la vie à partir de matière inerte en laboratoire.', source: 'Oparin, 1924 / Miller, 1953' },
      { id: 24, text: 'L\'ADN contient le code génétique.', correct: 'fait', explanation: 'La structure de l\'ADN est observable (cristallographie, séquençage). Son rôle de support de l\'information génétique est démontré expérimentalement.', source: 'Watson & Crick, 1953' },
      { id: 25, text: 'Les mutations génétiques sont le moteur principal de l\'évolution.', correct: 'modele', explanation: 'C\'est le modèle néo-darwinien. D\'autres mécanismes existent : dérive génétique, transfert horizontal, épigénétique. Le débat est actif.', source: 'Synthèse moderne, ~1940' },
      { id: 26, text: 'Un cœur humain bat environ 100 000 fois par jour.', correct: 'fait', explanation: 'Mesurable avec un simple stéthoscope. ~70 bpm × 1440 min ≈ 100 800 battements.', source: 'Mesurable' },
      { id: 27, text: 'La conscience émerge de l\'activité neuronale.', correct: 'hypothese', explanation: 'Aucune expérience n\'a démontré comment l\'activité neuronale produit la conscience subjective. C\'est le "hard problem" de la philosophie de l\'esprit.', source: 'Chalmers, 1995' },
    ],
  },
  {
    label: 'Géosciences',
    statements: [
      { id: 40, text: 'Les aimants ont un pôle nord et un pôle sud.', correct: 'fait', explanation: 'Observable et reproductible. Coupez un aimant : chaque morceau a deux pôles.', source: 'Observable' },
      { id: 41, text: 'Le champ magnétique terrestre est généré par un noyau de fer liquide en rotation.', correct: 'modele', explanation: 'C\'est le modèle de la géodynamo. Personne n\'a observé directement le noyau terrestre — c\'est un modèle basé sur des mesures sismiques indirectes.', source: 'Modèle de Glatzmaier & Roberts, 1995' },
      { id: 42, text: 'Ératosthène a prouvé que la Terre est ronde.', correct: 'modele', explanation: 'Ératosthène a mesuré un angle entre deux ombres et calculé une circonférence — en supposant un Soleil très lointain et une Terre sphérique. Le résultat dépend du modèle choisi.', source: 'Ératosthène, ~240 av. J.-C.' },
      { id: 43, text: 'Les volcans émettent de la lave, des cendres et des gaz.', correct: 'fait', explanation: 'Observable directement. Documenté par des milliers de témoins et instruments à chaque éruption.', source: 'Observable' },
      { id: 44, text: 'Les continents se déplacent de quelques centimètres par an.', correct: 'modele', explanation: 'La tectonique des plaques est un modèle. Les mesures GPS montrent des mouvements relatifs, mais l\'interprétation (plaques rigides sur un manteau visqueux) est un modèle.', source: 'Wegener, 1912 / GPS moderne' },
      { id: 45, text: 'L\'eau gèle à 0°C à pression atmosphérique normale.', correct: 'fait', explanation: 'Mesurable par n\'importe qui avec un thermomètre et un congélateur. Fait reproductible.', source: 'Mesurable en classe' },
      { id: 46, text: 'Le pétrole provient de la décomposition d\'organismes marins il y a des millions d\'années.', correct: 'modele', explanation: 'C\'est la théorie biogénique, dominante. La théorie abiogénique (origine minérale) existe aussi et a des partisans sérieux, notamment en Russie.', source: 'Théorie biogénique vs abiogénique' },
      { id: 47, text: 'L\'expérience de Michelson-Morley n\'a détecté aucun mouvement de la Terre dans l\'éther.', correct: 'fait', explanation: 'Le résultat expérimental est un fait : le résultat fut nul. L\'interprétation (pas d\'éther, ou contraction de Lorentz, ou Terre immobile) relève du modèle.', source: 'Michelson & Morley, 1887' },
    ],
  },
];

const CATEGORIES = {
  fait: { label: 'Fait', color: '#3D9E7C', icon: '✓', desc: 'Observable, mesurable, reproductible' },
  modele: { label: 'Modèle', color: '#3B8FD4', icon: '◈', desc: 'Description explicative, peut changer' },
  hypothese: { label: 'Hypothèse', color: '#D4943A', icon: '?', desc: 'Non vérifié, en attente de confirmation' },
};

type Category = 'fait' | 'modele' | 'hypothese';

function shuffleArray<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function ClassifierSim() {
  const [setIndex, setSetIndex] = useState(0);
  const [statements, setStatements] = useState<Statement[]>(() => shuffleArray(STATEMENT_SETS[0].statements));
  const [answers, setAnswers] = useState<Record<number, Category>>({});
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  const [showResults, setShowResults] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentStatement = statements[currentIndex];
  const totalAnswered = Object.keys(answers).length;
  const totalCorrect = Object.entries(answers).filter(([id, cat]) => {
    const s = statements.find(st => st.id === Number(id));
    return s && s.correct === cat;
  }).length;

  const handleSetChange = useCallback((idx: number) => {
    setSetIndex(idx);
    setStatements(shuffleArray(STATEMENT_SETS[idx].statements));
    setAnswers({});
    setRevealed({});
    setShowResults(false);
    setCurrentIndex(0);
  }, []);

  const handleAnswer = useCallback((category: Category) => {
    if (!currentStatement || answers[currentStatement.id]) return;
    setAnswers(prev => ({ ...prev, [currentStatement.id]: category }));
    setRevealed(prev => ({ ...prev, [currentStatement.id]: true }));
  }, [currentStatement, answers]);

  const handleNext = useCallback(() => {
    if (currentIndex < statements.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setShowResults(true);
    }
  }, [currentIndex, statements.length]);

  const handleReset = useCallback(() => {
    setStatements(shuffleArray(STATEMENT_SETS[setIndex].statements));
    setAnswers({});
    setRevealed({});
    setShowResults(false);
    setCurrentIndex(0);
  }, [setIndex]);

  const isCorrect = currentStatement && answers[currentStatement.id] === currentStatement.correct;
  const isAnswered = currentStatement && answers[currentStatement.id] !== undefined;

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>

      {/* Set selector */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {STATEMENT_SETS.map((s, i) => (
          <button
            key={i}
            onClick={() => handleSetChange(i)}
            style={{
              padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border)',
              background: i === setIndex ? '#2B7A5F' : 'var(--card)',
              color: i === setIndex ? '#fff' : 'var(--ink-soft)',
              fontSize: 13, fontWeight: 600, cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Progress */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 12, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
            {totalAnswered}/{statements.length} classées
          </span>
          <span style={{ fontSize: 12, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
            {totalCorrect} correcte{totalCorrect > 1 ? 's' : ''}
          </span>
        </div>
        <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 2, transition: 'width 0.3s',
            width: `${(totalAnswered / statements.length) * 100}%`,
            background: `linear-gradient(90deg, #3D9E7C, #3B8FD4, #D4943A)`,
          }} />
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 28 }}>
        {(Object.entries(CATEGORIES) as [Category, typeof CATEGORIES.fait][]).map(([key, cat]) => (
          <div key={key} style={{
            padding: '10px 12px', borderRadius: 8, background: `${cat.color}10`,
            border: `1px solid ${cat.color}25`, textAlign: 'center',
          }}>
            <div style={{ fontSize: 18, marginBottom: 4 }}>{cat.icon}</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: cat.color, marginBottom: 2 }}>{cat.label}</div>
            <div style={{ fontSize: 11, color: 'var(--ink-muted)', lineHeight: 1.35 }}>{cat.desc}</div>
          </div>
        ))}
      </div>

      {!showResults ? (
        <>
          {/* Statement card */}
          {currentStatement && (
            <div style={{
              background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12,
              padding: '32px 28px', marginBottom: 20, textAlign: 'center',
              minHeight: 160, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{ fontSize: 11, color: 'var(--ink-muted)', marginBottom: 12, fontFamily: "'JetBrains Mono', monospace" }}>
                Affirmation {currentIndex + 1}/{statements.length}
              </div>
              <div style={{
                fontSize: 19, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.45,
                maxWidth: 600,
              }}>
                « {currentStatement.text} »
              </div>
            </div>
          )}

          {/* Answer buttons */}
          {!isAnswered && currentStatement && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 20 }}>
              {(Object.entries(CATEGORIES) as [Category, typeof CATEGORIES.fait][]).map(([key, cat]) => (
                <button
                  key={key}
                  onClick={() => handleAnswer(key)}
                  style={{
                    padding: '16px 12px', borderRadius: 10,
                    background: 'var(--card)', border: `2px solid ${cat.color}30`,
                    cursor: 'pointer', transition: 'all 0.15s',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = cat.color;
                    e.currentTarget.style.background = `${cat.color}08`;
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = `${cat.color}30`;
                    e.currentTarget.style.background = 'var(--card)';
                  }}
                >
                  <span style={{ fontSize: 24 }}>{cat.icon}</span>
                  <span style={{ fontSize: 15, fontWeight: 700, color: cat.color }}>{cat.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Feedback */}
          {isAnswered && currentStatement && (
            <div style={{
              background: isCorrect ? '#3D9E7C10' : '#C45E6A10',
              border: `1px solid ${isCorrect ? '#3D9E7C30' : '#C45E6A30'}`,
              borderRadius: 10, padding: '20px 22px', marginBottom: 20,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <span style={{
                  fontSize: 14, fontWeight: 800,
                  color: isCorrect ? '#3D9E7C' : '#C45E6A',
                }}>
                  {isCorrect ? '✓ Correct !' : '✗ Pas tout à fait'}
                </span>
                <span style={{
                  fontSize: 12, fontWeight: 600,
                  color: CATEGORIES[currentStatement.correct].color,
                  padding: '2px 8px', borderRadius: 4,
                  background: `${CATEGORIES[currentStatement.correct].color}15`,
                }}>
                  → {CATEGORIES[currentStatement.correct].label}
                </span>
              </div>
              <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0, marginBottom: currentStatement.source ? 8 : 0 }}>
                {currentStatement.explanation}
              </p>
              {currentStatement.source && (
                <div style={{ fontSize: 11, color: 'var(--ink-muted)', fontStyle: 'italic', fontFamily: "'JetBrains Mono', monospace" }}>
                  Source : {currentStatement.source}
                </div>
              )}
            </div>
          )}

          {/* Next button */}
          {isAnswered && (
            <div style={{ textAlign: 'center' }}>
              <button
                onClick={handleNext}
                style={{
                  padding: '12px 32px', borderRadius: 8,
                  background: '#2B7A5F', color: '#fff',
                  fontSize: 14, fontWeight: 700, border: 'none', cursor: 'pointer',
                  transition: 'opacity 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.opacity = '0.85'; }}
                onMouseLeave={e => { e.currentTarget.style.opacity = '1'; }}
              >
                {currentIndex < statements.length - 1 ? 'Suivante →' : 'Voir les résultats'}
              </button>
            </div>
          )}
        </>
      ) : (
        /* Results */
        <div>
          <div style={{
            textAlign: 'center', padding: '28px 24px', marginBottom: 24,
            background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12,
          }}>
            <div style={{
              fontSize: 48, fontWeight: 900, marginBottom: 8,
              color: totalCorrect >= statements.length * 0.75 ? '#3D9E7C' : totalCorrect >= statements.length * 0.5 ? '#D4943A' : '#C45E6A',
              fontFamily: "'JetBrains Mono', monospace",
            }}>
              {totalCorrect}/{statements.length}
            </div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--ink)', marginBottom: 4 }}>
              {totalCorrect === statements.length ? 'Parfait ! Rigueur épistémologique exemplaire.' :
               totalCorrect >= statements.length * 0.75 ? 'Très bien ! Quelques nuances à revoir.' :
               totalCorrect >= statements.length * 0.5 ? 'Pas mal, mais la distinction fait/modèle mérite d\'être approfondie.' :
               'Les frontières entre fait, modèle et hypothèse sont plus subtiles qu\'on ne le pense.'}
            </div>
            <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>
              {STATEMENT_SETS[setIndex].label}
            </div>
          </div>

          {/* Review all */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 24 }}>
            {statements.map((s) => {
              const answer = answers[s.id];
              const correct = answer === s.correct;
              return (
                <div key={s.id} style={{
                  padding: '16px 18px', borderRadius: 8,
                  background: 'var(--card)', border: `1px solid ${correct ? '#3D9E7C25' : '#C45E6A25'}`,
                  borderLeft: `3px solid ${correct ? '#3D9E7C' : '#C45E6A'}`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 6 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)', lineHeight: 1.4, flex: 1 }}>
                      {s.text}
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                      {!correct && answer && (
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 4,
                          background: '#C45E6A15', color: '#C45E6A',
                          textDecoration: 'line-through',
                        }}>
                          {CATEGORIES[answer].label}
                        </span>
                      )}
                      <span style={{
                        fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 4,
                        background: `${CATEGORIES[s.correct].color}15`,
                        color: CATEGORIES[s.correct].color,
                      }}>
                        {CATEGORIES[s.correct].label}
                      </span>
                    </div>
                  </div>
                  <p style={{ fontSize: 12, color: 'var(--ink-muted)', lineHeight: 1.5, margin: 0 }}>
                    {s.explanation}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Reset */}
          <div style={{ textAlign: 'center' }}>
            <button
              onClick={handleReset}
              style={{
                padding: '12px 32px', borderRadius: 8,
                background: '#2B7A5F', color: '#fff',
                fontSize: 14, fontWeight: 700, border: 'none', cursor: 'pointer',
              }}
            >
              Recommencer
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
