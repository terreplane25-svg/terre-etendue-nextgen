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
}

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
export function getAllPositions(date: Date): {
  sun: CelestialPosition;
  moon: CelestialPosition;
  planets: CelestialPosition[];
  moonPhaseAngle: number;
  moonIllumination: number;
} {
  const obs = new Astronomy.Observer(0, 0, 0);
  
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
    };
  });
  
  return {
    sun: { name: 'Soleil', color: '#FFD040', lat: sunEq.dec, lng: sunLng, size: 0.22 },
    moon: { name: 'Lune', color: '#C8C8D0', lat: moonEq.dec, lng: moonLng, size: 0.12 },
    planets,
    moonPhaseAngle,
    moonIllumination: moonIll,
  };
}

/**
 * Convertit lat/lng en position sur le disque AE (Three.js)
 * Pôle Nord au centre, Antarctique en bordure
 */
export function latLngToFlatDisc(lat: number, lng: number, discRadius: number): [number, number] {
  // Offset calibré sur l'image satellite AE (128°)
  // Longitude inversée pour que le mouvement soit HORAIRE vu du dessus (pôle Nord)
  const AE_OFFSET = 128;
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
