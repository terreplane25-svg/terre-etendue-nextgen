#!/usr/bin/env python3
"""
Export clean .txt files from JSON articles for audio narration.
Reads from content/articles/, writes to exports/audio-scripts/.
"""

import json
import os
import re
import textwrap
from html.parser import HTMLParser
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLES_DIR = BASE_DIR / "content" / "articles"
OUTPUT_DIR = BASE_DIR / "exports" / "audio-scripts"

SLUGS = {
    "headquarters": [
        "200-ans-de-resultats-nuls-darago-a-einstein",
        "chronologie-de-la-tromperie-du-globe",
        "dune-terre-plate-universelle-a-la-sphere-grecque",
        "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
        "la-cosmologie-comme-instrument-de-domination",
        "le-concordisme",
        "le-mouvement-zetetique-150-ans-de-resistance",
        "les-distances-cosmiques-au-dela-de-la-regle",
        "les-trous-noirs-nexistent-pas",
        "pourquoi-tout-remettre-en-question",
    ],
    "observatory": [
        "experiences-sous-pression-reduite",
        "la-perspective-lineaire",
        "le-pendule-de-foucault-une-preuve-contestee",
        "le-pole-sud-nexiste-pas",
        "les-horloges-atomiques-ne-prouvent-rien",
        "les-marees-contre-lheliocentrisme",
        "les-telescopes-et-la-courbure-terrestre",
        "pourquoi-les-choses-montent-et-descendent",
    ],
    "library": [
        "la-terre-dans-le-coran",
        "la-qibla-et-la-direction-cote-ouest",
        "mise-en-garde-la-kaaba-et-saturne",
        "sources-historiques-le-fonds-documentaire-1865-1920",
    ],
    "meta": [
        "glossaire",
        "index-thematique",
        "manifeste",
        "methodologie",
        "ethique-intellectuelle",
    ],
}

# Map requested slugs to actual filenames (handle mismatches)
SLUG_TO_FILE = {
    "sources-historiques-le-fonds-documentaire-1865-1920": "sources-historiques-fonds-documentaire",
}

CATEGORY_LABELS = {
    "headquarters": "Quartier General",
    "observatory": "Observatoire",
    "library": "Bibliotheque",
    "meta": "Meta",
}

WRAP_WIDTH = 80


# ── HTML to Text Converter ─────────────────────────────────────

