'use client';
import { useState, useMemo, useCallback } from 'react';

/* ═══════════════════════════════════════════════════════════════
   CARTE PAR TRILATÉRATION
   Toile vierge. Aucune carte de fond, aucun centre, aucune
   coordonnée. Les villes sont placées uniquement à partir des
   distances saisies : la première sert d'ancrage, la deuxième se
   place à la distance donnée (orientation libre), les suivantes
   par trilatération sur les villes déjà placées.
   Si le réseau ne peut pas s'aplanir sans déformation, on applique
   le meilleur compromis (tension globale minimale) et on affiche
   l'écart entre distance saisie et distance tracée.
   ═══════════════════════════════════════════════════════════════ */

const OPAL = '#3D9E7C';
const GOLD = '#D4943A';
const ROSE = '#C45E6A';
const MONO = "'JetBrains Mono', monospace";
const NM = 1.852;

type Nature = 'trajet' | 'separation';
interface Leg { a: string; b: string; km: number; src: string; on: boolean; nat: Nature; }

/** Lot de données fourni — repris tel quel, sans modification. */
const SEED: Leg[] = [
  { a: 'Paris', b: 'Londres', km: 343, on: true, src: 'Géodésique / Directe — triangulation IGN / Ordnance Survey' , nat: 'separation' },
  { a: 'Paris', b: 'Berlin', km: 1050, on: true, src: 'Terrestre (Odomètre / Rail) — via Francfort' , nat: 'trajet' },
  { a: 'Paris', b: 'Moscou', km: 3217, on: true, src: 'Terrestre (Odomètre / Rail) — via Allemagne et Biélorussie' , nat: 'trajet' },
  { a: 'New York', b: 'Londres', km: 5869, on: true, src: 'Maritime (NGA Pub. 151) — Bishop Rock' , nat: 'trajet' },
  { a: 'New York', b: 'Rio de Janeiro', km: 8834, on: true, src: 'Maritime (NGA Pub. 151) — Atlantique' , nat: 'trajet' },
  { a: 'New York', b: 'Los Angeles', km: 4491, on: true, src: 'Terrestre (Odomètre / Route) — I-80 / I-15' , nat: 'trajet' },
  { a: 'Los Angeles', b: 'Tokyo', km: 8816, on: true, src: 'Maritime (NGA Pub. 151) — transpacifique' , nat: 'trajet' },
  { a: 'Tokyo', b: 'Sydney', km: 8225, on: true, src: 'Maritime (NGA Pub. 151) — Pacifique Ouest' , nat: 'trajet' },
  { a: 'Londres', b: 'Le Caire', km: 3510, on: true, src: 'Aérienne (Orthodromie) — trajet direct' , nat: 'separation' },
  { a: 'Sydney', b: 'Auckland', km: 2156, on: true, src: 'Maritime (NGA Pub. 151) — mer de Tasman' , nat: 'trajet' },
  { a: "Buenos Aires", b: "Le Cap", km: 6880, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Route maritime Transatlantique Sud" , nat: 'trajet' },
  { a: "Le Cap", b: "Sydney", km: 11010, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Route maritime Océan Indien Sud" , nat: 'trajet' },
  { a: "Sydney", b: "Santiago", km: 11340, on: true, src: "Aérienne (Orthodromie) · Séparation directe — Vol transpacifique Sud" , nat: 'separation' },
  { a: "Punta Arenas", b: "Base Eduardo Frei", km: 1250, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Passage de Drake vers la péninsule Antarctique" , nat: 'trajet' },
  { a: "Ushuaïa", b: "Base McMurdo", km: 4800, on: true, src: "Aérienne (Directe) · Séparation directe — Liaison directe Amérique du Sud – Antarctique" , nat: 'separation' },
  { a: "Hobart", b: "Base Casey", km: 3420, on: true, src: "Maritime / Ravitaillement · Trajet — Route maritime de ravitaillement australienne" , nat: 'trajet' },
  { a: "Christchurch", b: "Base McMurdo", km: 3830, on: true, src: "Aérienne (Ravitaillement) · Séparation directe — Ligne de ravitaillement américaine / néo-zélandaise" , nat: 'separation' },
  { a: "Le Cap", b: "Base Novolazarevskaya", km: 4180, on: true, src: "Aérienne (DROMLAN) · Séparation directe — Réseau aérien intercontinental antarctique sud-africain" , nat: 'separation' },
  { a: "Dakar", b: "Rio de Janeiro", km: 5030, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Traversée la plus courte de l'Atlantique Sud", nat: 'trajet' },
  { a: "Le Caire", b: "Bombay (Mumbai)", km: 3930, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Via la mer Rouge et le golfe d'Aden", nat: 'trajet' },
  { a: "Bombay (Mumbai)", b: "Singapour", km: 3900, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Océan Indien Est / détroit de Malacca" , nat: 'trajet' },
  { a: "Singapour", b: "Sydney", km: 6300, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Passage Indonésie / nord de l'Australie", nat: 'trajet' },
  { a: "Pékin", b: "Moscou", km: 7980, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Transmongolien / Transsibérien" , nat: 'trajet' },
  { a: "Los Angeles", b: "Honolulu", km: 4110, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Route Pacifique Nord-Est" , nat: 'trajet' },
  { a: "Honolulu", b: "Tokyo", km: 6200, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Route Pacifique Centre-Ouest" , nat: 'trajet' },
  { a: "Christchurch", b: "Auckland", km: 1070, on: true, src: "Terrestre (Route / Ferry Interislander) · Trajet — Île du Sud – île du Nord via ferry du détroit de Cook" , nat: 'trajet' },
  { a: "Hobart", b: "Sydney", km: 1160, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Détroit de Bass / mer de Tasman" , nat: 'trajet' },
  { a: "Punta Arenas", b: "Santiago", km: 3090, on: true, src: "Terrestre (Route / Ruta 40 & Ruta 5) · Trajet — Trajet routier Chili – Argentine – Chili" , nat: 'trajet' },
  { a: "Ushuaïa", b: "Buenos Aires", km: 3080, on: true, src: "Terrestre (Route / Ruta Nacional 3) · Trajet — Trajet routier direct Patagonie" , nat: 'trajet' },
  { a: "Le Cap", b: "Rio de Janeiro", km: 6050, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Traversée directe Atlantique Sud" , nat: 'trajet' },
  { a: "Le Cap", b: "Dakar", km: 7030, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Le long de la côte ouest-africaine" , nat: 'trajet' },
  { a: "Honolulu", b: "Sydney", km: 8180, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Pacifique Sud-Ouest" , nat: 'trajet' },
  { a: "Singapour", b: "Tokyo", km: 5390, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Mer de Chine méridionale / Pacifique" , nat: 'trajet' },
  { a: "Buenos Aires", b: "Rio de Janeiro", km: 2180, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Côtière Amérique du Sud" , nat: 'trajet' },
  { a: "Le Caire", b: "Singapour", km: 8200, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Via Suez, mer Rouge et détroit de Malacca" , nat: 'trajet' },
  { a: "New York", b: "Le Cap", km: 12590, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Transatlantique Nord-Sud" , nat: 'trajet' },
  { a: "Berlin", b: "Moscou", km: 1820, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Ligne directe via Varsovie et Minsk" , nat: 'trajet' },
  { a: "Berlin", b: "Londres", km: 1100, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Via Bruxelles et Eurostar" , nat: 'trajet' },
  { a: "Pékin", b: "Singapour", km: 4480, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Asie du Sud-Est via Viêt Nam / Laos / Thaïlande" , nat: 'trajet' },
  { a: "Sydney", b: "Los Angeles", km: 12060, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct transpacifique" , nat: 'separation' },
  { a: "Paris", b: "New York", km: 5830, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct transatlantique" , nat: 'separation' },
  { a: "Londres", b: "Tokyo", km: 9560, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct Eurasie" , nat: 'separation' },
  { a: "New York", b: "Tokyo", km: 10860, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct Pacifique" , nat: 'separation' },
  { a: "Londres", b: "Moscou", km: 2500, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct Europe Ouest – Est" , nat: 'separation' },
  { a: "Pékin", b: "Tokyo", km: 2100, on: true, src: "Aérienne (Directe) · Séparation directe — Vol direct Asie de l'Est", nat: 'separation' },
  { a: "Paris", b: "Rome", km: 1420, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Ligne ferroviaire via la Suisse / Alpes" , nat: 'trajet' },
  { a: "Londres", b: "Rome", km: 1870, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Réseau ferroviaire continental via la France" , nat: 'trajet' },
  { a: "Berlin", b: "Rome", km: 1500, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Réseau ferroviaire via l'Autriche (Brenner)", nat: 'trajet' },
  { a: "New York", b: "Miami", km: 2060, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Route I-95, côte est des États-Unis" , nat: 'trajet' },
  { a: "Chicago", b: "New York", km: 1270, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Route I-80 est-ouest" , nat: 'trajet' },
  { a: "Chicago", b: "Los Angeles", km: 3250, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Route 66 / I-40" , nat: 'trajet' },
  { a: "Miami", b: "Los Angeles", km: 4390, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Route I-10, sud des États-Unis" , nat: 'trajet' },
  { a: "Bombay (Mumbai)", b: "Pékin", km: 6800, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Océan Indien / mer de Chine via Malacca" , nat: 'trajet' },
  { a: "Le Caire", b: "Dakar", km: 6820, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Méditerranée / Atlantique via Gibraltar" , nat: 'trajet' },
  { a: "Dakar", b: "Johannesbourg", km: 8150, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Atlantique Sud (via Le Cap / Durban)" , nat: 'trajet' },
  { a: "Le Caire", b: "Johannesbourg", km: 10200, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Mer Rouge / océan Indien" , nat: 'trajet' },
  { a: "Sydney", b: "Buenos Aires", km: 12230, on: true, src: "Aérienne (Directe) · Séparation directe — Vol transpacifique Sud" , nat: 'separation' },
  { a: "Rio de Janeiro", b: "Santiago", km: 3650, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Transcontinentale sud-américaine via l'Argentine", nat: 'trajet' },
  { a: "Santiago", b: "Buenos Aires", km: 1400, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Traversée des Andes (col de la Cumbre / route 7)" , nat: 'trajet' },
  { a: "Chicago", b: "Miami", km: 2220, on: true, src: "Terrestre (Odomètre / Route) · Trajet — Route I-75 / I-65, centre-sud des États-Unis", nat: 'trajet' },
  { a: "New York", b: "Dakar", km: 6170, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Transatlantique Nord-Ouest / Afrique de l'Ouest", nat: 'trajet' },
  { a: "New York", b: "Buenos Aires", km: 10870, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Atlantique Nord-Sud complète", nat: 'trajet' },
  { a: "Los Angeles", b: "Sydney", km: 12510, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Transpacifique via Honolulu", nat: 'trajet' },
  { a: "Le Cap", b: "Singapour", km: 9830, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Océan Indien Sud", nat: 'trajet' },
  { a: "Le Caire", b: "Rio de Janeiro", km: 9850, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Méditerranée, Gibraltar et Atlantique", nat: 'trajet' },
  { a: "Rome", b: "Le Caire", km: 2130, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Méditerranée centrale / Port-Saïd", nat: 'trajet' },
  { a: "Rome", b: "Moscou", km: 2870, on: true, src: "Terrestre (Odomètre / Rail) · Trajet — Trans-européen via Autriche, Pologne et Biélorussie", nat: 'trajet' },
  { a: "Honolulu", b: "Auckland", km: 7240, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Pacifique Centre-Sud", nat: 'trajet' },
  { a: "Dakar", b: "Buenos Aires", km: 6070, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Atlantique Sud médian direct", nat: 'trajet' },
  { a: "Dakar", b: "Londres", km: 4610, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Côte ouest-africaine / Europe du Nord", nat: 'trajet' },
  { a: "Dakar", b: "Punta Arenas", km: 8780, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Atlantique Sud vers le détroit de Magellan", nat: 'trajet' },
  { a: "Miami", b: "Rio de Janeiro", km: 7620, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Caraïbes / Atlantique Sud", nat: 'trajet' },
  { a: "Los Angeles", b: "Santiago", km: 9210, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Côtière Pacifique Est", nat: 'trajet' },
  { a: "Honolulu", b: "Singapour", km: 10830, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Transpacifique Centre-Ouest via Philippines", nat: 'trajet' },
  { a: "Auckland", b: "Santiago", km: 9880, on: true, src: "Maritime (NGA Pub. 151) · Trajet — Pacifique Sud-Est", nat: 'trajet' },
  { a: "Londres", b: "New York", km: 5570, on: true, src: "Aérienne (Directe) · Séparation directe — Transatlantique Nord", nat: 'separation' },
  { a: "Londres", b: "Los Angeles", km: 8780, on: true, src: "Aérienne (Directe) · Séparation directe — Transcontinental / arctique", nat: 'separation' },
  { a: "Londres", b: "Singapour", km: 10860, on: true, src: "Aérienne (Directe) · Séparation directe — Europe – Asie du Sud-Est", nat: 'separation' },
  { a: "Londres", b: "Johannesbourg", km: 9070, on: true, src: "Aérienne (Directe) · Séparation directe — Europe – Afrique", nat: 'separation' },
  { a: "Paris", b: "Tokyo", km: 9710, on: true, src: "Aérienne (Directe) · Séparation directe — Europe – Asie de l'Est", nat: 'separation' },
  { a: "Paris", b: "Le Caire", km: 3210, on: true, src: "Aérienne (Directe) · Séparation directe — Europe – Moyen-Orient", nat: 'separation' },
  { a: "New York", b: "Los Angeles", km: 3940, on: true, src: "Aérienne (Directe) · Séparation directe — Transcontinental USA", nat: 'separation' },
  { a: "New York", b: "Buenos Aires", km: 8530, on: true, src: "Aérienne (Directe) · Séparation directe — Amériques", nat: 'separation' },
  { a: "Los Angeles", b: "Tokyo", km: 8820, on: true, src: "Aérienne (Directe) · Séparation directe — Transpacifique Nord", nat: 'separation' },
  { a: "Tokyo", b: "Singapour", km: 5320, on: true, src: "Aérienne (Directe) · Séparation directe — Asie de l'Est – Sud-Est", nat: 'separation' },
  { a: "Tokyo", b: "Sydney", km: 7830, on: true, src: "Aérienne (Directe) · Séparation directe — Asie – Océanie", nat: 'separation' },
  { a: "Singapour", b: "Sydney", km: 6300, on: true, src: "Aérienne (Directe) · Séparation directe — Asie du Sud-Est – Océanie", nat: 'separation' },
  { a: "Le Caire", b: "Johannesbourg", km: 6260, on: true, src: "Aérienne (Directe) · Séparation directe — Afrique Nord-Sud", nat: 'separation' },
  { a: "Johannesbourg", b: "Buenos Aires", km: 8110, on: true, src: "Aérienne (Directe) · Séparation directe — Atlantique Sud", nat: 'separation' },
  { a: "Santiago", b: "Buenos Aires", km: 1140, on: true, src: "Aérienne (Directe) · Séparation directe — Transandin", nat: 'separation' },
  { a: "Pékin", b: "Singapour", km: 4470, on: true, src: "Aérienne (Directe) · Séparation directe — Asie de l'Est – Sud-Est", nat: 'separation' },
  { a: "Christchurch", b: "Sydney", km: 2130, on: true, src: "Aérienne (Directe) · Séparation directe — Rattachement du groupe McMurdo", nat: 'separation' },
  { a: "Ushuaïa", b: "Buenos Aires", km: 2370, on: true, src: "Aérienne (Directe) · Séparation directe — Rattachement du groupe antarctique sud-américain", nat: 'separation' },
  { a: "Le Cap", b: "Johannesbourg", km: 1270, on: true, src: "Aérienne (Directe) · Séparation directe — Rattachement du groupe Novolazarevskaya", nat: 'separation' },
  { a: "Le Cap", b: "Londres", km: 9670, on: true, src: "Aérienne (Directe) · Séparation directe — Axe Europe – Afrique", nat: 'separation' },
  { a: "Londres", b: "Buenos Aires", km: 11120, on: true, src: "Aérienne (Directe) · Séparation directe — Transatlantique", nat: 'separation' },
  { a: "Paris", b: "Los Angeles", km: 9100, on: true, src: "Aérienne (Directe) · Séparation directe — Transcontinental", nat: 'separation' },
  { a: "Paris", b: "Singapour", km: 10730, on: true, src: "Aérienne (Directe) · Séparation directe — Europe – Asie", nat: 'separation' },
  { a: "New York", b: "Johannesbourg", km: 12840, on: true, src: "Aérienne (Directe) · Séparation directe — Transatlantique Nord-Sud", nat: 'separation' },
  { a: "Pékin", b: "Sydney", km: 8960, on: true, src: "Aérienne (Directe) · Séparation directe — Asie – Océanie", nat: 'separation' },
  { a: "Johannesbourg", b: "Sydney", km: 11040, on: true, src: "Aérienne (Directe) · Séparation directe — Océan Indien Sud", nat: 'separation' },
  { a: "Pôle Nord", b: "Longyearbyen", km: 1310, on: true, src: "Géodésique / Orthodromique · Séparation directe — Pôle Nord – archipel du Svalbard", nat: 'separation' },
  { a: "Pôle Nord", b: "Tromsø", km: 2260, on: true, src: "Géodésique / Orthodromique · Séparation directe — Pôle Nord – Norvège du Nord", nat: 'separation' },
  { a: "Pôle Nord", b: "Reykjavík", km: 2870, on: true, src: "Géodésique / Orthodromique · Séparation directe — Pôle Nord – Islande", nat: 'separation' },
  { a: "Pôle Nord", b: "Londres", km: 4280, on: true, src: "Géodésique / Orthodromique · Séparation directe — Pôle Nord – Londres", nat: 'separation' },
  { a: "Longyearbyen", b: "Tromsø", km: 960, on: true, src: "Aérienne (Directe) · Séparation directe — Transversale arctique nord", nat: 'separation' },
  { a: "Reykjavík", b: "Londres", km: 1890, on: true, src: "Aérienne (Directe) · Séparation directe — Transversale Islande – Europe", nat: 'separation' },
  { a: "Tromsø", b: "Reykjavík", km: 1880, on: true, src: "Aérienne (Directe) · Séparation directe — Transversale arctique ouest", nat: 'separation' },
  { a: "Longyearbyen", b: "Reykjavík", km: 2010, on: true, src: "Aérienne (Directe) · Séparation directe — Svalbard – Islande", nat: 'separation' },
  { a: "Longyearbyen", b: "Londres", km: 3050, on: true, src: "Aérienne (Directe) · Séparation directe — Svalbard – Europe du Nord", nat: 'separation' },
  { a: "Tromsø", b: "Londres", km: 2280, on: true, src: "Aérienne (Directe) · Séparation directe — Norvège du Nord – Europe", nat: 'separation' },
  { a: "Base McMurdo", b: "Base Novolazarevskaya", km: 3410, on: true, src: "Séparation directe — Transversale trans-antarctique", nat: 'separation' },
  { a: "Base Novolazarevskaya", b: "Ushuaïa", km: 4060, on: true, src: "Séparation directe — Antarctique Est – Amérique du Sud", nat: 'separation' },
  { a: "Base McMurdo", b: "Hobart", km: 3980, on: true, src: "Séparation directe — Antarctique – Tasmanie", nat: 'separation' },
  { a: "Base Novolazarevskaya", b: "Christchurch", km: 7210, on: true, src: "Séparation directe — Trans-océanique australe", nat: 'separation' },
  { a: "Pôle Sud", b: "Base McMurdo", km: 1350, on: true, src: "Géodésique / Orthodromique · Séparation directe — Rayon polaire sud (lat 77,84° S)", nat: 'separation' },
  { a: "Pôle Sud", b: "Base Novolazarevskaya", km: 2140, on: true, src: "Géodésique / Orthodromique · Séparation directe — Rayon polaire sud (lat 70,78° S)", nat: 'separation' },
  { a: "Pôle Sud", b: "Ushuaïa", km: 3920, on: true, src: "Géodésique / Orthodromique · Séparation directe — Rayon polaire sud (lat 54,80° S)", nat: 'separation' },
  { a: "Pôle Sud", b: "Christchurch", km: 5170, on: true, src: "Géodésique / Orthodromique · Séparation directe — Rayon polaire sud (lat 43,53° S)", nat: 'separation' },
  { a: "Pôle Sud", b: "Hobart", km: 5240, on: true, src: "Géodésique / Orthodromique · Séparation directe — Rayon polaire sud (lat 42,88° S)", nat: 'separation' },
  { a: "Hobart", b: "Christchurch", km: 2040, on: true, src: "Aérienne (Directe) · Séparation directe — Transversale de verrouillage Océanie Sud", nat: 'separation' },
];

// ── Géométrie ───────────────────────────────────────────────────
type Pt = { x: number; y: number };

/** Intersection de deux cercles. Renvoie 0, 1 ou 2 points.
 *  Si les cercles ne se coupent pas, renvoie le point de compromis
 *  situé sur la droite qui les joint. */
function circleIntersect(p1: Pt, r1: number, p2: Pt, r2: number): Pt[] {
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const d = Math.hypot(dx, dy);
  if (d < 1e-9) return [];
  const ux = dx / d, uy = dy / d;
  if (d > r1 + r2 || d < Math.abs(r1 - r2)) {
    // pas d'intersection : compromis sur l'axe (respecte au mieux les deux rayons)
    const t = d > r1 + r2 ? r1 + (d - r1 - r2) / 2 : (r1 + (d + r2)) / 2;
    return [{ x: p1.x + ux * t, y: p1.y + uy * t }];
  }
  const a = (r1 * r1 - r2 * r2 + d * d) / (2 * d);
  const h2 = r1 * r1 - a * a;
  const h = Math.sqrt(Math.max(0, h2));
  const bx = p1.x + ux * a, by = p1.y + uy * a;
  if (h < 1e-9) return [{ x: bx, y: by }];
  return [{ x: bx - uy * h, y: by + ux * h }, { x: bx + uy * h, y: by - ux * h }];
}

/** Ordre d'insertion : ordre d'apparition des villes dans la liste des liaisons. */
function insertionOrder(legs: Leg[]): string[] {
  const seen: string[] = [];
  legs.forEach(l => { [l.a, l.b].forEach(c => { if (!seen.includes(c)) seen.push(c); }); });
  return seen;
}

/** Relaxation par ressorts : minimise la tension globale
 *  Σ (distance tracée − distance saisie)². */
function relax(pos: Map<string, Pt>, legs: Leg[], iterations = 4000) {
  const names = Array.from(pos.keys());
  const active = legs.filter(l => pos.has(l.a) && pos.has(l.b));
  if (active.length === 0) return;
  for (let it = 0; it < iterations; it++) {
    const g = new Map<string, Pt>(names.map(n => [n, { x: 0, y: 0 }]));
    for (const l of active) {
      const A = pos.get(l.a)!, B = pos.get(l.b)!;
      const dx = A.x - B.x, dy = A.y - B.y;
      const L = Math.hypot(dx, dy) + 1e-9;
      const c = 2 * (L - l.km) / L;
      const ga = g.get(l.a)!, gb = g.get(l.b)!;
      ga.x += c * dx; ga.y += c * dy;
      gb.x -= c * dx; gb.y -= c * dy;
    }
    const lr = 0.12 / active.length;
    for (const n of names) {
      const p = pos.get(n)!, gr = g.get(n)!;
      p.x -= lr * gr.x; p.y -= lr * gr.y;
    }
  }
}

/** Regroupe les villes en réseaux connexes (des liaisons les relient). */
function components(legs: Leg[]): string[][] {
  const parent = new Map<string, string>();
  const find = (x: string): string => {
    if (!parent.has(x)) parent.set(x, x);
    while (parent.get(x) !== x) { parent.set(x, parent.get(parent.get(x)!)!); x = parent.get(x)!; }
    return x;
  };
  legs.forEach(l => { const a = find(l.a), b = find(l.b); if (a !== b) parent.set(a, b); });
  const groups = new Map<string, string[]>();
  insertionOrder(legs).forEach(c => {
    const r = find(c);
    if (!groups.has(r)) groups.set(r, []);
    groups.get(r)!.push(c);
  });
  return Array.from(groups.values());
}

/** Place un réseau connexe : ancrage, puis trilatération, puis relaxation. */
function placeGroup(cities: string[], legs: Leg[]) {
  const pos = new Map<string, Pt>();
  const unconstrained: string[] = [];
  const own = legs.filter(l => cities.includes(l.a) && cities.includes(l.b));

  cities.forEach((city, i) => {
    if (i === 0) { pos.set(city, { x: 0, y: 0 }); return; }
    const links = own.filter(l =>
      (l.a === city && pos.has(l.b)) || (l.b === city && pos.has(l.a)));
    if (links.length === 0) {
      const ang = i * 2.399963;
      pos.set(city, { x: Math.cos(ang) * 3000, y: Math.sin(ang) * 3000 });
      unconstrained.push(city);
      return;
    }
    const ref = (l: Leg) => (l.a === city ? pos.get(l.b)! : pos.get(l.a)!);
    if (links.length === 1) {
      const p = ref(links[0]), d = links[0].km;
      const ang = pos.size === 1 ? 0 : i * 2.399963;
      pos.set(city, { x: p.x + Math.cos(ang) * d, y: p.y + Math.sin(ang) * d });
      return;
    }
    const cands = circleIntersect(ref(links[0]), links[0].km, ref(links[1]), links[1].km);
    if (cands.length === 0) { pos.set(city, { x: 0, y: 0 }); return; }
    let bestPt = cands[0], bestErr = Infinity;
    for (const c of cands) {
      let err = 0;
      for (const l of links.slice(2)) {
        const p = ref(l);
        err += (Math.hypot(c.x - p.x, c.y - p.y) - l.km) ** 2;
      }
      if (err < bestErr) { bestErr = err; bestPt = c; }
    }
    pos.set(city, bestPt);
  });

  relax(pos, own);
  return { pos, unconstrained };
}

/** Construit la carte : chaque réseau connexe est placé séparément,
 *  puis les réseaux sont disposés côte à côte sans se chevaucher. */
function buildMap(legs: Leg[]) {
  const groups = components(legs);
  const pos = new Map<string, Pt>();
  const unconstrained: string[] = [];
  const order: string[] = [];
  let offsetX = 0;

  groups.forEach(cities => {
    const g = placeGroup(cities, legs);
    const pts = Array.from(g.pos.values());
    const minX = Math.min(...pts.map(p => p.x)), maxX = Math.max(...pts.map(p => p.x));
    const minY = Math.min(...pts.map(p => p.y)), maxY = Math.max(...pts.map(p => p.y));
    const cy = (minY + maxY) / 2;
    cities.forEach(c => {
      const p = g.pos.get(c)!;
      pos.set(c, { x: p.x - minX + offsetX, y: p.y - cy });
      order.push(c);
    });
    unconstrained.push(...g.unconstrained);
    offsetX += (maxX - minX) + 2200;   // marge entre réseaux
  });

  return { pos, order, unconstrained, groups };
}

// ── Composant ───────────────────────────────────────────────────
export default function TrilaterationMap() {
  const [legs, setLegs] = useState<Leg[]>(SEED);
  const [unit, setUnit] = useState<'km' | 'nm'>('km');
  const [showLabels, setShowLabels] = useState(true);
  const [form, setForm] = useState({ a: '', b: '', km: '', src: '' });

  const activeLegs = useMemo(() => legs.filter(l => l.on), [legs]);
  const built = useMemo(() => buildMap(activeLegs), [activeLegs]);

  const conv = (km: number) => (unit === 'km' ? km : km / NM);
  const uLabel = unit === 'km' ? 'km' : 'NM';
  const fmt = (km: number) => conv(km).toLocaleString('fr-FR', { maximumFractionDigits: 0 });

  const visible = useMemo(() => {
    const { pos } = built;
    return activeLegs
      .filter(l => pos.has(l.a) && pos.has(l.b))
      .map(l => {
        const A = pos.get(l.a)!, B = pos.get(l.b)!;
        const drawn = Math.hypot(A.x - B.x, A.y - B.y);
        return { ...l, drawn, gap: drawn - l.km };
      });
  }, [built, activeLegs]);

  const view = useMemo(() => {
    const pts = Array.from(built.pos.values());
    if (pts.length === 0) return null;
    const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const w = Math.max(1, maxX - minX), h = Math.max(1, maxY - minY);
    const pad = 70;
    const S = Math.min((680 - 2 * pad) / w, (520 - 2 * pad) / h);
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    return { map: (p: Pt) => ({ x: 340 + (p.x - cx) * S, y: 260 + (p.y - cy) * S }), S };
  }, [built]);

  const addLeg = useCallback(() => {
    const km = Number(form.km);
    if (!form.a.trim() || !form.b.trim() || !km || km <= 0) return;
    setLegs(ls => [...ls, {
      a: form.a.trim(), b: form.b.trim(),
      km: unit === 'km' ? km : km * NM, on: true, nat: 'trajet',
      src: form.src.trim() || 'source non renseignée',
    }]);
    setForm({ a: '', b: '', km: '', src: '' });
  }, [form, unit]);

  const card: React.CSSProperties = {
    background: 'var(--card)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '14px 16px',
  };
  const input: React.CSSProperties = {
    background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--ink)',
    padding: '7px 9px', borderRadius: 6, fontFamily: MONO, fontSize: 13, width: '100%',
  };

  const scaleBar = useMemo(() => {
    if (!view) return null;
    const targets = [200, 500, 1000, 2000, 5000, 10000];
    const t = targets.find(v => v * view.S > 70 && v * view.S < 220) ?? 5000;
    return { km: t, px: t * view.S };
  }, [view]);

  const nCities = built.order.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* ═══ RÉGLAGES (en haut) ═══ */}
      <div style={{ ...card, display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 10, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 5, letterSpacing: '0.06em' }}>UNITÉ</div>
          <div style={{ display: 'flex', gap: 4 }}>
            {(['km', 'nm'] as const).map(u => (
              <button key={u} onClick={() => setUnit(u)}
                style={{
                  background: unit === u ? OPAL : 'var(--bg)', color: unit === u ? '#08130f' : 'var(--ink-soft)',
                  border: `1px solid ${unit === u ? OPAL : 'var(--border)'}`, padding: '6px 13px',
                  borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12, fontWeight: 700,
                }}>{u === 'km' ? 'KM' : 'MILLES NAUT.'}</button>
            ))}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 10, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 5, letterSpacing: '0.06em' }}>LIAISONS</div>
          <div style={{ display: 'flex', gap: 4 }}>
            <button onClick={() => setLegs(ls => ls.map(l => ({ ...l, on: true })))}
              style={{ background: 'var(--bg)', color: 'var(--ink-soft)', border: '1px solid var(--border)', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12 }}>
              TOUT COCHER
            </button>
            <button onClick={() => setLegs(ls => ls.map(l => ({ ...l, on: l.nat === 'trajet' })))}
              style={{ background: 'var(--bg)', color: 'var(--ink-soft)', border: '1px solid var(--border)', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12 }}>
              TRAJETS SEULS
            </button>
            <button onClick={() => setLegs(ls => ls.map(l => ({ ...l, on: l.nat === 'separation' })))}
              style={{ background: 'var(--bg)', color: 'var(--ink-soft)', border: '1px solid var(--border)', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12 }}>
              SÉPARATIONS SEULES
            </button>
            <button onClick={() => setLegs(ls => ls.map(l => ({ ...l, on: false })))}
              style={{ background: 'var(--bg)', color: 'var(--ink-soft)', border: '1px solid var(--border)', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12 }}>
              TOUT DÉCOCHER
            </button>
          </div>
        </div>
        <div>
          <div style={{ fontSize: 10, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 5, letterSpacing: '0.06em' }}>AFFICHAGE</div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 7, cursor: 'pointer', fontFamily: MONO, fontSize: 12, color: 'var(--ink-soft)' }}>
            <input type="checkbox" checked={showLabels} onChange={() => setShowLabels(v => !v)}
              style={{ width: 15, height: 15, accentColor: OPAL, cursor: 'pointer' }} />
            distances sur la carte
          </label>
        </div>
        <div style={{ marginLeft: 'auto', textAlign: 'right', fontFamily: MONO, fontSize: 11.5, color: 'var(--ink-muted)', lineHeight: 1.7 }}>
          <div><span style={{ color: GOLD, fontWeight: 700 }}>{nCities}</span> ville{nCities > 1 ? 's' : ''} placée{nCities > 1 ? 's' : ''}</div>
          <div><span style={{ color: OPAL, fontWeight: 700 }}>{visible.length}</span> / {legs.length} liaison{legs.length > 1 ? 's' : ''} active{visible.length > 1 ? 's' : ''}</div>
        </div>
      </div>

      {/* ═══ AJOUT D'UNE LIAISON (en haut) ═══ */}
      <div style={card}>
        <div style={{ fontSize: 10, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 8, letterSpacing: '0.06em' }}>
          AJOUTER UNE LIAISON
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 100px 1.7fr auto', gap: 8, alignItems: 'end' }}>
          <input style={input} placeholder="Ville A" value={form.a}
            onChange={e => setForm({ ...form, a: e.target.value })}
            onKeyDown={e => { if (e.key === 'Enter') addLeg(); }} />
          <input style={input} placeholder="Ville B" value={form.b}
            onChange={e => setForm({ ...form, b: e.target.value })}
            onKeyDown={e => { if (e.key === 'Enter') addLeg(); }} />
          <input style={input} type="number" placeholder={uLabel} value={form.km}
            onChange={e => setForm({ ...form, km: e.target.value })}
            onKeyDown={e => { if (e.key === 'Enter') addLeg(); }} />
          <input style={input} placeholder="Provenance (source)" value={form.src}
            onChange={e => setForm({ ...form, src: e.target.value })}
            onKeyDown={e => { if (e.key === 'Enter') addLeg(); }} />
          <button onClick={addLeg}
            style={{ background: OPAL, color: '#08130f', border: 'none', padding: '8px 18px', borderRadius: 6, fontFamily: MONO, fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>
            AJOUTER
          </button>
        </div>
      </div>

      {/* ═══ TOILE ═══ */}
      <div style={{ ...card, padding: 0, overflow: 'hidden' }}>
        <svg viewBox="0 0 680 520" style={{ width: '100%', maxHeight: '62vh', display: 'block', background: '#0d1117' }}>
          <rect width="680" height="520" fill="#0d1117" />
          {view && visible.map((l, i) => {
            const A = view.map(built.pos.get(l.a)!), B = view.map(built.pos.get(l.b)!);
            const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
            const tense = Math.abs(l.gap) / l.km > 0.02;
            return (
              <g key={i}>
                <line x1={A.x} y1={A.y} x2={B.x} y2={B.y}
                  stroke={tense ? ROSE : OPAL} strokeWidth={tense ? 1.4 : 1}
                  strokeDasharray={tense ? '5,3' : undefined} opacity="0.75" />
                {showLabels && (
                  <text x={mx} y={my - 4} fill={tense ? ROSE : '#8fa0b8'} fontSize="8.5"
                    fontFamily="monospace" textAnchor="middle">{fmt(l.km)} {uLabel}</text>
                )}
                {showLabels && tense && (
                  <text x={mx} y={my + 7} fill={ROSE} fontSize="7.5" fontFamily="monospace" textAnchor="middle">
                    tracé {fmt(l.drawn)} ({l.gap > 0 ? '+' : ''}{fmt(l.gap)})
                  </text>
                )}
              </g>
            );
          })}
          {view && (() => {
            const placed: { x: number; y: number }[] = [];
            return built.order.map(c => {
              const p = view.map(built.pos.get(c)!);
              const free = built.unconstrained.includes(c);
              let right = p.x < 500;
              // on essaie quelques décalages bornés, à droite puis à gauche,
              // pour éviter les cascades de libellés loin de leur point
              const slotFree = (x: number, y: number) =>
                !placed.some(q => Math.abs(q.x - x) < 88 && Math.abs(q.y - y) < 11.5);
              let ly = p.y + 4;
              const tries: [number, boolean][] = [[0, right], [0, !right], [13, right], [-13, right],
                [13, !right], [-13, !right], [26, right], [-26, right]];
              for (const [dy, side] of tries) {
                const ax = side ? p.x + 8 : p.x - 8;
                if (slotFree(ax, p.y + 4 + dy)) { ly = p.y + 4 + dy; right = side; break; }
              }
              placed.push({ x: right ? p.x + 8 : p.x - 8, y: ly });
              return (
                <g key={c}>
                  <circle cx={p.x} cy={p.y} r="4.5" fill={free ? '#6b7a8f' : GOLD}
                    stroke="#0d1117" strokeWidth="1.5" />
                  {Math.abs(ly - (p.y + 4)) > 6 && (
                    <line x1={p.x} y1={p.y} x2={right ? p.x + 6 : p.x - 6} y2={ly - 3}
                      stroke="#4a5b70" strokeWidth="0.6" />
                  )}
                  <text x={right ? p.x + 8 : p.x - 8} y={ly} fill="#c8d8e8" fontSize="10.5"
                    fontFamily="monospace" fontWeight="bold" textAnchor={right ? 'start' : 'end'}>{c}</text>
                </g>
              );
            });
          })()}
          {scaleBar && (
            <g transform="translate(24,496)">
              <line x1="0" y1="0" x2={scaleBar.px} y2="0" stroke="#8fa0b8" strokeWidth="1.5" />
              <line x1="0" y1="-4" x2="0" y2="4" stroke="#8fa0b8" strokeWidth="1.5" />
              <line x1={scaleBar.px} y1="-4" x2={scaleBar.px} y2="4" stroke="#8fa0b8" strokeWidth="1.5" />
              <text x={scaleBar.px / 2} y="-8" fill="#8fa0b8" fontSize="9" fontFamily="monospace" textAnchor="middle">
                {fmt(scaleBar.km)} {uLabel}
              </text>
            </g>
          )}
          {nCities === 0 && (
            <text x="340" y="260" fill="#4a5b70" fontSize="13" fontFamily="monospace" textAnchor="middle">
              toile vierge — cochez ou ajoutez une liaison
            </text>
          )}
        </svg>
      </div>

      <p style={{ fontSize: 12, color: 'var(--ink-muted)', fontStyle: 'italic', lineHeight: 1.6, margin: 0 }}>
        La première ville sert d&apos;ancrage, la deuxième se place à la distance donnée (orientation libre), les
        suivantes par trilatération sur les villes déjà placées. Les liaisons en <span style={{ color: ROSE }}>rose
        pointillé</span> ne peuvent pas être respectées exactement : le tracé applique le meilleur compromis et
        l&apos;écart est indiqué. Un point <span style={{ color: '#6b7a8f' }}>gris</span> signale une ville sans
        distance connue vers le réseau déjà placé.
      </p>

      {/* ═══ DONNÉES ═══ */}
      <div style={card}>
        <div style={{ fontSize: 10, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 8, letterSpacing: '0.06em' }}>
          DONNÉES — {legs.length} LIAISON{legs.length > 1 ? 'S' : ''}
        </div>
        <div style={{ maxHeight: 340, overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ color: 'var(--ink-muted)', fontFamily: MONO, fontSize: 9.5, textAlign: 'left' }}>
                <th style={{ padding: '4px 6px', width: 28 }} title="Activer / désactiver">ON</th>
                <th style={{ padding: '4px 6px' }}>LIAISON</th>
                <th style={{ padding: '4px 6px', width: 96 }}>SAISI ({uLabel})</th>
                <th style={{ padding: '4px 6px', width: 104 }}>TRACÉ</th>
                <th style={{ padding: '4px 6px' }}>PROVENANCE</th>
                <th style={{ padding: '4px 6px', width: 28 }} />
              </tr>
            </thead>
            <tbody>
              {legs.map((l, i) => {
                const v = visible.find(x => x.a === l.a && x.b === l.b && x.km === l.km);
                const tense = v && Math.abs(v.gap) / l.km > 0.02;
                return (
                  <tr key={i} style={{ borderTop: '1px solid var(--border-soft)', opacity: l.on ? 1 : 0.42 }}>
                    <td style={{ padding: '4px 6px' }}>
                      <input type="checkbox" checked={l.on}
                        onChange={() => setLegs(ls => ls.map((x, k) => k === i ? { ...x, on: !x.on } : x))}
                        style={{ width: 15, height: 15, accentColor: OPAL, cursor: 'pointer' }} />
                    </td>
                    <td style={{ padding: '4px 6px', fontFamily: MONO, color: 'var(--ink)' }}>
                      <span style={{ fontSize: 8.5, fontWeight: 700, color: l.nat === 'separation' ? GOLD : OPAL, border: `1px solid ${l.nat === 'separation' ? GOLD : OPAL}55`, borderRadius: 3, padding: '1px 4px', marginRight: 6 }}>
                        {l.nat === 'separation' ? 'SÉP' : 'TRAJ'}
                      </span>{l.a} – {l.b}</td>
                    <td style={{ padding: '4px 6px' }}>
                      <input type="number" value={Math.round(conv(l.km))}
                        onChange={e => {
                          const val = Number(e.target.value) || 0;
                          setLegs(ls => ls.map((x, k) => k === i ? { ...x, km: unit === 'km' ? val : val * NM } : x));
                        }}
                        style={{ ...input, width: 82, padding: '3px 6px', fontSize: 12 }} />
                    </td>
                    <td style={{ padding: '4px 6px', fontFamily: MONO, fontSize: 11.5, color: tense ? ROSE : 'var(--ink-muted)' }}>
                      {v ? `${fmt(v.drawn)}${tense ? ` (${v.gap > 0 ? '+' : ''}${fmt(v.gap)})` : ''}` : '—'}
                    </td>
                    <td style={{ padding: '4px 6px', color: 'var(--ink-muted)', fontSize: 10.5 }}>{l.src}</td>
                    <td style={{ padding: '4px 6px' }}>
                      <button onClick={() => setLegs(ls => ls.filter((_, k) => k !== i))} title="Supprimer"
                        style={{ background: 'none', border: 'none', color: ROSE, cursor: 'pointer', fontSize: 15 }}>×</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
