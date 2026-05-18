// ─── Calculs astronomiques simplifiés ───────────────
// Positions réelles des astres basées sur les éphémérides
// Toutes les positions sont le point subsolaire / sublunaire (zénith)
// exprimé en (latitude, longitude) sur la Terre

/**
 * Déclinaison solaire : oscille entre +23.44° (solstice juin) et -23.44° (solstice déc)
 * C'est la latitude du point subsolaire
 */
export function getSunDeclination(dayOfYear: number): number {
  // Formule de Spencer simplifiée
  const B = ((dayOfYear - 81) / 365) * 2 * Math.PI;
  return 23.44 * Math.sin(B);
}

/**
 * Longitude subsolaire : dépend de l'heure UTC
 * Le soleil est au méridien 0° à 12:00 UTC, puis recule de 15°/heure
 */
export function getSunLongitude(hoursUTC: number): number {
  return ((12 - hoursUTC) / 24) * 360;
}

/**
 * Déclinaison lunaire : oscille entre ±28.5° sur un cycle de ~27.3 jours
 * Simplifié — en réalité c'est plus complexe (nutation etc.)
 */
export function getMoonDeclination(dayOfYear: number): number {
  const lunarCycle = 27.3; // jours (sidéral)
  const phase = ((dayOfYear % lunarCycle) / lunarCycle) * 2 * Math.PI;
  return 28.5 * Math.sin(phase);
}

/**
 * Longitude sublunaire : la Lune fait un tour en ~24h 50min
 * Donc elle retarde de ~13.17° par jour par rapport au Soleil
 */
export function getMoonLongitude(hoursUTC: number, dayOfYear: number): number {
  const baseLng = ((12 - hoursUTC) / 24) * 360;
  const dailyLag = 13.17; // degrés de retard par jour
  return baseLng - (dayOfYear * dailyLag) % 360;
}

/**
 * Phase lunaire (0-1) : 0 = nouvelle lune, 0.5 = pleine lune
 */
export function getMoonPhase(dayOfYear: number): number {
  const synodicPeriod = 29.53; // jours
  // Nouvelle lune de référence : ~6 janvier
  const daysSinceNewMoon = (dayOfYear - 6 + 365) % synodicPeriod;
  return daysSinceNewMoon / synodicPeriod;
}

/**
 * Positions des planètes visibles (simplifié)
 * Retourne la déclinaison et l'ascension droite approximatives
 */
interface PlanetPosition {
  name: string;
  color: string;
  lat: number;  // déclinaison → latitude subplanétaire
  lng: number;  // heure angle → longitude
  size: number; // taille visuelle relative
}

export function getPlanetPositions(dayOfYear: number, hoursUTC: number): PlanetPosition[] {
  // Périodes synodiques simplifiées et déclinaisons moyennes
  const t = dayOfYear + hoursUTC / 24;
  
  return [
    {
      name: 'Vénus',
      color: '#E8C060',
      lat: 15 * Math.sin((t / 224.7) * 2 * Math.PI + 1.2),
      lng: getSunLongitude(hoursUTC) + 45 * Math.sin((t / 584) * 2 * Math.PI),
      size: 0.18,
    },
    {
      name: 'Mars',
      color: '#CC6644',
      lat: 20 * Math.sin((t / 687) * 2 * Math.PI + 0.5),
      lng: ((12 - hoursUTC) / 24) * 360 - (t * 0.524) % 360,
      size: 0.12,
    },
    {
      name: 'Jupiter',
      color: '#C8A060',
      lat: 3 * Math.sin((t / 4333) * 2 * Math.PI),
      lng: ((12 - hoursUTC) / 24) * 360 - (t * 0.083) % 360,
      size: 0.22,
    },
    {
      name: 'Saturne',
      color: '#D4B878',
      lat: 5 * Math.sin((t / 10759) * 2 * Math.PI),
      lng: ((12 - hoursUTC) / 24) * 360 - (t * 0.033) % 360,
      size: 0.16,
    },
    {
      name: 'Mercure',
      color: '#A0A0A0',
      lat: 7 * Math.sin((t / 88) * 2 * Math.PI + 2.0),
      lng: getSunLongitude(hoursUTC) + 25 * Math.sin((t / 116) * 2 * Math.PI),
      size: 0.08,
    },
  ];
}

/**
 * Convertir lat/lng en position sur le disque plat (projection azimutale équidistante)
 * Retourne [x, z] en unités Three.js
 */
export function latLngToFlatDisc(lat: number, lng: number, discRadius: number): [number, number] {
  const latRad = (lat * Math.PI) / 180;
  const lngRad = (lng * Math.PI) / 180;
  // En projection AE, la distance au centre = (90° - lat) / 180° × diamètre
  const r = ((90 - lat) / 180) * discRadius;
  const x = Math.sin(lngRad) * r;
  const z = -Math.cos(lngRad) * r;
  return [x, z];
}

/**
 * Obtenir la date courante décomposée
 */
export function getCurrentTimeInfo() {
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now.getTime() - start.getTime();
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hoursUTC = now.getUTCHours() + now.getUTCMinutes() / 60;
  return { dayOfYear, hoursUTC, now };
}
