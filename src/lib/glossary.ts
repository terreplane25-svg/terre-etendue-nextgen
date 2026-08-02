import fs from 'fs';
import path from 'path';

// ═══════════════════════════════════════════════════════════════════════════
// GLOSSAIRE INTERACTIF
//
// Le glossaire vit dans content/articles/glossaire.json — source unique. Ce
// module en extrait les termes et annote automatiquement le corps des articles
// au moment du rendu serveur : première occurrence de chaque terme soulignée,
// définition en bulle au survol ou au focus. Aucun JavaScript côté client.
//
// Ajouter une entrée au glossaire suffit : elle s'applique seule à tout le site.
// ═══════════════════════════════════════════════════════════════════════════

export type GlossaryTerm = {
  term: string;
  aliases: string[];
  definition: string;
};

const glossaryPath = path.join(process.cwd(), 'content/articles/glossaire.json');

// Termes trop courants comme mots ordinaires : ils restent dans le glossaire,
// mais ne sont pas auto-annotés dans les textes sous peine de faux positifs.
const NE_PAS_AUTO_LIER = new Set(['dynamique', 'cinématique']);

// Alias supplémentaires déclarés à la main, quand la forme entre parenthèses
// est elle-même un terme employé dans les articles.
const ALIAS_SUPPLEMENTAIRES: Record<string, string[]> = {
  'Redshift (décalage vers le rouge)': ['décalage vers le rouge'],
  'Éther (luminifère)': ['éther luminifère'],
  'Mufassir (pl. mufassirūn)': ['mufassirūn'],
  'Van der Waals (forces de)': ['forces de Van der Waals'],
  'Coefficient de réfraction (k)': ['coefficient de réfraction'],
  'EM (Électromagnétisme)': [],
  'Hypothèse nulle (H₀)': ['hypothèse nulle'],
  'OBT (Orbite Basse Terrestre)': ['orbite basse terrestre'],
  'Curve-fitting (ajustement de courbe)': ['ajustement de courbe'],
  'Tired Light (fatigue lumineuse)': ['fatigue lumineuse'],
  'Ligne de changement de date (LID)': ['ligne de changement de date'],
};

