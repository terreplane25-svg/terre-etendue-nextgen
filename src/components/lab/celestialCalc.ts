/**
 * Calculs astronomiques basés sur astronomy-engine
 * Positions précises offline pour tous les corps célestes
 */
import * as Astronomy from 'astronomy-engine';

export interface CelestialPosition {
  name: string;
  color: string;
  lat: number;    // Déclinaison = latitude subplanétaire
  lng: number;    // Heure angle → longitude subplanétaire
  size: number;   // Taille visuelle relative
  altitude?: number; // Altitude en degrés (pour observateur)
  azimuth?: number;  // Azimut en degrés (pour observateur)
}

export interface ObserverLocation {
  lat: number;
  lng: number;
  name: string;
}

export const DEFAULT_OBSERVER: ObserverLocation = { lat: 48.853, lng: 2.35, name: 'Paris' };

/** Projection azimutale inverse : position sur le disque (x, z) → (lat, lng) en degrés */
export function flatDiscToLatLng(x: number, z: number, discRadius: number): [number, number] | null {
  const r = Math.sqrt(x * x + z * z);
  if (r > discRadius) return null;
  const lat = 90 - (r / discRadius) * 180;
  const AE_OFFSET = 180;
  const a = Math.atan2(x, -z);
  let lng = AE_OFFSET - (a * 180) / Math.PI;
  lng = ((lng + 180) % 360 + 360) % 360 - 180;
  return [lat, lng];
}

export const PRESET_CITIES: ObserverLocation[] = [
  { lat: 21.4225, lng: 39.8262, name: 'La Mecque' },
  { lat: 24.4672, lng: 39.6112, name: 'Médine' },
  { lat: 48.853, lng: 2.35, name: 'Paris' },
  { lat: 51.507, lng: -0.128, name: 'Londres' },
  { lat: 40.713, lng: -74.006, name: 'New York' },
  { lat: 35.682, lng: 139.692, name: 'Tokyo' },
  { lat: -33.868, lng: 151.209, name: 'Sydney' },
  { lat: -22.907, lng: -43.172, name: 'Rio de Janeiro' },
  { lat: 55.756, lng: 37.617, name: 'Moscou' },
  { lat: 30.044, lng: 31.236, name: 'Le Caire' },
  { lat: -1.286, lng: 36.817, name: 'Nairobi' },
  { lat: 31.768, lng: 35.214, name: 'Jérusalem' },
  { lat: 33.513, lng: 36.292, name: 'Damas' },
  { lat: 41.009, lng: 28.980, name: 'Istanbul' },
  { lat: 39.916, lng: 116.397, name: 'Pékin' },
];

/**
 * Calcule la longitude subsolaire/sublunaire/subplanétaire
 * RA (ascension droite en heures) + heure sidérale → longitude
 */
function raToSubLongitude(raHours: number, date: Date): number {
  // Heure sidérale apparente de Greenwich via astronomy-engine
  // (précision arc-seconde, inclut nutation — remplace l'approximation polynomiale)
  const gastHours = Astronomy.SiderealTime(date);
  const gastDeg = gastHours * 15;

  const raDeg = raHours * 15; // RA en degrés
  let lng = raDeg - gastDeg;
  // Normaliser entre -180 et 180
  lng = ((lng + 180) % 360 + 360) % 360 - 180;
  return lng;
}

/**
 * Obtient les positions de tous les corps célestes pour une date donnée
 */
