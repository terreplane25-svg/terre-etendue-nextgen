/**
 * Composants utilitaires pour appliquer les polices TEI
 * Remplacent les inline style={{fontFamily: '...'}} par des classes Tailwind
 */

import React from 'react';

interface FontProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  className?: string;
}

/**
 * <FontOrbitron> — Titres sci-fi (Orbitron)
 * Usage: <FontOrbitron>Titre</FontOrbitron>
 */
export const FontOrbitron: React.FC<FontProps> = ({ children, className = '', ...props }) => (
  <span className={`font-orbitron ${className}`} {...props}>
    {children}
  </span>
);

/**
 * <FontTechMono> — Données, tags, timestamps (Share Tech Mono)
 * Usage: <FontTechMono>DATA_123</FontTechMono>
 */
export const FontTechMono: React.FC<FontProps> = ({ children, className = '', ...props }) => (
  <span className={`font-tech-mono ${className}`} {...props}>
    {children}
  </span>
);

/**
 * <FontRajdhani> — Navigation, descriptions (Rajdhani)
 * Usage: <FontRajdhani>Description</FontRajdhani>
 */
export const FontRajdhani: React.FC<FontProps> = ({ children, className = '', ...props }) => (
  <span className={`font-rajdhani ${className}`} {...props}>
    {children}
  </span>
);

/**
 * <FontArabic> — Texte arabe, citations coraniques (Amiri)
 * Usage: <FontArabic>النص العربي</FontArabic>
 */
export const FontArabic: React.FC<FontProps> = ({ children, className = '', ...props }) => (
  <span className={`font-arabic ${className}`} {...props}>
    {children}
  </span>
);

/**
 * Utilitaire pour convertir inline style {{fontFamily: '...'}} en className
 * @deprecated Préférer les composants <FontOrbitron>, <FontTechMono>, etc.
 * 
 * Usage :
 * const fontClass = getFontClass('Orbitron'); // => 'font-orbitron'
 */
export function getFontClass(
  fontName: 'Orbitron' | 'Share Tech Mono' | 'Rajdhani' | 'Source Serif 4' | 'Amiri' | string
): string {
  const mapping: Record<string, string> = {
    'Orbitron': 'font-orbitron',
    'Share Tech Mono': 'font-tech-mono',
    'Rajdhani': 'font-rajdhani',
    'Source Serif 4': 'font-body',
    'Amiri': 'font-arabic',
  };
  return mapping[fontName] || 'font-rajdhani';
}
