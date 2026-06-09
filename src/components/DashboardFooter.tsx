import { getAllArticles } from '@/lib/articles';

export default function DashboardFooter() {
  const count = getAllArticles().length;
  return (
    <footer style={{ borderTop: '1px solid #eee', padding: '32px 24px', marginTop: 'auto', background: '#fafafa' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <span style={{ fontSize: 15, fontWeight: 800 }}>Terre Étendue <span style={{ color: '#7C6FC4' }}>Islam</span></span>
          <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>Revue indépendante de cosmologie · {new Date().getFullYear()}</div>
        </div>
        <div style={{ fontSize: 11, color: '#bbb', fontFamily: "'JetBrains Mono', monospace" }}>{count} publications · 450+ sources</div>
      </div>
    </footer>
  );
}
