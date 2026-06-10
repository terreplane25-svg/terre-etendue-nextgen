"use client";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div style={{ width: '100%', height: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#FAFBFC', borderRadius: 12, border: '1px solid #E8EAED' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ width: 20, height: 20, border: '2px solid #8B7EC8', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }} />
        <p style={{ fontSize: 12, color: '#8B8F96' }}>Chargement du graphe…</p>
      </div>
    </div>
  ),
});

export default function NexusClient() {
  return (
    <div style={{ minHeight: '100vh', padding: '40px 0 80px' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <div style={{ width: 4, height: 28, background: '#8B7EC8', borderRadius: 2 }} />
            <h1 style={{ fontSize: 28, fontWeight: 800, color: '#1A1D23', letterSpacing: '-0.02em' }}>Le Nexus</h1>
          </div>
          <p style={{ fontSize: 15, color: '#8B8F96', maxWidth: 560 }}>
            Chaque point est un article. Chaque lien une connexion intellectuelle.
            Explorez le réseau de connaissances.
          </p>
        </div>
        <NexusGraph />
      </div>
    </div>
  );
}
