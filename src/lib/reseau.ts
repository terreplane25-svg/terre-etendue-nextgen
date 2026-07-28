// Lecture des réseaux de distances de content/reseau/.
// Serveur uniquement : utilise fs. Les composants clients reçoivent le résultat en props.
import fs from 'node:fs';
import path from 'node:path';

const DIR = path.join(process.cwd(), 'content', 'reseau');

export interface ReseauPoint {
  nom: string;
  latitude: number;
  longitude: number;
  description?: string;
}

export interface Noyau {
  fichier: string;
  titre: string;
  centre: ReseauPoint;
  points: ReseauPoint[];
  liaisons: number;
  etendueM: number;
  flecheM: number;
  incertitudeM: number;
  signalSurBruit: string;
  discriminant: boolean;
}

export interface Corde {
  a: string;
  b: string;
  cordeM: number;
  geodesiqueM: number;
  ecartM: number;
  ecartPct: number;
}

export interface Cible {
  rang: number;
  lieu: string;
  a: string;
  aLat: number;
  aLon: number;
  b: string;
  bLat: number;
  bLon: number;
  azimut: number;
  spherique: number;
  plan: number;
  ecart: number;
  ecartPct: number;
  classeExigee: string;
  pourquoi: string;
  accessibilite: string;
}

export interface ReseauData {
  noyaux: Noyau[];
  cordes: Corde[];
  cibles: Cible[];
  reperes: ReseauPoint[];
  etirement: { lieu: string; latitude: number; facteur: number; pourcent: number }[];
  stats: {
    noyaux: number;
    points: number;
    distances: number;
    mesures: number;
    discriminants: number;
    cordes: number;
  };
}

function lire(nom: string): any {
  return JSON.parse(fs.readFileSync(path.join(DIR, nom), 'utf-8'));
}

export function getReseau(): ReseauData {
  const global = lire('reseau-global-terre.json');
  const membres: any[] = global._meta.noyaux_membres;

  const noyaux: Noyau[] = membres.map((m) => {
    const n = lire(m.fichier);
    const points: ReseauPoint[] = n.points.map((p: any) => ({
      nom: p.nom,
      latitude: p.latitude,
      longitude: p.longitude,
      description: p.description,
    }));
    const centre = points.find((p) => p.nom === m.centre) ?? points[0];
    return {
      fichier: m.fichier,
      titre: n._meta.titre,
      centre,
      points,
      liaisons: n.liaisons.length,
      etendueM: m.etendue_m,
      flecheM: m.fleche_m,
      incertitudeM: m.incertitude_m,
      signalSurBruit: m.signal_sur_bruit,
      discriminant: m.discriminant === true,
    };
  });

  const cordes: Corde[] = global._meta.cordes_3D_entre_centres.valeurs.map((c: any) => ({
    a: c.a,
    b: c.b,
    cordeM: c.corde_3D_m,
    geodesiqueM: c.geodesique_m,
    ecartM: c.ecart_m,
    ecartPct: c.ecart_pourcent,
  }));

  const reperes: ReseauPoint[] = (global._meta.reperes_sans_noyau ?? []).map((r: any) => ({
    nom: r.nom,
    latitude: r.latitude,
    longitude: r.longitude,
    description: r.description,
  }));

  const cibles: Cible[] = lire('cibles-experimentales.json').cibles.map((c: any) => ({
    rang: c.rang,
    lieu: c.lieu,
    a: c.a,
    aLat: c.a_lat,
    aLon: c.a_lon,
    b: c.b,
    bLat: c.b_lat,
    bLon: c.b_lon,
    azimut: c.azimut_deg,
    spherique: c.prediction_modele_spherique_m,
    plan: c.prediction_modele_plan_m,
    ecart: c.ecart_m,
    ecartPct: c.ecart_pourcent,
    classeExigee: c.classe_exigee,
    pourquoi: c.pourquoi,
    accessibilite: c.accessibilite,
  }));

  const etirement = global._meta._table_etirement_par_latitude.valeurs.map((t: any) => ({
    lieu: t.lieu,
    latitude: t.latitude_deg,
    facteur: t.facteur,
    pourcent: t.etirement_pourcent,
  }));

  const ctrl = global._controle;
  return {
    noyaux,
    cordes,
    cibles,
    reperes,
    etirement,
    stats: {
      noyaux: ctrl.noyaux_membres,
      points: ctrl.points_totaux,
      distances: ctrl.distances_calculees,
      mesures: ctrl.mesures_de_terrain,
      discriminants: ctrl.noyaux_discriminants,
      cordes: ctrl.cordes_3D_classe_C,
    },
  };
}
