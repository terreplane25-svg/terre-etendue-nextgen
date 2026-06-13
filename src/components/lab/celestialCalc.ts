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

/**
 * Catalogue des 50 étoiles les plus brillantes du ciel (époque J2000)
 * RA en heures, déclinaison en degrés, magnitude apparente.
 * Sert à projeter de vraies étoiles nommées sur la voûte de l'observateur.
 */
export interface BrightStar { name: string; ra: number; dec: number; mag: number; }

export const BRIGHT_STARS: BrightStar[] = [
  { name: 'Sirius', ra: 6.7525, dec: -16.7161, mag: -1.46 },
  { name: 'Canopus', ra: 6.3992, dec: -52.6957, mag: -0.74 },
  { name: 'Rigil Kentaurus', ra: 14.6599, dec: -60.8354, mag: -0.27 },
  { name: 'Arcturus', ra: 14.2610, dec: 19.1825, mag: -0.05 },
  { name: 'Véga', ra: 18.6156, dec: 38.7837, mag: 0.03 },
  { name: 'Capella', ra: 5.2782, dec: 45.9980, mag: 0.08 },
  { name: 'Rigel', ra: 5.2423, dec: -8.2016, mag: 0.13 },
  { name: 'Procyon', ra: 7.6550, dec: 5.2250, mag: 0.34 },
  { name: 'Achernar', ra: 1.6286, dec: -57.2368, mag: 0.46 },
  { name: 'Bételgeuse', ra: 5.9195, dec: 7.4071, mag: 0.50 },
  { name: 'Hadar', ra: 14.0637, dec: -60.3730, mag: 0.61 },
  { name: 'Altaïr', ra: 19.8464, dec: 8.8683, mag: 0.76 },
  { name: 'Acrux', ra: 12.4433, dec: -63.0991, mag: 0.76 },
  { name: 'Aldébaran', ra: 4.5987, dec: 16.5093, mag: 0.86 },
  { name: 'Antarès', ra: 16.4901, dec: -26.4320, mag: 0.96 },
  { name: 'Spica', ra: 13.4199, dec: -11.1613, mag: 0.97 },
  { name: 'Pollux', ra: 7.7553, dec: 28.0262, mag: 1.14 },
  { name: 'Fomalhaut', ra: 22.9608, dec: -29.6222, mag: 1.16 },
  { name: 'Deneb', ra: 20.6905, dec: 45.2803, mag: 1.25 },
  { name: 'Mimosa', ra: 12.7953, dec: -59.6888, mag: 1.25 },
  { name: 'Régulus', ra: 10.1395, dec: 11.9672, mag: 1.39 },
  { name: 'Adhara', ra: 6.9771, dec: -28.9721, mag: 1.50 },
  { name: 'Castor', ra: 7.5767, dec: 31.8883, mag: 1.58 },
  { name: 'Shaula', ra: 17.5601, dec: -37.1038, mag: 1.62 },
  { name: 'Gacrux', ra: 12.5194, dec: -57.1132, mag: 1.64 },
  { name: 'Bellatrix', ra: 5.4188, dec: 6.3497, mag: 1.64 },
  { name: 'Elnath', ra: 5.4382, dec: 28.6075, mag: 1.65 },
  { name: 'Miaplacidus', ra: 9.2200, dec: -69.7172, mag: 1.69 },
  { name: 'Alnilam', ra: 5.6036, dec: -1.2019, mag: 1.69 },
  { name: 'Alnair', ra: 22.1372, dec: -46.9610, mag: 1.74 },
  { name: 'Alnitak', ra: 5.6793, dec: -1.9426, mag: 1.77 },
  { name: 'Alioth', ra: 12.9005, dec: 55.9598, mag: 1.77 },
  { name: 'Dubhe', ra: 11.0622, dec: 61.7510, mag: 1.79 },
  { name: 'Mirfak', ra: 3.4054, dec: 49.8612, mag: 1.80 },
  { name: 'Wezen', ra: 7.1399, dec: -26.3932, mag: 1.84 },
  { name: 'Kaus Australis', ra: 18.4029, dec: -34.3846, mag: 1.85 },
  { name: 'Alkaid', ra: 13.7923, dec: 49.3133, mag: 1.86 },
  { name: 'Avior', ra: 8.3752, dec: -59.5095, mag: 1.86 },
  { name: 'Sargas', ra: 17.6219, dec: -42.9978, mag: 1.87 },
  { name: 'Menkalinan', ra: 5.9921, dec: 44.9474, mag: 1.90 },
  { name: 'Atria', ra: 16.8110, dec: -69.0277, mag: 1.92 },
  { name: 'Alhena', ra: 6.6285, dec: 16.3993, mag: 1.92 },
  { name: 'Peacock', ra: 20.4275, dec: -56.7351, mag: 1.94 },
  { name: 'Polaris', ra: 2.5302, dec: 89.2641, mag: 1.98 },
  { name: 'Mirzam', ra: 6.3783, dec: -17.9559, mag: 1.98 },
  { name: 'Alphard', ra: 9.4598, dec: -8.6587, mag: 2.00 },
  { name: 'Hamal', ra: 2.1196, dec: 23.4624, mag: 2.00 },
  { name: 'Diphda', ra: 0.7265, dec: -17.9866, mag: 2.04 },
  { name: 'Nunki', ra: 18.9211, dec: -26.2967, mag: 2.06 },
  { name: 'Mizar', ra: 13.3988, dec: 54.9254, mag: 2.07 },
  // ── mag 2.1–2.5 ──
  { name: 'Saiph', ra: 5.7954, dec: -9.6696, mag: 2.09 },
  { name: 'Kochab', ra: 14.8451, dec: 74.1555, mag: 2.08 },
  { name: 'Rasalhague', ra: 17.5822, dec: 12.5600, mag: 2.08 },
  { name: 'Algol', ra: 3.1361, dec: 40.9556, mag: 2.12 },
  { name: 'Almach', ra: 2.0650, dec: 42.3297, mag: 2.17 },
  { name: 'Denebola', ra: 11.8177, dec: 14.5720, mag: 2.13 },
  { name: 'Tiaki', ra: 0.1375, dec: -45.7475, mag: 2.16 },
  { name: 'Naos', ra: 8.0594, dec: -40.0031, mag: 2.25 },
  { name: 'Aspidiske', ra: 9.2849, dec: -59.2753, mag: 2.25 },
  { name: 'Suhail', ra: 9.1331, dec: -43.4326, mag: 2.21 },
  { name: 'Alphecca', ra: 15.5783, dec: 26.7147, mag: 2.23 },
  { name: 'Menkent', ra: 14.1114, dec: -36.3700, mag: 2.06 },
  { name: 'Sabik', ra: 17.1728, dec: -15.7249, mag: 2.43 },
  { name: 'Etamin', ra: 17.9434, dec: 51.4889, mag: 2.23 },
  { name: 'Dschubba', ra: 16.0054, dec: -22.6217, mag: 2.32 },
  { name: 'Yed Prior', ra: 16.2390, dec: -3.6944, mag: 2.56 },
  { name: 'Markab', ra: 23.0793, dec: 15.2053, mag: 2.49 },
  { name: 'Zubeneschamali', ra: 15.2833, dec: -9.3829, mag: 2.61 },
  { name: 'Schedar', ra: 0.6753, dec: 56.5374, mag: 2.23 },
  { name: 'Caph', ra: 0.1530, dec: 59.1498, mag: 2.27 },
  { name: 'Ruchbah', ra: 1.4302, dec: 60.2353, mag: 2.68 },
  { name: 'Phact', ra: 5.6609, dec: -34.0742, mag: 2.64 },
  { name: 'Mintaka', ra: 5.5335, dec: -0.2991, mag: 2.23 },
  // ── mag 2.5–3.0 ──
  { name: 'Enif', ra: 21.7364, dec: 9.8750, mag: 2.39 },
  { name: 'Scheat', ra: 23.0628, dec: 28.0828, mag: 2.42 },
  { name: 'Algieba', ra: 10.3327, dec: 19.8416, mag: 2.61 },
  { name: 'Ankaa', ra: 0.4381, dec: -42.3060, mag: 2.37 },
  { name: 'Girtab', ra: 17.7926, dec: -37.0437, mag: 2.41 },
  { name: 'Tureis', ra: 8.1595, dec: -24.3044, mag: 2.49 },
  { name: 'Unukalhai', ra: 15.7378, dec: 6.4256, mag: 2.64 },
  { name: 'Sheratan', ra: 1.9107, dec: 20.8081, mag: 2.64 },
  { name: 'Kraz', ra: 12.5737, dec: -23.3968, mag: 2.65 },
  { name: 'Mahasim', ra: 5.9933, dec: 37.2126, mag: 2.69 },
  { name: 'Phaet', ra: 5.6609, dec: -34.0742, mag: 2.64 },
  { name: 'Rasalgethi', ra: 17.2443, dec: 14.3902, mag: 2.81 },
  { name: 'Alderamin', ra: 21.3096, dec: 62.5856, mag: 2.51 },
  { name: 'Aludra', ra: 7.4016, dec: -29.3031, mag: 2.45 },
  { name: 'Muscida', ra: 8.5043, dec: 60.7180, mag: 3.35 },
  { name: 'Merak', ra: 11.0306, dec: 56.3824, mag: 2.37 },
  { name: 'Phecda', ra: 11.8968, dec: 53.6948, mag: 2.44 },
  { name: 'Megrez', ra: 12.2571, dec: 57.0326, mag: 3.31 },
  { name: 'Al Niyat', ra: 16.3533, dec: -25.5927, mag: 2.89 },
  { name: 'Acrab', ra: 16.0905, dec: -19.8052, mag: 2.62 },
  { name: 'Wezn', ra: 5.5929, dec: -17.8222, mag: 2.78 },
  { name: 'Alcyone', ra: 3.7914, dec: 24.1053, mag: 2.87 },
  { name: 'Alsephina', ra: 8.1584, dec: -47.3367, mag: 1.93 },
  { name: 'Tarazed', ra: 19.7711, dec: 10.6133, mag: 2.72 },
  { name: 'Alhajoth', ra: 5.2782, dec: 45.9980, mag: 2.69 },
  // ── mag 3.0–3.5 : constellations majeures ──
  { name: 'Thuban', ra: 14.0733, dec: 64.3757, mag: 3.67 },
  { name: 'Alula Borealis', ra: 11.3081, dec: 33.0861, mag: 3.49 },
  { name: 'Algenib', ra: 0.2205, dec: 15.1836, mag: 2.83 },
  { name: 'Mirach', ra: 1.1622, dec: 35.6206, mag: 2.05 },
  { name: 'Almak', ra: 2.0650, dec: 42.3297, mag: 2.17 },
  { name: 'Azmidi', ra: 8.3040, dec: -40.0031, mag: 3.34 },
  { name: 'Adhil', ra: 1.3900, dec: 45.5289, mag: 3.27 },
  { name: 'Rukbat', ra: 19.3981, dec: -40.6160, mag: 3.97 },
  { name: 'Kornephoros', ra: 16.5036, dec: 21.4895, mag: 2.77 },
  { name: 'Altais', ra: 19.2094, dec: 67.6617, mag: 3.07 },
  { name: 'Grumium', ra: 17.8924, dec: 56.8727, mag: 3.75 },
  { name: 'Ginan', ra: 12.6262, dec: -57.1732, mag: 3.23 },
  { name: 'Acubens', ra: 8.9755, dec: 11.8578, mag: 4.25 },
  { name: 'Zubenelgenubi', ra: 14.8479, dec: -16.0418, mag: 2.75 },
  { name: 'Wei', ra: 16.8362, dec: -34.2932, mag: 3.02 },
  { name: 'Sualocin', ra: 20.6606, dec: 15.9120, mag: 3.77 },
  { name: 'Rotanev', ra: 20.6258, dec: 14.5953, mag: 3.63 },
  { name: 'Kitalpha', ra: 21.2633, dec: 5.2481, mag: 3.93 },
  { name: 'Errai', ra: 23.6557, dec: 77.6322, mag: 3.21 },
  { name: 'Alfirk', ra: 21.4776, dec: 70.5607, mag: 3.23 },
];

