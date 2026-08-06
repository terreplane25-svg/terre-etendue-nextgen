#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse structurelle du HTML des articles — bibliothèque commune, sans
dépendance externe (html.parser de la bibliothèque standard).

Pourquoi ce module existe
─────────────────────────
Le premier contrôle « texte hors conteneur » signalait 249 fragments. En les
examinant un à un, la plupart se sont révélés légitimes : la migration
Elementor a laissé des cartes et des grilles bâties sur des <div> portant leur
propre style typographique — <div style="font-size:22px;font-weight:900">1728
</div>. Ce texte est le contenu de son élément, il est stylé, et l'enfermer
dans un <p> ajouterait des marges qui casseraient la grille.

Le vrai défaut est différent, et plus étroit : du texte nu posé **entre** des
frères de niveau bloc. C'est là que le texte échappe à toute règle, parce
qu'aucun élément ne le porte. La règle retenue est donc :

    un fragment de texte est fautif si, et seulement si, son élément parent
    contient au moins un enfant de niveau bloc.

Autrement dit : un élément dont le contenu est entièrement du texte et de
l'inline est un conteneur de texte, quel que soit son nom. Un élément qui mêle
des blocs et du texte nu a un problème.

Le module travaille par relevé de positions et non par réécriture d'arbre : il
rend les décalages exacts dans la chaîne d'origine, ce qui permet de corriger
par chirurgie sur le texte et de garantir que tout le reste du document —
guillemets d'attributs, entités, espaces — reste identique à l'octet.
"""

from html.parser import HTMLParser

BLOCS = {
    "p", "div", "ul", "ol", "li", "dl", "dt", "dd", "table", "thead", "tbody",
    "tfoot", "tr", "td", "th", "caption", "blockquote", "footer", "header",
    "section", "article", "aside", "nav", "figure", "figcaption", "main",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "pre", "form", "fieldset",
    "details", "summary", "video", "audio", "iframe",
}

# Sous-arbres opaques : leur contenu ne relève pas des règles du corps de texte.
OPAQUES = {"svg", "script", "style", "math"}

VIDES = {"br", "hr", "img", "input", "meta", "link", "source", "col", "area",
         "base", "embed", "param", "track", "wbr"}


class _Analyseur(HTMLParser):
    """Repère les suites de texte et d'inline posées entre des frères de bloc.

    Chaque élément tient une liste d'« enfants » réduite à ce qui nous
    intéresse : ('bloc', début, fin) ou ('inline', début, fin) ou
    ('texte', début, fin, vide?).
    """

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        # Décalage du début de chaque ligne, pour convertir (ligne, colonne).
        self.debuts = [0]
        for ligne in source.split("\n")[:-1]:
            self.debuts.append(self.debuts[-1] + len(ligne) + 1)
        self.racine = {"nom": "#racine", "enfants": []}
        self.pile = [self.racine]
        self.profondeur_opaque = 0

    # ── utilitaires de position ──
    def _pos(self):
        ligne, col = self.getpos()
        return self.debuts[ligne - 1] + col

    def _fin_balise(self):
        """Fin de la balise courante dans la source (le texte brut est fiable)."""
        debut = self._pos()
        fin = self.source.find(">", debut)
        return (fin + 1) if fin != -1 else debut + len(self.get_starttag_text() or "")

    def _ajouter(self, genre, debut, fin):
        self.pile[-1]["enfants"].append((genre, debut, fin))

    # ── événements ──
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        debut, fin = self._pos(), self._fin_balise()
        if self.profondeur_opaque:
            return
        if tag in OPAQUES:
            self.profondeur_opaque = 1
            self._ajouter("bloc", debut, fin)
            self.pile.append({"nom": tag, "enfants": [], "debut": debut})
            return
        if tag in VIDES:
            self._ajouter("bloc" if tag in BLOCS else "inline", debut, fin)
            return
        self._ajouter("bloc" if tag in BLOCS else "inline", debut, fin)
        self.pile.append({"nom": tag, "enfants": [], "debut": debut, "fin_ouvrante": fin})

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if self.profondeur_opaque:
            return
        self._ajouter("bloc" if tag in BLOCS else "inline", self._pos(), self._fin_balise())

    def handle_endtag(self, tag):
        tag = tag.lower()
        debut, fin = self._pos(), self._fin_balise()
        if tag in OPAQUES:
            self.profondeur_opaque = 0
            if len(self.pile) > 1 and self.pile[-1]["nom"] == tag:
                self.pile.pop()
            return
        if self.profondeur_opaque:
            return
        # Refermer jusqu'à l'élément correspondant, s'il est ouvert.
        for i in range(len(self.pile) - 1, 0, -1):
            if self.pile[i]["nom"] == tag:
                for _ in range(len(self.pile) - i):
                    ferme = self.pile.pop()
                ferme["fin_fermante"] = fin
                self.pile[-1].setdefault("fermes", []).append(ferme)
                # La position de la balise fermante borne le contenu du parent.
                self.pile[-1]["enfants"].append(("#fin", debut, fin))
                self.pile[-1]["enfants"].pop()
                break

    def handle_data(self, data):
        if self.profondeur_opaque:
            return
        debut = self._pos()
        self._ajouter("texte", debut, debut + len(data))

    def handle_entityref(self, name):
        if self.profondeur_opaque:
            return
        debut = self._pos()
        self._ajouter("texte", debut, debut + len(name) + 2)

    def handle_charref(self, name):
        if self.profondeur_opaque:
            return
        debut = self._pos()
        self._ajouter("texte", debut, debut + len(name) + 3)

    def handle_comment(self, data):
        pass


def runs_fautifs(source):
    """Rend les intervalles (début, fin) des suites texte/inline qui cohabitent
    avec des frères de niveau bloc, et sont donc portées par aucun élément."""
    a = _Analyseur(source)
    a.feed(source)
    a.close()

    resultats = []

    def visiter(el):
        enfants = el["enfants"]
        a_un_bloc = any(g == "bloc" for g, *_ in enfants)
        if a_un_bloc:
            courant = []
            for genre, debut, fin in enfants + [("bloc", len(source), len(source))]:
                if genre == "bloc":
                    if courant and any(
                            source[d:f].strip() for g, d, f in courant if g == "texte"):
                        resultats.append((courant[0][1], courant[-1][2]))
                    courant = []
                else:
                    courant.append((genre, debut, fin))
        for ferme in el.get("fermes", []):
            visiter(ferme)

    visiter(a.racine)
    # Les runs collectés peuvent inclure des espaces de bordure : on resserre.
    propres = []
    for debut, fin in resultats:
        d, f = debut, fin
        while d < f and source[d].isspace():
            d += 1
        while f > d and source[f - 1].isspace():
            f -= 1
        if f > d:
            propres.append((d, f))
    propres.sort()
    return propres


def texte_nu(source):
    """Version texte de la source, pour comparer avant/après une correction."""
    import re
    sans = re.sub(r"<[^>]+>", " ", source)
    return " ".join(sans.split())
