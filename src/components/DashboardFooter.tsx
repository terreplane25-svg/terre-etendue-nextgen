import { getAllArticles } from '@/lib/articles';

export default function DashboardFooter() {
  const count = getAllArticles().length;
  return (
    <footer style={{ borderTop: '1px solid rgba(20,18,16,0.06)', padding: '40px 32px', marginTop: 'auto' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <span style={{ fontSize: 14, fontWeight: 800, letterSpacing: '-0.01em' }}>Terre Étendue <span style={{ color: '#7C6FC4', fontWeight: 600 }}>Islam</span></span>
          <div style={{ fontSize: 12, color: '#BAB5AC', marginTop: 4 }}>Revue indépendante de cosmologie · Fondée 2024</div>
        </div>
        <div style={{ fontSize: 11, color: '#BAB5AC', fontFamily: "'JetBrains Mono', monospace" }}>
          {count} publications · 450+ sources · 3 modèles 3D
        </div>
      </div>
    </footer>
  );
}
