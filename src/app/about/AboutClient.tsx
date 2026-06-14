'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';

const fade = (i: number) => ({ initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 }, transition: { delay: 0.1 + i * 0.06 } });

const PRINCIPES = [
  { icon: '🔍', title: 'Distinguer le fait de l\'interprétation', desc: 'La chute d\'un objet est un fait. L\'appeler « gravité » est une interprétation. Nous documentons les faits et identifions les interprétations comme telles.', color: dash.lavender },
  { icon: '🧪', title: 'Privilégier l\'expérience sur l\'observation', desc: 'Un test reproductible sur un lac a plus de poids qu\'une image satellite interprétée. L\'expérience que tout le monde peut refaire vaut plus que l\'observation que personne ne peut vérifier.', color: dash.cyan },
  { icon: '📖', title: 'Ne jamais plier la Révélation', desc: 'Le concordisme est une erreur méthodologique et théologique. Le Coran est muhaymin — dominant. Ses termes ont des sens précis, documentés par les Salaf et les dictionnaires classiques.', color: dash.saffron },
  { icon: '🎯', title: 'Appeler les choses par leur nom', desc: 'Une hypothèse est une hypothèse. Un consensus est un consensus, pas une preuve. Une inférence est une inférence, pas une mesure. Nous n\'utilisons pas de vocabulaire trompeur.', color: dash.opal },
];

const SOURCES = [
  { icon: '🕌', label: 'Sources islamiques primaires', detail: 'Coran, hadith authentiques, tafsīr classiques, dictionnaires arabes' },
  { icon: '📄', label: 'Revues à comité de lecture', detail: 'Physique, géodésie, optique, géophysique — auteurs et références citées' },
  { icon: '🔧', label: 'Données d\'ingénierie', detail: 'Canaux, pipelines, infrastructures ferroviaires — construits sur modèles plans' },
];

const FAQ = [
  { q: 'Êtes-vous un groupe complotiste ?', a: 'Non. Nous citons nos sources, reconnaissons les arguments adverses, identifions ce qui reste ouvert, et invitons à la vérification — pas à la croyance aveugle.' },
  { q: 'Quel rapport avec l\'Islam ?', a: 'Le Coran et la Sunna décrivent une cosmologie cohérente qui a été la compréhension unanime des Compagnons et des grands savants classiques pendant plus de mille ans. Nous prenons cette parole au sérieux.' },
  { q: 'Pourquoi remettre en question le modèle officiel ?', a: 'Parce qu\'il repose sur des hypothèses — certaines solides, d\'autres fragiles, d\'autres non vérifiables. Les tensions internes (matière noire, énergie noire, constante de Hubble) sont documentées dans la littérature scientifique.' },
  { q: 'Avez-vous toutes les réponses ?', a: 'Non, et nous le disons explicitement. Nous identifions ce qui reste ouvert et les pistes de recherche à explorer. C\'est la marque d\'une démarche sincère, pas d\'une faiblesse.' },
  { q: 'Comment puis-je vérifier par moi-même ?', a: 'La plupart de nos observations sont reproductibles : test laser sur un lac, zoom sur un objet « disparu sous l\'horizon », horizon au niveau des yeux, boussole. Voir notre section État des lieux.' },
];

const SOCIALS = [
  { icon: '▶', label: 'YouTube', href: 'https://www.youtube.com/@TERREETENDUE', color: '#FF0000' },
  { icon: '◉', label: 'Odysee', href: 'https://odysee.com/@terreetendue', color: '#E84A8A' },
  { icon: '✈', label: 'Telegram (canal)', href: 'https://t.me/LATERREETENDUE', color: '#0088CC' },
  { icon: '💬', label: 'Telegram (groupe)', href: 'https://t.me/terre_etendue', color: '#0088CC' },
  { icon: '♪', label: 'TikTok', href: 'https://tiktok.com/@terreetendue1', color: '#111' },
];

const ETHIQUE = [
  { title: 'Honnêteté', desc: 'Quand un argument du modèle officiel est solide, nous le disons.' },
  { title: 'Sources vérifiables', desc: 'Chaque affirmation est accompagnée de sa source. Nous ne demandons à personne de nous croire sur parole.' },
  { title: 'Respect du texte sacré', desc: 'Le Coran n\'a pas besoin d\'être « sauvé » par la science moderne.' },
  { title: 'Respect de l\'adversaire', desc: 'Nous ne méprisons pas ceux qui pensent différemment. Nous distinguons la personne de l\'argument.' },
  { title: 'Reconnaissance des limites', desc: 'Nous identifions ce que nous n\'avons pas résolu et les pistes ouvertes.' },
];

