import { getAllArticles } from '@/lib/articles';
import { dash } from '@/lib/design-tokens';

export default function DashboardFooter() {
  const count = getAllArticles().length;

  return (
    <footer style={{
      borderTop: `1px solid ${dash.borderSoft}`,
      background: dash.card,
      padding: '32px 24px',
      marginTop: 'auto',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, color: dash.ink, letterSpacing: '0.04em', fontFamily: dash.fontMain }}>
            TERRE ÉTENDUE ISLAM
          </div>
          <div style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMain, marginTop: 4 }}>
            Revue indépendante de cosmologie · Fondée 2024
          </div>
        </div>
        <div style={{ fontSize: 11, color: dash.inkGhost, fontFamily: dash.fontMono }}>
          {count} publications · 450+ sources · 3 modèles 3D
        </div>
      </div>
    </footer>
  );
}