function stripTags(html: string): string {
  return html
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function decodeBasic(s: string): string {
  return s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"');
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

let cache: GlossaryTerm[] | null = null;

export function getGlossaryTerms(): GlossaryTerm[] {
  if (cache) return cache;

  let raw = '';
  try {
    raw = JSON.parse(fs.readFileSync(glossaryPath, 'utf8')).htmlBody || '';
  } catch {
    cache = [];
    return cache;
  }

  const terms: GlossaryTerm[] = [];
  const re = /<li><strong>(.*?)<\/strong>\s*—\s*([\s\S]*?)<\/li>/g;
  let m: RegExpExecArray | null;

  while ((m = re.exec(raw)) !== null) {
    const label = decodeBasic(stripTags(m[1]));
    const definition = decodeBasic(stripTags(m[2]));
    if (!label || !definition) continue;

    // Alias principal : la partie avant une éventuelle parenthèse.
    const base = label.replace(/\s*\([^)]*\)\s*$/, '').trim();
    const aliases = new Set<string>();
    if (base.length >= 4 && !NE_PAS_AUTO_LIER.has(base.toLowerCase())) aliases.add(base);
    for (const extra of ALIAS_SUPPLEMENTAIRES[label] || []) {
      if (extra.length >= 4) aliases.add(extra);
    }

    if (aliases.size === 0) continue;
    terms.push({ term: label, aliases: [...aliases], definition });
  }

  // Les alias les plus longs d'abord : « coefficient de réfraction » doit
  // l'emporter sur « réfraction atmosphérique » si les deux peuvent matcher.
  terms.sort((a, b) => Math.max(...b.aliases.map((x) => x.length)) - Math.max(...a.aliases.map((x) => x.length)));
  cache = terms;
  return cache;
}

// Un alias tout en majuscules et court est un sigle : on le matche en
// respectant la casse, sinon « BEC » attraperait « bec ».
function isSigle(alias: string): boolean {
  return alias.length <= 5 && alias === alias.toUpperCase() && /[A-ZΛ]/.test(alias);
}

// Éléments dans lesquels on n'annote jamais : titres, liens, code, SVG
// (qui contient des <text>), et les libellés d'encadrés.
const BALISES_INTERDITES = new Set(['a', 'code', 'pre', 'svg', 'h1', 'h2', 'h3', 'h4', 'sup', 'sub', 'script', 'style', 'abbr']);

/**
 * Annote la première occurrence de chaque terme du glossaire dans un corps
 * d'article. Ne touche jamais au contenu des balises ni aux éléments interdits.
 */
export function annotateGlossary(html: string, slug?: string): string {
  if (!html) return html;
  if (slug === 'glossaire' || slug === 'index-thematique') return html;

  const terms = getGlossaryTerms();
  if (terms.length === 0) return html;

  const parAlias = new Map<string, GlossaryTerm>();
  const motifs: string[] = [];
  for (const t of terms) {
    for (const a of t.aliases) {
      parAlias.set(a.toLowerCase(), t);
      // Pluriel toléré sur les alias d'un seul mot.
      const pluriel = !a.includes(' ') && !isSigle(a) ? 's?' : '';
      motifs.push(escapeRegExp(a) + pluriel);
    }
  }

  // Lookarounds Unicode : \b n'est pas fiable sur les lettres accentuées.
  const motif = new RegExp(`(?<![\\p{L}\\p{N}_-])(${motifs.join('|')})(?![\\p{L}\\p{N}_-])`, 'giu');

  const utilises = new Set<string>();
  const morceaux = html.split(/(<[^>]+>)/);
  let profondeurInterdite = 0;
  let compteur = 0;

  for (let i = 0; i < morceaux.length; i++) {
    const morceau = morceaux[i];

    if (morceau.startsWith('<')) {
      const balise = /^<\s*(\/?)\s*([a-zA-Z][a-zA-Z0-9]*)/.exec(morceau);
      if (balise) {
        const fermante = balise[1] === '/';
        const nom = balise[2].toLowerCase();
        const autoFermante = /\/\s*>$/.test(morceau);
        if (BALISES_INTERDITES.has(nom) && !autoFermante) {
          if (fermante) profondeurInterdite = Math.max(0, profondeurInterdite - 1);
          else profondeurInterdite++;
        }
      }
      continue;
    }

    if (profondeurInterdite > 0 || !morceau.trim()) continue;

    morceaux[i] = morceau.replace(motif, (found) => {
      const cle = found.toLowerCase().replace(/s$/, '');
      const t = parAlias.get(found.toLowerCase()) || parAlias.get(cle);
      if (!t || utilises.has(t.term)) return found;

      // Un sigle ne se matche qu'à la casse exacte.
      const aliasExact = t.aliases.find(
        (a) => a.toLowerCase() === found.toLowerCase() || a.toLowerCase() === cle,
      );
      if (aliasExact && isSigle(aliasExact) && aliasExact !== found) return found;

      utilises.add(t.term);
      // aria-describedby plutôt que role="button" : le terme reste du texte
      // ordinaire, et la définition n'est annoncée qu'à la prise de focus au
      // lieu d'être lue en plein milieu de la phrase.
      const id = `gloss-${slug || 'art'}-${++compteur}`;
      return (
        `<span class="tei-gloss" tabindex="0" aria-describedby="${id}">` +
        `${found}` +
        `<span class="tei-gloss-bulle" id="${id}" role="tooltip">` +
        `<strong>${escapeHtml(t.term)}</strong>${escapeHtml(t.definition)}` +
        `</span></span>`
      );
    });
  }

  return morceaux.join('');
}