export interface StarPosition extends BrightStar { altitude: number; azimuth: number; }

/**
 * Altitude/azimut des étoiles brillantes pour un observateur et une date.
 * Angle horaire H = TSL − RA, puis transformation équatorial → horizontal :
 * sin(alt) = sin(φ)·sin(δ) + cos(φ)·cos(δ)·cos(H)
 * az mesuré depuis le Nord vers l'Est.
 */
export function getStarPositions(date: Date, obs: ObserverLocation): StarPosition[] {
  const lstDeg = Astronomy.SiderealTime(date) * 15 + obs.lng;
  const latR = obs.lat * Math.PI / 180;
  return BRIGHT_STARS.map(s => {
    const haR = ((lstDeg - s.ra * 15) * Math.PI) / 180;
    const decR = s.dec * Math.PI / 180;
    const sinAlt = Math.sin(latR) * Math.sin(decR) + Math.cos(latR) * Math.cos(decR) * Math.cos(haR);
    const alt = Math.asin(Math.max(-1, Math.min(1, sinAlt)));
    const az = Math.atan2(
      -Math.cos(decR) * Math.sin(haR),
      Math.sin(decR) * Math.cos(latR) - Math.cos(decR) * Math.sin(latR) * Math.cos(haR)
    );
    return { ...s, altitude: alt * 180 / Math.PI, azimuth: ((az * 180 / Math.PI) + 360) % 360 };
  });
}

/** Longueur et direction de l'ombre d'un gnomon de hauteur h, pour une altitude et azimut solaires donnés */
export function gnomonShadow(sunAltDeg: number, sunAzDeg: number, gnomonH: number): { length: number; dirDeg: number } | null {
  if (sunAltDeg <= 0) return null;
  const length = gnomonH / Math.tan(sunAltDeg * Math.PI / 180);
  const dirDeg = (sunAzDeg + 180) % 360;
  return { length, dirDeg };
}
