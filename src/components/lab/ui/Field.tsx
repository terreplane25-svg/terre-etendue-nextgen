'use client';
import { useState, useEffect } from 'react';

// Champs de saisie épurés partagés par les simulateurs du Lab.
// Remplacent les jauges slider : grand nombre lisible + unité, plus d'air.

// Facteurs vers le mètre (unité de base pour les conversions de longueur).
export const LEN_UNITS: Record<string, number> = {
  cm: 0.01, m: 1, km: 1000, mi: 1609.344, ft: 0.3048,
};
export const UNIT_LABEL: Record<string, string> = {
  cm: 'cm', m: 'm', km: 'km', mi: 'mi', ft: 'ft',
};

/** Affichage propre d'un nombre saisi (évite les flottants à rallonge). */
export function fmtNum(n: number): string {
  if (!isFinite(n)) return '0';
  const r = Math.round(n * 1000) / 1000;
  return String(r);
}

function InfoDot({ hint }: { hint: string }) {
  return (
    <span title={hint} style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: 13, height: 13, borderRadius: '50%', border: '1px solid #46566e',
      color: '#8499b3', fontSize: 9, fontFamily: 'monospace', cursor: 'help', lineHeight: 1,
    }}>i</span>
  );
}

// ─── Champ longueur avec sélecteur d'unité ───
export function LengthField({
  label, value, onChange, canonical, units, min, max, accent = '#00C8FF', hint,
}: {
  label: string; value: number; onChange: (v: number) => void;
  canonical: string; units: string[]; min: number; max: number;
  accent?: string; hint?: string;
}) {
  const [unit, setUnit] = useState(units[0]);
  const [focused, setFocused] = useState(false);
  const toDisplay = (v: number, u: string) => v * LEN_UNITS[canonical] / LEN_UNITS[u];
  const toCanonical = (d: number, u: string) => d * LEN_UNITS[u] / LEN_UNITS[canonical];
  const [text, setText] = useState(() => fmtNum(toDisplay(value, units[0])));

  // Resynchronise hors-focus (presets, changement d'unité) sans écraser la saisie.
  useEffect(() => { if (!focused) setText(fmtNum(toDisplay(value, unit))); }, [value, unit, focused]); // eslint-disable-line react-hooks/exhaustive-deps

  const commit = (raw: string) => {
    setText(raw);
    const d = parseFloat(raw.replace(',', '.'));
    if (!isNaN(d)) onChange(Math.max(min, Math.min(max, toCanonical(d, unit))));
  };

  return (
    <div style={{
      background: '#0A1020', border: `1px solid ${focused ? accent + '80' : '#1c2942'}`,
      borderRadius: 10, padding: '13px 15px', transition: 'border-color 0.15s ease',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 9 }}>
        <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#8499b3', letterSpacing: '0.12em', textTransform: 'uppercase' }}>{label}</span>
        {hint && <InfoDot hint={hint} />}
      </div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        background: '#050A12', border: '1px solid #1c2942', borderRadius: 8,
        padding: '8px 10px 8px 12px',
      }}>
        <input
          type="text" inputMode="decimal" value={text}
          onChange={e => commit(e.target.value)}
          onFocus={() => setFocused(true)} onBlur={() => { setFocused(false); setText(fmtNum(toDisplay(value, unit))); }}
          style={{ flex: 1, minWidth: 0, background: 'transparent', border: 'none', outline: 'none', color: accent, fontSize: 20, fontWeight: 700, fontFamily: 'monospace' }}
        />
        {units.length > 1 ? (
          <select value={unit} onChange={e => setUnit(e.target.value)}
            style={{ background: '#0A1020', border: '1px solid #283750', borderRadius: 6, color: '#8499b3', fontSize: 13, fontFamily: 'monospace', padding: '4px 6px', cursor: 'pointer', outline: 'none' }}>
            {units.map(u => <option key={u} value={u}>{UNIT_LABEL[u]}</option>)}
          </select>
        ) : (
          <span style={{ fontSize: 13, fontFamily: 'monospace', color: '#8499b3', paddingRight: 4 }}>{UNIT_LABEL[unit]}</span>
        )}
      </div>
    </div>
  );
}

// ─── Champ sans dimension (k, °C, %, compte, gradient…) ───
export function PlainField({
  label, value, onChange, min, max, unit, accent = '#00C8FF', hint, compact,
}: {
  label: string; value: number; onChange: (v: number) => void;
  min: number; max: number; unit: string; accent?: string; hint?: string; compact?: boolean;
}) {
  const [focused, setFocused] = useState(false);
  const [text, setText] = useState(() => fmtNum(value));
  useEffect(() => { if (!focused) setText(fmtNum(value)); }, [value, focused]);
  const commit = (raw: string) => {
    setText(raw);
    const v = parseFloat(raw.replace(',', '.'));
    if (!isNaN(v)) onChange(Math.max(min, Math.min(max, v)));
  };
  return (
    <div style={{
      background: '#0A1020', border: `1px solid ${focused ? accent + '80' : '#1c2942'}`,
      borderRadius: 10, padding: compact ? '10px 13px' : '13px 15px', transition: 'border-color 0.15s ease',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: compact ? 6 : 9 }}>
        <span style={{ fontSize: compact ? 10 : 11, fontFamily: 'monospace', color: '#8499b3', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</span>
        {hint && <InfoDot hint={hint} />}
      </div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        background: '#050A12', border: '1px solid #1c2942', borderRadius: 8,
        padding: '7px 10px 7px 12px',
      }}>
        <input
          type="text" inputMode="decimal" value={text}
          onChange={e => commit(e.target.value)}
          onFocus={() => setFocused(true)} onBlur={() => { setFocused(false); setText(fmtNum(value)); }}
          style={{ flex: 1, minWidth: 0, background: 'transparent', border: 'none', outline: 'none', color: accent, fontSize: compact ? 16 : 20, fontWeight: 700, fontFamily: 'monospace' }}
        />
        {unit && <span style={{ fontSize: 12, fontFamily: 'monospace', color: '#8499b3', paddingRight: 2, whiteSpace: 'nowrap' }}>{unit}</span>}
      </div>
    </div>
  );
}
