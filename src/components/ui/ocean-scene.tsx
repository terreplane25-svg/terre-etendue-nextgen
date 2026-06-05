'use client';

import React from 'react';

const SHIP = 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/bateau_horizon.png';
const OCEAN = 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/mer_horizon.png';

interface Props { shipScale: number; showVignette: boolean; zoomLevel: number; }

export default function OceanScene({ shipScale, showVignette, zoomLevel }: Props) {
  const shipOpacity = Math.min(1, shipScale * 8);
  const shipBlur = Math.max(0, (0.4 - shipScale) * 5);
  const shipW = 30 + shipScale * 600;
  const shipH = shipW * 1.1;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
      {/* Ocean background */}
      <img src={OCEAN} alt="" style={{
        position: 'absolute', inset: 0, width: '100%', height: '100%',
        objectFit: 'cover', objectPosition: 'center 50%',
      }} />

      {/* Ship — black bg removed via mix-blend-mode: screen */}
      {shipScale > 0.003 && (
        <div style={{
          position: 'absolute',
          bottom: '42%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: shipW, height: shipH,
          mixBlendMode: 'screen' as any,
          opacity: shipOpacity,
          filter: `blur(${shipBlur}px)`,
          transition: 'none',
          pointerEvents: 'none',
        }}>
          <img src={SHIP} alt="" style={{
            width: '100%', height: '100%',
            objectFit: 'contain',
          }} />
        </div>
      )}

      {/* Telescope vignette */}
      {showVignette && (
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: `radial-gradient(circle at 50% 50%, transparent ${35 + zoomLevel * 25}%, rgba(0,0,0,${0.3 + zoomLevel * 0.25}) ${65 + zoomLevel * 15}%, rgba(0,0,0,0.75) 100%)`,
          opacity: Math.min(0.85, zoomLevel * 1.2),
        }} />
      )}

      {/* Crosshair */}
      {showVignette && zoomLevel > 0.05 && (
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)', pointerEvents: 'none',
          opacity: Math.min(0.18, zoomLevel * 0.3) * (1 - Math.max(0, (zoomLevel - 0.7) / 0.3)),
        }}>
          <div style={{
            width: 80 + zoomLevel * 140, height: 80 + zoomLevel * 140,
            border: '1px solid rgba(255,255,255,0.5)', borderRadius: '50%', position: 'relative',
          }}>
            <div style={{ position: 'absolute', top: '50%', left: '10%', right: '10%', height: 1, background: 'rgba(255,255,255,0.4)' }} />
            <div style={{ position: 'absolute', left: '50%', top: '10%', bottom: '10%', width: 1, background: 'rgba(255,255,255,0.4)' }} />
          </div>
        </div>
      )}

      {/* Zoom indicator */}
      {zoomLevel > 0.02 && (
        <div style={{
          position: 'absolute', bottom: 16, right: 20,
          fontSize: 13, color: 'rgba(255,255,255,0.3)',
          fontFamily: "'JetBrains Mono', monospace",
        }}>×{(1 + zoomLevel * 24).toFixed(0)}</div>
      )}
    </div>
  );
}
