/**
 * TERRE ÉTENDUE ISLAM — Design Tokens
 * "La Revue de Cosmologie d'Avant-Garde"
 * 
 * Ce fichier centralise TOUS les tokens du thème éditorial.
 * Importé par les composants qui ont besoin de valeurs JS (inline styles, Framer Motion).
 * Les CSS variables correspondantes sont dans globals.css pour Tailwind.
 */

export const editorial = {
  // ─── Surfaces ───
  bg:        "#FAFAF8",
  bgWarm:    "#F5F2ED",
  bgDeep:    "#EDE8E0",
  card:      "#FFFFFF",

  // ─── Ink (texte) ───
  ink:       "#0C0A09",
  inkSoft:   "#2C2825",
  inkMuted:  "#6B6560",
  inkGhost:  "#A09890",

  // ─── Rules (lignes) ───
  rule:      "#D6D0C8",
  ruleFaint: "#E8E2DA",

  // ─── Accents ───
  bronze:    "#8B6914",
  bronzeL:   "#C49B30",
  bronzeBg:  "rgba(139,105,20,0.06)",

  green:     "#1B6B45",
  greenBg:   "rgba(27,107,69,0.05)",

  indigo:    "#3B3F8C",
  indigoBg:  "rgba(59,63,140,0.04)",

  coral:     "#8B3A2A",
  coralBg:   "rgba(139,58,42,0.05)",

  // ─── Fonts ───
  fontDisplay:  "'Cormorant Garamond', 'Georgia', serif",
  fontBody:     "'Crimson Pro', 'Georgia', serif",
  fontLabel:    "'Cinzel', 'Georgia', serif",
  fontSans:     "'DM Sans', 'Helvetica Neue', sans-serif",
  fontMono:     "'JetBrains Mono', 'Consolas', monospace",
  fontArabic:   "'Amiri', 'Traditional Arabic', serif",

  // ─── Easing ───
  easeOut: "cubic-bezier(0.16, 1, 0.3, 1)",
  easeSmooth: "cubic-bezier(0.4, 0, 0.2, 1)",

  // ─── Pillar colors ───
  pillarColors: {
    headquarters: "#0C0A09",
    observatory:  "#1B6B45",
    library:      "#8B6914",
    lab:          "#3B3F8C",
    nexus:        "#8B3A2A",
  } as const,

  // ─── Pillar labels ───
  pillarLabels: {
    headquarters: "Épistémologie",
    observatory:  "Empirique",
    library:      "Sources Sacrées",
    lab:          "Modélisation 3D",
    nexus:        "Graphe de Connaissances",
  } as const,

  // ─── Pillar numerals ───
  pillarNumerals: {
    headquarters: "I",
    observatory:  "II",
    library:      "III",
    lab:          "IV",
    nexus:        "⬡",
  } as const,
} as const;

export type PillarSlug = keyof typeof editorial.pillarColors;