class HTMLToTextConverter(HTMLParser):
    """Convert HTML to clean, readable plain text."""

    def __init__(self):
        super().__init__()
        self.output = []
        self.current_tag = None
        self.tag_stack = []
        self.in_blockquote = False
        self.blockquote_text = []
        self.blockquote_cite = ""
        self.in_cite = False
        self.in_svg = False
        self.svg_depth = 0
        self.in_table = False
        self.table_headers = []
        self.table_rows = []
        self.current_row = []
        self.current_cell = ""
        self.in_cell = False
        self.in_header_cell = False
        self.in_figcaption = False
        self.in_figure = False
        self.skip_tags = {"script", "style", "img", "figure"}
        self.inline_tags = {"strong", "b", "em", "i", "a", "span", "code"}
        self.list_depth = 0
        self.in_list_item = False
        self.list_item_text = []
        self.ordered_list = False
        self.list_counters = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "svg":
            self.in_svg = True
            self.svg_depth = 1
            return
        if self.in_svg:
            self.svg_depth += 1
            return

        self.tag_stack.append(tag)

        if tag in ("h2", "h3"):
            self.current_tag = tag
            self.output.append("\n\n")
            return

        if tag == "blockquote":
            self.in_blockquote = True
            self.blockquote_text = []
            self.blockquote_cite = ""
            return

        if tag == "cite" and self.in_blockquote:
            self.in_cite = True
            return

        if tag == "table":
            self.in_table = True
            self.table_headers = []
            self.table_rows = []
            return

        if tag == "tr":
            self.current_row = []
            return

        if tag == "th":
            self.in_header_cell = True
            self.current_cell = ""
            return

        if tag == "td":
            self.in_cell = True
            self.current_cell = ""
            return

        if tag == "figure":
            self.in_figure = True
            return

        if tag == "figcaption":
            self.in_figcaption = True
            return

        if tag in ("ul", "ol"):
            self.list_depth += 1
            self.ordered_list = tag == "ol"
            self.list_counters.append(0)
            return

        if tag == "li":
            self.in_list_item = True
            self.list_item_text = []
            if self.list_counters:
                self.list_counters[-1] += 1
            return

        if tag == "p":
            if not self.in_blockquote and not self.in_cell:
                self.output.append("\n\n")
            return

        if tag == "br":
            if self.in_list_item:
                self.list_item_text.append("\n")
            elif self.in_blockquote:
                self.blockquote_text.append("\n")
            else:
                self.output.append("\n")
            return

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg_depth -= 1
            if self.svg_depth <= 0:
                self.in_svg = False
                self.svg_depth = 0
            return
        if self.in_svg:
            if tag == "svg":
                self.svg_depth -= 1
                if self.svg_depth <= 0:
                    self.in_svg = False
            return

        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag in ("h2", "h3"):
            self.output.append("\n")
            self.current_tag = None
            return

        if tag == "cite" and self.in_blockquote:
            self.in_cite = False
            return

        if tag == "blockquote":
            self._flush_blockquote()
            self.in_blockquote = False
            return

        if tag == "th":
            self.in_header_cell = False
            self.table_headers.append(self.current_cell.strip())
            self.current_cell = ""
            return

        if tag == "td":
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
            self.current_cell = ""
            return

        if tag == "tr":
            if self.current_row:
                self.table_rows.append(self.current_row)
            return

        if tag == "table":
            self._flush_table()
            self.in_table = False
            return

        if tag == "figcaption":
            self.in_figcaption = False
            return

        if tag == "figure":
            self.in_figure = False
            return

        if tag in ("ul", "ol"):
            self.list_depth -= 1
            if self.list_counters:
                self.list_counters.pop()
            if self.list_depth == 0:
                self.output.append("\n")
            return

        if tag == "li":
            self._flush_list_item()
            self.in_list_item = False
            return

    def handle_data(self, data):
        if self.in_svg:
            return

        if self.in_figure and not self.in_figcaption:
            return

        if self.in_figcaption:
            # Skip figure captions (they reference images)
            return

        text = data

        if self.in_cite and self.in_blockquote:
            self.blockquote_cite += text
            return

        if self.in_blockquote:
            self.blockquote_text.append(text)
            return

        if self.in_header_cell or self.in_cell:
            self.current_cell += text
            return

        if self.in_list_item:
            self.list_item_text.append(text)
            return

        if self.current_tag in ("h2", "h3"):
            # Strip section numbers like "01", "02" etc.
            cleaned = re.sub(r"^\d{2}\s*", "", text.strip())
            if cleaned:
                level = "=" if self.current_tag == "h2" else "-"
                header_line = cleaned.upper() if self.current_tag == "h2" else cleaned
                separator = level * min(len(header_line), WRAP_WIDTH)
                self.output.append(f"{header_line}\n{separator}")
            return

        self.output.append(text)

    def _flush_blockquote(self):
        raw = "".join(self.blockquote_text).strip()
        # Clean up the text
        raw = re.sub(r"\s+", " ", raw)

        cite = self.blockquote_cite.strip()
        cite = re.sub(r"^—\s*", "", cite)

        self.output.append("\n\n")
        self.output.append(f"  << {raw} >>")
        if cite:
            self.output.append(f"\n  -- {cite}")
        self.output.append("\n")

    def _flush_table(self):
        self.output.append("\n\n")
        if not self.table_rows:
            return

        if self.table_headers:
            for row in self.table_rows:
                parts = []
                for i, cell in enumerate(row):
                    if i < len(self.table_headers):
                        parts.append(f"{self.table_headers[i]} : {cell}")
                    else:
                        parts.append(cell)
                self.output.append("\n".join(parts))
                self.output.append("\n\n")
        else:
            for row in self.table_rows:
                self.output.append(" | ".join(row))
                self.output.append("\n")

    def _flush_list_item(self):
        text = "".join(self.list_item_text).strip()
        indent = "  " * (self.list_depth - 1)
        if self.ordered_list and self.list_counters:
            bullet = f"{self.list_counters[-1]}."
        else:
            bullet = "-"
        self.output.append(f"\n{indent}{bullet} {text}")

    def get_text(self):
        return "".join(self.output)


