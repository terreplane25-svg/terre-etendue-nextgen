// Helpers partagés pour les graphiques SVG des simulateurs du Lab.

/** Graduations « rondes » de 0 à ~max (pas en 1 / 2 / 5 × 10ⁿ). */
export function niceTicks(max: number, count = 5): number[] {
  if (!isFinite(max) || max <= 0) return [0];
  const raw = max / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
  const ticks: number[] = [];
  for (let v = 0; v <= max + step * 0.5; v += step) {
    ticks.push(Math.round(v * 1e6) / 1e6);
  }
  return ticks;
}

/** Format compact d'une distance (m / km) pour un libellé d'axe. */
export function fmtDist(m: number): string {
  if (m >= 1000) return `${Math.round(m / 1000)} km`;
  return `${Math.round(m)} m`;
}

/** Format compact d'une longueur en km vers une étiquette lisible. */
export function fmtKmAxis(km: number): string {
  if (km >= 1) return `${km % 1 === 0 ? km : km.toFixed(1)} km`;
  if (km >= 0.001) return `${Math.round(km * 1000)} m`;
  return `${(km * 1e5).toFixed(0)} cm`;
}
