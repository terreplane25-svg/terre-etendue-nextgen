'use client';

import React from 'react';

const SHIP = 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/bateau_horizon-removebg-preview.png';
const OCEAN = 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/mer_horizon.png';

interface Props { shipScale: number; showVignette: boolean; zoomLevel: number; }

export default function OceanScene({ shipScale, showVignette, zoomLevel }: Props) {
  const shipOpacity = Math.min(1, shipScale * 10);
  const shipBlur = Math.max(0, (0.3 - shipScale) * 5);
  const shipW = 25 + shipScale * 550;
  const shipH = shipW * 1.15;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
      {/* Ocean background */}
      <img src={OCEAN} alt="" style={{
        position: 'absolute', inset: 0, width: '100%', height: '100%',
        objectFit: 'cover', objectPosition: 'center 50%',
      }} />

      {/* Ship — transparent PNG, no blend mode, no color filter, original colors */}
      {shipScale > 0.003 && (
        <div style={{
          position: 'absolute',
          top: '59%',
          left: '50%',
          transform: 'translate(-50%, -100%)',
          width: shipW,
          height: shipH,
          opacity: shipOpacity,
          filter: shipBlur > 0.1 ? `blur(${shipBlur}px)` : 'none',
          pointerEvents: 'none',
          transition: 'none',
        }}>
          <img src={SHIP} alt="" style={{
            width: '100%', height: '100%',
            objectFit: 'contain',
            objectPosition: 'center bottom',
          }} />
        </div>
      )}

      {/* Telescope vignette */}
      {showVignette && (
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: `radial-gradient(circle at 50% 59%, transparent ${30 + zoomLevel * 28}%, rgba(0,0,0,${0.25 + zoomLevel * 0.3}) ${60 + zoomLevel * 18}%, rgba(0,0,0,0.8) 100%)`,
          opacity: Math.min(0.85, zoomLevel * 1.1),
        }} />
      )}

      {/* Crosshair */}
      {showVignette && zoomLevel > 0.08 && zoomLevel < 0.85 && (
        <div style={{
          position: 'absolute', top: '59%', left: '50%',
          transform: 'translate(-50%, -50%)', pointerEvents: 'none',
          opacity: Math.min(0.15, (zoomLevel - 0.08) * 0.5) * (1 - Math.max(0, (zoomLevel - 0.7) / 0.15)),
        }}>
          <div style={{
            width: 70 + zoomLevel * 150, height: 70 + zoomLevel * 150,
            border: '1px solid rgba(255,255,255,0.45)', borderRadius: '50%', position: 'relative',
          }}>
            <div style={{ position: 'absolute', top: '50%', left: '15%', right: '15%', height: 1, background: 'rgba(255,255,255,0.35)' }} />
            <div style={{ position: 'absolute', left: '50%', top: '15%', bottom: '15%', width: 1, background: 'rgba(255,255,255,0.35)' }} />
          </div>
        </div>
      )}

      {/* Zoom indicator */}
      {zoomLevel > 0.03 && (
        <div style={{
          position: 'absolute', bottom: 16, right: 20,
          fontSize: 13, color: 'rgba(255,255,255,0.35)',
          fontFamily: "'JetBrains Mono', monospace",
        }}>×{(1 + zoomLevel * 24).toFixed(0)}</div>
      )}
    </div>
  );
}