export function getAllPositions(date: Date, obsLoc?: ObserverLocation): {
  sun: CelestialPosition;
  moon: CelestialPosition;
  planets: CelestialPosition[];
  moonPhaseAngle: number;
  moonIllumination: number;
} {
  const obs = new Astronomy.Observer(obsLoc?.lat ?? 0, obsLoc?.lng ?? 0, 0);

  // Coordonnées horizontales (altitude/azimut) pour l'observateur
  const horizon = (ra: number, dec: number): { altitude?: number; azimuth?: number } => {
    if (!obsLoc) return {};
    const hor = Astronomy.Horizon(date, obs, ra, dec, 'normal');
    return { altitude: hor.altitude, azimuth: hor.azimuth };
  };

  // Soleil
  const sunEq = Astronomy.Equator(Astronomy.Body.Sun, date, obs, true, true);
  const sunLng = raToSubLongitude(sunEq.ra, date);

  // Lune
  const moonEq = Astronomy.Equator(Astronomy.Body.Moon, date, obs, true, true);
  const moonLng = raToSubLongitude(moonEq.ra, date);
  const moonPhaseAngle = Astronomy.MoonPhase(date);
  // Illumination
  let moonIll: number;
  try {
    const illum = Astronomy.Illumination(Astronomy.Body.Moon, date);
    moonIll = illum.phase_fraction * 100;
  } catch {
    moonIll = (1 - Math.cos(moonPhaseAngle * Math.PI / 180)) / 2 * 100;
  }
  
  // Planètes
  const planetDefs: { body: Astronomy.Body; name: string; color: string; size: number }[] = [
    { body: Astronomy.Body.Mercury, name: 'Mercure', color: '#A0A0A0', size: 0.06 },
    { body: Astronomy.Body.Venus,   name: 'Vénus',   color: '#E8C060', size: 0.10 },
    { body: Astronomy.Body.Mars,    name: 'Mars',    color: '#CC6644', size: 0.08 },
    { body: Astronomy.Body.Jupiter, name: 'Jupiter', color: '#C8A060', size: 0.14 },
    { body: Astronomy.Body.Saturn,  name: 'Saturne', color: '#D4B878', size: 0.11 },
  ];
  
  const planets: CelestialPosition[] = planetDefs.map(p => {
    const eq = Astronomy.Equator(p.body, date, obs, true, true);
    return {
      name: p.name,
      color: p.color,
      lat: eq.dec,
      lng: raToSubLongitude(eq.ra, date),
      size: p.size,
      ...horizon(eq.ra, eq.dec),
    };
  });

  return {
    sun: { name: 'Soleil', color: '#FFD040', lat: sunEq.dec, lng: sunLng, size: 0.22, ...horizon(sunEq.ra, sunEq.dec) },
    moon: { name: 'Lune', color: '#C8C8D0', lat: moonEq.dec, lng: moonLng, size: 0.12, ...horizon(moonEq.ra, moonEq.dec) },
    planets,
    moonPhaseAngle,
    moonIllumination: moonIll,
  };
}

/**
 * Nom de la phase lunaire en français à partir de l'angle de phase (0 = nouvelle lune)
 */
export function moonPhaseName(phaseAngle: number): string {
  const a = ((phaseAngle % 360) + 360) % 360;
  if (a < 22.5 || a >= 337.5) return 'Nouvelle lune';
  if (a < 67.5) return 'Premier croissant';
  if (a < 112.5) return 'Premier quartier';
  if (a < 157.5) return 'Gibbeuse croissante';
  if (a < 202.5) return 'Pleine lune';
  if (a < 247.5) return 'Gibbeuse décroissante';
  if (a < 292.5) return 'Dernier quartier';
  return 'Dernier croissant';
}

/**
 * Convertit lat/lng en position sur le disque AE (Three.js)
 * Pôle Nord au centre, Antarctique en bordure
 */
export function latLngToFlatDisc(lat: number, lng: number, discRadius: number): [number, number] {
  // Orientation de la texture ae-map.jpg : méridien de Greenwich (0°) vers le bas,
  // longitudes Est en sens anti-horaire → angle écran a = 180° − lng.
  // Longitude inversée pour que le mouvement du Soleil soit HORAIRE vu du dessus (pôle Nord)
  const AE_OFFSET = 180;
  const lngRad = ((-lng + AE_OFFSET) * Math.PI) / 180;
  const r = ((90 - lat) / 180) * discRadius;
  const x = Math.sin(lngRad) * r;
  const z = -Math.cos(lngRad) * r;
  return [x, z];
}

/**
 * Date formatée pour l'affichage
 */