def html_to_text(html: str) -> str:
    """Convert HTML body to clean plain text."""
    converter = HTMLToTextConverter()
    converter.feed(html)
    text = converter.get_text()

    # Clean up whitespace
    # Replace multiple spaces on same line
    text = re.sub(r"[^\S\n]+", " ", text)
    # Normalize line endings
    text = re.sub(r" *\n *", "\n", text)
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Remove leading blank lines
    text = text.strip()

    return text


def wrap_text(text: str) -> str:
    """Wrap text at ~80 chars, preserving structure."""
    lines = text.split("\n")
    wrapped = []

    for line in lines:
        stripped = line.strip()

        # Preserve blank lines
        if not stripped:
            wrapped.append("")
            continue

        # Don't wrap header separators
        if re.match(r"^[=\-]{3,}$", stripped):
            wrapped.append(stripped)
            continue

        # Don't wrap list items and blockquote attributions short enough
        if stripped.startswith(("-", "<<", ">>", "--")) and len(stripped) <= WRAP_WIDTH:
            wrapped.append(stripped)
            continue

        # Don't wrap table lines (header: value)
        if " : " in stripped and len(stripped) <= WRAP_WIDTH + 20:
            wrapped.append(stripped)
            continue

        # Preserve indentation for blockquotes
        indent_match = re.match(r"^(\s+)", line)
        indent = indent_match.group(1) if indent_match else ""

        if len(stripped) > WRAP_WIDTH:
            # Wrap long lines
            w = textwrap.fill(
                stripped,
                width=WRAP_WIDTH,
                initial_indent=indent,
                subsequent_indent=indent,
                break_long_words=False,
                break_on_hyphens=False,
            )
            wrapped.append(w)
        else:
            wrapped.append(line)

    return "\n".join(wrapped)


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (~200 words/min for French)."""
    words = len(text.split())
    return max(1, round(words / 200))


def format_article(slug: str, data: dict, category: str) -> str:
    """Format a single article as clean text for audio."""
    title = data["title"]
    description = data.get("description", "")
    html_body = data.get("htmlBody", "")

    # Convert body
    body_text = html_to_text(html_body)
    body_text = wrap_text(body_text)

    # Reading time
    reading_time = estimate_reading_time(body_text)

    # Build document
    cat_label = CATEGORY_LABELS.get(category, category.title())

    # Center the title
    title_upper = title.upper()
    pad = max(0, (WRAP_WIDTH - len(title_upper)) // 2)
    centered_title = " " * pad + title_upper

    separator = "=" * WRAP_WIDTH

    lines = []
    lines.append("")
    lines.append(separator)
    lines.append(centered_title)
    lines.append(separator)
    lines.append("")
    lines.append(f"  Categorie : {cat_label}")
    lines.append(f"  Temps de lecture : ~{reading_time} min")
    lines.append("")
    lines.append(separator[:40])
    lines.append("")

    if description:
        wrapped_desc = textwrap.fill(description, width=WRAP_WIDTH)
        lines.append(wrapped_desc)
        lines.append("")
        lines.append(separator[:40])
        lines.append("")

    lines.append(body_text)
    lines.append("")
    lines.append(separator)
    lines.append(f"  Fin de l'article : {title}")
    lines.append(separator)
    lines.append("")

    result = "\n".join(lines)

    # Final cleanup: no more than 2 consecutive blank lines
    result = re.sub(r"\n{4,}", "\n\n\n", result)

    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    errors = []

    for category, slug_list in SLUGS.items():
        for slug in slug_list:
            # Resolve actual filename
            file_slug = SLUG_TO_FILE.get(slug, slug)
            json_path = ARTICLES_DIR / f"{file_slug}.json"

            if not json_path.exists():
                errors.append(f"  MANQUANT : {slug} ({json_path.name})")
                continue

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            text = format_article(slug, data, category)

            out_path = OUTPUT_DIR / f"{slug}.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)

            word_count = len(text.split())
            print(f"  OK  {slug}.txt ({word_count} mots)")
            total += 1

    print(f"\n{'='*60}")
    print(f"  {total} fichiers exportes dans {OUTPUT_DIR.relative_to(BASE_DIR)}/")

    if errors:
        print(f"\n  {len(errors)} erreur(s) :")
        for e in errors:
            print(f"    {e}")
    else:
        print("  Aucune erreur.")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
