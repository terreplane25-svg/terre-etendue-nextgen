/**
 * Configuration centralisée des polices — Terre Étendue Islam
 * Utilise next/font/google pour optimiser le chargement et le LCP
 */

import { Orbitron, Share_Tech_Mono, Rajdhani, Source_Serif_4, Amiri } from 'next/font/google';

/**
 * ORBITRON — Titres, labels, sections (sci-fi, angulaire)
 * Poids : 400 (regular), 700 (bold), 900 (heavy)
 */
export const orbitron = Orbitron({
  subsets: ['latin'],
  weight: ['400', '700', '900'],
  variable: '--font-orbitron',
  display: 'swap',
  fallback: ['sans-serif'],
});

/**
 * SHARE TECH MONO — Données, tags, timestamps (terminal, monospace)
 * Poids : 400 (regular seulement disponible)
 */
export const shareMonoTech = Share_Tech_Mono({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-tech-mono',
  display: 'swap',
  fallback: ['monospace'],
});

/**
 * RAJDHANI — Sous-titres, descriptions, navigation (technique, lisible)
 * Poids : 400, 500, 600, 700
 */
export const rajdhani = Rajdhani({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-raj',
  display: 'swap',
  fallback: ['sans-serif'],
});

/**
 * SOURCE SERIF 4 — Corps des articles (lecture longue confortable)
 * Poids : 400 (regular)
 */
export const sourceSerif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
  fallback: ['serif'],
});

/**
 * AMIRI — Texte arabe, citations coraniques (calligraphique, doré)
 * Poids : 400, 700
 */
export const amiri = Amiri({
  subsets: ['arabic', 'latin'],
  weight: ['400', '700'],
  variable: '--font-amiri',
  display: 'swap',
  fallback: ['serif'],
});

/**
 * Liste des variables CSS pour utilisation globale
 * À intégrer dans className du <html>
 */
export const fontVariables = [
  orbitron.variable,
  shareMonoTech.variable,
  rajdhani.variable,
  sourceSerif.variable,
  amiri.variable,
].join(' ');