export function formatSimDate(date: Date): string {
  const d = date.getDate().toString().padStart(2, '0');
  const m = (date.getMonth() + 1).toString().padStart(2, '0');
  const y = date.getFullYear();
  const h = date.getUTCHours().toString().padStart(2, '0');
  const min = date.getUTCMinutes().toString().padStart(2, '0');
  return `${d}/${m}/${y} ${h}:${min} UTC`;
}

/** Distance sur grand cercle (formule de Haversine) en km */
export function haversineKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371;
  const toRad = (d: number) => d * Math.PI / 180;
  const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

/** Angle central entre deux points (en degrés) */
export function centralAngleDeg(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const toRad = (d: number) => d * Math.PI / 180;
  const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))) * 180 / Math.PI;
}

/** Points intermédiaires le long d'un grand cercle pour le tracé sur le disque AE */
export function greatCirclePoints(lat1: number, lng1: number, lat2: number, lng2: number, n: number): [number, number][] {
  const toRad = (d: number) => d * Math.PI / 180;
  const toDeg = (r: number) => r * 180 / Math.PI;
  const f1 = toRad(lat1), l1 = toRad(lng1), f2 = toRad(lat2), l2 = toRad(lng2);
  const d = 2 * Math.asin(Math.sqrt(Math.sin((f2 - f1) / 2) ** 2 + Math.cos(f1) * Math.cos(f2) * Math.sin((l2 - l1) / 2) ** 2));
  if (d < 1e-10) return [[lat1, lng1]];
  const pts: [number, number][] = [];
  for (let i = 0; i <= n; i++) {
    const f = i / n;
    const a = Math.sin((1 - f) * d) / Math.sin(d);
    const b = Math.sin(f * d) / Math.sin(d);
    const x = a * Math.cos(f1) * Math.cos(l1) + b * Math.cos(f2) * Math.cos(l2);
    const y = a * Math.cos(f1) * Math.sin(l1) + b * Math.cos(f2) * Math.sin(l2);
    const z = a * Math.sin(f1) + b * Math.sin(f2);
    pts.push([toDeg(Math.atan2(z, Math.sqrt(x * x + y * y))), toDeg(Math.atan2(y, x))]);
  }
  return pts;
}

/** Réfraction atmosphérique (formule de Bennett) en arc-minutes */
export function bennettRefractionArcmin(apparentAltDeg: number): number {
  if (apparentAltDeg < -1) return 0;
  const h = Math.max(apparentAltDeg, -0.5);
  return 1 / Math.tan((h + 7.31 / (h + 4.4)) * Math.PI / 180) + 0.0013515;
}

/** Prochaine éclipse solaire et lunaire depuis une date donnée */
export function nextEclipses(date: Date): {
  solarDate: Date | null;
  solarType: string;
  lunarDate: Date | null;
  lunarType: string;
} {
  let solarDate: Date | null = null, solarType = '';
  let lunarDate: Date | null = null, lunarType = '';
  try {
    const se = Astronomy.SearchGlobalSolarEclipse(date);
    solarDate = se.peak.date;
    solarType = se.kind === 'total' ? 'Totale' : se.kind === 'annular' ? 'Annulaire' : 'Partielle';
  } catch { /* pas disponible */ }
  try {
    const le = Astronomy.SearchLunarEclipse(date);
    lunarDate = le.peak.date;
    lunarType = le.kind === 'total' ? 'Totale' : le.kind === 'partial' ? 'Partielle' : 'Pénombrale';
  } catch { /* pas disponible */ }
  return { solarDate, solarType, lunarDate, lunarType };
}

/** Longueur et direction de l'ombre d'un gnomon de hauteur h, pour une altitude et azimut solaires donnés */
export function gnomonShadow(sunAltDeg: number, sunAzDeg: number, gnomonH: number): { length: number; dirDeg: number } | null {
  if (sunAltDeg <= 0) return null;
  const length = gnomonH / Math.tan(sunAltDeg * Math.PI / 180);
  const dirDeg = (sunAzDeg + 180) % 360;
  return { length, dirDeg };
}
