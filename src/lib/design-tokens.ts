// ═══════════════════════════════════════════
// TERRE ÉTENDUE ISLAM — DASHBOARD DESIGN TOKENS
// White Mode Academic Dashboard
// ═══════════════════════════════════════════

export const dash = {
  // ── Surfaces ──
  bg: "#F4F5F7",
  bgWarm: "#F8F7F5",
  card: "#FFFFFF",
  cardHover: "#FAFBFC",

  // ── Ink ──
  ink: "#1A1D23",
  inkSoft: "#4A4E57",
  inkMuted: "#8B8F96",
  inkGhost: "#B8BBC2",

  // ── Borders ──
  border: "#E8EAED",
  borderSoft: "#F0F1F3",

  // ── Accents ──
  lavender: "#8B7EC8",
  lavenderSoft: "#EFEAFF",
  saffron: "#D4943A",
  saffronSoft: "#FFF4E4",
  opal: "#3D9E7C",
  opalSoft: "#E6F7F0",
  cyan: "#3B8FD4",
  cyanSoft: "#E8F4FD",
  rose: "#C45E6A",
  roseSoft: "#FDE8EA",

  // ── Sacred (Quranic) ──
  gold: "#B8941F",
  goldSoft: "#FBF5E4",

  // ── Shadows ──
  shadow: "0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)",
  shadowMd: "0 2px 6px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)",
  shadowLg: "0 4px 12px rgba(0,0,0,0.05), 0 16px 40px rgba(0,0,0,0.08)",

  // ── Radii ──
  radius: "16px",
  radiusSm: "10px",
  radiusXs: "6px",

  // ── Fonts ──
  fontMain: "'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif",
  fontMono: "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
  fontArabic: "'Amiri', 'Noto Naskh Arabic', serif",
} as const;

// ── Pillar definitions ──
export const PILLARS = [
  { id: "headquarters", num: "01", name: "Le Quartier Général", sub: "Épistémologie & Méthode", icon: "◎", color: dash.lavender, colorSoft: dash.lavenderSoft, href: "/headquarters" },
  { id: "observatory", num: "02", name: "L'Observatoire", sub: "Données empiriques", icon: "◉", color: dash.cyan, colorSoft: dash.cyanSoft, href: "/observatory" },
  { id: "library", num: "03", name: "La Bibliothèque", sub: "Sources sacrées & historiques", icon: "▣", color: dash.saffron, colorSoft: dash.saffronSoft, href: "/library" },
  { id: "lab", num: "04", name: "Le Lab", sub: "Modélisation 3D", icon: "△", color: dash.opal, colorSoft: dash.opalSoft, href: "/lab" },
  { id: "experiences", num: "05", name: "Les Expériences", sub: "Physique naturelle", icon: "⬡", color: dash.rose, colorSoft: dash.roseSoft, href: "/experiences" },
] as const;

// ── Tag color map ──
export const TAG_COLORS: Record<string, { bg: string; color: string }> = {
  optique: { bg: dash.cyanSoft, color: dash.cyan },
  horizon: { bg: dash.lavenderSoft, color: dash.lavender },
  perspective: { bg: dash.lavenderSoft, color: dash.lavender },
  réfraction: { bg: dash.lavenderSoft, color: dash.lavender },
  visibilité: { bg: dash.opalSoft, color: dash.opal },
  données: { bg: dash.saffronSoft, color: dash.saffron },
  mécanique: { bg: dash.roseSoft, color: dash.rose },
  historique: { bg: "#F3F0E8", color: "#8B7A54" },
  physique: { bg: dash.lavenderSoft, color: dash.lavender },
  densité: { bg: dash.opalSoft, color: dash.opal },
  expériences: { bg: dash.cyanSoft, color: dash.cyan },
  "physique-naturelle": { bg: dash.opalSoft, color: dash.opal },
  magnétisme: { bg: dash.saffronSoft, color: dash.saffron },
  vision: { bg: dash.roseSoft, color: dash.rose },
  forces: { bg: dash.saffronSoft, color: dash.saffron },
};