export default function AboutClient() {
  return (
    <div>
      <SectionHeader pillar="À PROPOS" pillarNum="06" subtitle="Qui sommes-nous" title="Terre Étendue Islam" color={dash.opal} count={5} countLabel="sections — manifeste, méthodologie, FAQ, éthique et liens" />

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 80px' }}>

        {/* ── MANIFESTE ── */}
        <motion.section {...fade(0)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.saffron }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>Manifeste</h2>
          </div>

          <div className="dash-card" style={{ padding: '32px 28px' }}>
            <p style={{ fontSize: 17, fontWeight: 600, color: dash.ink, lineHeight: 1.6, marginBottom: 20 }}>
              Ce site existe parce qu&apos;une question mérite d&apos;être posée — et qu&apos;elle ne l&apos;est presque jamais.
            </p>

            <div style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75 }}>
              <p style={{ marginBottom: 16 }}>
                Le modèle cosmologique enseigné dans les écoles, les universités et les médias est présenté comme un fait établi. Or il repose sur des hypothèses — certaines solides, d&apos;autres fragiles, d&apos;autres non vérifiables.
              </p>
              <p style={{ marginBottom: 16 }}>
                Parallèlement, le Coran et la Sunna décrivent une cosmologie cohérente qui a été la compréhension unanime des Compagnons, des Tābiʿūn et des grands savants classiques pendant plus de mille ans. Cette compréhension a été progressivement marginalisée sous la pression du concordisme.
              </p>
              <p style={{ marginBottom: 0 }}>
                <strong>Ce site est un espace où les deux paradigmes sont examinés avec la même rigueur.</strong>
              </p>
            </div>

            <div style={{ marginTop: 24, padding: '20px 24px', background: dash.opalSoft, borderRadius: 8, borderLeft: `4px solid ${dash.opal}` }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: dash.opal, marginBottom: 6 }}>Ce que nous sommes</div>
              <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }}>
                Des musulmans qui prennent au sérieux les mots du Coran et de la Sunna, et qui prennent au sérieux la méthode scientifique. Nous ne pensons pas que les deux soient en contradiction — à condition de ne pas plier l&apos;un pour le faire coïncider avec l&apos;autre.
              </p>
            </div>
          </div>
        </motion.section>

        {/* ── MÉTHODOLOGIE — 4 CARDS ── */}
        <motion.section {...fade(1)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.cyan }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>Méthodologie</h2>
          </div>
          <p style={{ fontSize: 15, color: dash.inkSoft, lineHeight: 1.6, marginBottom: 24 }}>
            Quatre principes guident chaque article, chaque argument, chaque conclusion.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
            {PRINCIPES.map((p, i) => (
              <motion.div key={i} {...fade(i + 2)} className="dash-card" style={{ padding: '24px 22px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ fontSize: 22 }}>{p.icon}</span>
                  <span style={{
                    fontSize: 10, fontWeight: 700, color: p.color, letterSpacing: '0.1em',
                    padding: '3px 8px', border: `1px solid ${p.color}30`, borderRadius: 3,
                    fontFamily: dash.fontMono,
                  }}>PRINCIPE {i + 1}</span>
                </div>
                <div style={{ fontSize: 16, fontWeight: 750, color: dash.ink, marginBottom: 8, lineHeight: 1.35 }}>{p.title}</div>
                <p style={{ fontSize: 14, color: dash.inkSoft, lineHeight: 1.6, margin: 0 }}>{p.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Sources */}
          <div style={{ marginTop: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: dash.ink, marginBottom: 12 }}>Sources utilisées</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {SOURCES.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'var(--bg)', borderRadius: 8 }}>
                  <span style={{ fontSize: 18 }}>{s.icon}</span>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 650, color: dash.ink }}>{s.label}</div>
                    <div style={{ fontSize: 12, color: dash.inkMuted }}>{s.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* ── ÉTAT DES LIEUX ── */}
        <motion.section {...fade(2)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.lavender }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>État des lieux</h2>
          </div>

          <div className="dash-card" style={{ padding: '28px 24px' }}>
            <p style={{ fontSize: 15, color: dash.inkSoft, lineHeight: 1.6, marginBottom: 20 }}>
              Ce que nous avons établi. Ce qui reste ouvert. Ce que vous pouvez vérifier vous-même.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 24 }}>
              {[
                { num: '23', label: 'Articles documentés', color: dash.lavender },
                { num: '18', label: 'Résultats établis', color: dash.opal },
                { num: '4', label: 'Questions ouvertes', color: dash.saffron },
                { num: '6', label: 'Expériences reproductibles', color: dash.cyan },
              ].map((s, i) => (
                <div key={i} style={{ textAlign: 'center', padding: '16px 12px', background: 'var(--bg)', borderRadius: 8 }}>
                  <div style={{ fontSize: 28, fontWeight: 900, color: s.color, fontFamily: dash.fontMono }}>{s.num}</div>
                  <div style={{ fontSize: 12, color: dash.inkMuted, fontWeight: 600, marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>

            <Link href="/article/etat-des-lieux-ou-en-sommes-nous" style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              fontSize: 14, fontWeight: 650, color: dash.lavender,
            }}>
              Lire l&apos;état des lieux complet →
            </Link>
          </div>
        </motion.section>

        {/* ── ÉTHIQUE ── */}
        <motion.section {...fade(3)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.opal }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>Éthique intellectuelle</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {ETHIQUE.map((e, i) => (
              <motion.div key={i} {...fade(i + 3)} style={{
                display: 'flex', alignItems: 'flex-start', gap: 14,
                padding: '16px 20px', background: 'var(--bg)', borderRadius: 10,
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 6, background: `${dash.opal}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, fontWeight: 800, color: dash.opal, fontFamily: dash.fontMono, flexShrink: 0,
                }}>{i + 1}</div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: dash.ink, marginBottom: 3 }}>{e.title}</div>
                  <div style={{ fontSize: 14, color: dash.inkSoft, lineHeight: 1.55 }}>{e.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ── FAQ ── */}
        <motion.section {...fade(4)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.rose }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>Questions fréquentes</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {FAQ.map((f, i) => (
              <motion.div key={i} {...fade(i + 4)} className="dash-card" style={{ padding: '22px 24px' }}>
                <div style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginBottom: 8 }}>{f.q}</div>
                <p style={{ fontSize: 14, color: dash.inkSoft, lineHeight: 1.65, margin: 0 }}>{f.a}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ── CITATION ── */}
        <motion.section {...fade(5)} style={{ marginTop: 48 }}>
          <div style={{
            padding: '32px 28px', background: '#0D1528', borderRadius: 12,
            textAlign: 'center',
          }}>
            <p style={{ fontSize: 16, fontWeight: 600, color: '#C8D8E8', lineHeight: 1.6, marginBottom: 16 }}>
              « La vérité n&apos;a pas besoin d&apos;être protégée — elle a besoin d&apos;être examinée. »
            </p>
            <div style={{ fontSize: 18, color: dash.saffron, lineHeight: 1.8, fontFamily: dash.fontArabic, marginBottom: 8 }}>
              أَفَلَا يَنظُرُونَ إِلَى ٱلْإِبِلِ كَيْفَ خُلِقَتْ ۝ وَإِلَى ٱلسَّمَآءِ كَيْفَ رُفِعَتْ
            </div>
            <div style={{ fontSize: 18, color: dash.saffron, lineHeight: 1.8, fontFamily: dash.fontArabic, marginBottom: 12 }}>
              وَإِلَى ٱلْجِبَالِ كَيْفَ نُصِبَتْ ۝ وَإِلَى ٱلْأَرْضِ كَيْفَ سُطِحَتْ
            </div>
            <p style={{ fontSize: 13, color: '#607890', lineHeight: 1.6, margin: 0 }}>
              « Ne considèrent-ils pas les chameaux, comment ils ont été créés ; et le ciel, comment il a été élevé ; et les montagnes, comment elles ont été dressées ; et la terre, comment elle a été étendue ? »
            </p>
            <p style={{ fontSize: 11, color: '#4A5568', marginTop: 8, fontFamily: dash.fontMono }}>Sourate Al-Ghashiyah — 88:17-20</p>
          </div>
        </motion.section>

        {/* ── LIENS SOCIAUX ── */}
        <motion.section {...fade(6)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: dash.cyan }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em' }}>Rejoignez-nous</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
            {SOCIALS.map((s, i) => (
              <a key={i} href={s.href} target="_blank" rel="noopener noreferrer" className="dash-card" style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '16px 20px',
                cursor: 'pointer',
              }}>
                <span style={{ fontSize: 20, width: 36, height: 36, borderRadius: 8, background: `${s.color}10`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{s.icon}</span>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: dash.ink }}>{s.label}</div>
                  <div style={{ fontSize: 11, color: dash.inkMuted }}>Suivre →</div>
                </div>
              </a>
            ))}
          </div>
        </motion.section>

      </div>
    </div>
  );
}
