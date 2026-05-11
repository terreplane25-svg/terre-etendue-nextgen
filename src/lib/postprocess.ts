/**
 * Post-processeur HTML pour articles Terre Étendue Islam
 * Détecte les patterns dans le HTML rendu et les enrichit visuellement.
 */

// ─── Numéros de section dans les titres h2 ────────
function styleSectionNumbers(html: string): string {
  // h2 qui commencent par "01 ", "02 ", etc.
  return html.replace(
    /<h2([^>]*)>(\d{1,2})\s+/gi,
    '<h2$1><span class="section-number">$2</span>'
  );
}

// ─── Blocs "En termes simples" / "Résumé" ────────
function styleInfoBoxes(html: string): string {
  // Pattern: <p>💡 En termes simples</p> followed by <p>...</p>
  let result = html;

  // Detect emoji-prefixed standalone labels followed by content
  result = result.replace(
    /<p>([💡📌🔑⚠️🎯✨📖🔬⚗️📋🧪])\s*(En termes simples|Résumé|Point clé|À retenir|En bref|Note importante|Important)\s*<\/p>\s*<p>([\s\S]*?)<\/p>/gi,
    '<div class="info-box"><div class="info-box__header"><span class="info-box__icon">$1</span><span class="info-box__label">$2</span></div><div class="info-box__content"><p>$3</p></div></div>'
  );

  return result;
}

// ─── Blocs de protocole / étapes numérotées ────────
function styleProtocols(html: string): string {
  let result = html;

  // Detect "Protocole en X étapes" as a header for a steps block
  result = result.replace(
    /<p>(Protocole en \d+ étapes|Méthodologie|Les étapes|Procédure)\s*/gi,
    '<div class="protocol-box"><div class="protocol-box__header">$1</div><p>'
  );

  return result;
}

// ─── Citations avec « guillemets » ────────────────
function styleFrenchQuotes(html: string): string {
  let result = html;

  // Pattern: paragraph starting with « and containing » — attribution
  result = result.replace(
    /<p>(«\s[\s\S]*?»)\s*\n?\s*—\s*([\s\S]*?)<\/p>/gi,
    '<blockquote class="styled-quote"><div class="styled-quote__text">$1</div><cite class="styled-quote__cite">— $2</cite></blockquote>'
  );

  // Pattern: paragraph starting with « without attribution
  result = result.replace(
    /<p>(«\s[\s\S]*?»)\s*<\/p>/gi,
    (match, content) => {
      // Only if not already inside a blockquote
      if (content.length > 80) {
        return `<blockquote class="styled-quote"><div class="styled-quote__text">${content}</div></blockquote>`;
      }
      return match;
    }
  );

  return result;
}

// ─── Résultats / conclusions en gras ──────────────
function styleKeyResults(html: string): string {
  let result = html;

  // Pattern: <p><strong>Le résultat...</strong> or <strong>Ce hadith est décisif</strong>
  result = result.replace(
    /<p><strong>(Le résultat[^<]*|Ce hadith est décisif[^<]*|Résultat[^<]*|Conclusion[^<]*):?\s*:?<\/strong>\s*/gi,
    '<div class="key-result"><div class="key-result__label">$1</div><p>'
  );

  return result;
}

// ─── Tables en texte plat → détection ─────────────
function styleInlineTables(html: string): string {
  // Tables that were lost in conversion appear as text with columns
  // We'll wrap consecutive lines with similar structure
  return html;
}

// ─── Versets coraniques ───────────────────────────
function styleQuranVerses(html: string): string {
  let result = html;

  // Pattern: Sourate Name (XX:YY)
  result = result.replace(
    /(Sourate\s+[\w\-']+\s*\(\d+:\d+(?:-\d+)?\))/gi,
    '<span class="quran-ref">$1</span>'
  );

  // Pattern: s88 v20, s13 v3 etc
  result = result.replace(
    /\b(s\d+\s*v\d+)\b/gi,
    '<span class="quran-ref-short">$1</span>'
  );

  return result;
}

// ─── Hadiths et sources ───────────────────────────
function styleHadithRefs(html: string): string {
  let result = html;

  // Pattern: — Sunan Abi Dawud, hadith XXXX  or — Sahih Muslim, etc.
  result = result.replace(
    /—\s*(Sunan[^<,]*|Sahih[^<,]*|Musnad[^<,]*|Jami[^<,]*|Bukhari[^<,]*|Muslim[^<,]*)/gi,
    '<span class="hadith-ref">— $1</span>'
  );

  return result;
}

// ─── Pipeline principal ───────────────────────────
export function postProcessArticleHtml(html: string): string {
  let result = html;

  result = styleSectionNumbers(result);
  result = styleInfoBoxes(result);
  result = styleFrenchQuotes(result);
  result = styleKeyResults(result);
  result = styleQuranVerses(result);
  result = styleHadithRefs(result);

  return result;
}
