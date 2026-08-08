#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige la section 01 de « Cartes, routes, boussoles et le mystère antarctique ».

Le défaut
─────────
Le passage nommait al-Idrīsī, Ibn Ḥawqal et al-Bīrūnī comme « cartographes de
premier rang » du monde islamique médiéval, puis relevait comme « caractéristique
frappante » l'orientation Sud en haut de leurs cartes — dans une section qui
affirme par ailleurs que les cartes « révèlent la vision du monde de ceux qui les
ont conçues ».

Le texte ne disait pas littéralement que ces hommes tenaient la Terre pour plate.
Mais placé là, il le laissait entendre. Or :

  · al-Bīrūnī a MESURÉ le rayon terrestre par la dépression de l'horizon, une
    méthode qui n'a aucun sens sans courbure — l'angle est nul par construction
    sur une surface étendue. Son Taḥdīd nihāyāt al-amākin est bâti sur de la
    trigonométrie sphérique. Il est l'une des autorités que le camp sphériciste
    cite en premier ;
  · al-Idrīsī décrit la Terre comme ronde dans la Nuzhat al-mushtāq, a réalisé un
    planisphère d'argent pour Roger II, et organise sa carte selon les sept
    climats ptoléméens, qui sont un découpage en bandes de latitude ;
  · Ibn Ḥawqal relève de l'école de Balkhī, dont les cartes sont schématiques et
    sans projection. Sa position théorique propre sur la forme est mal
    documentée : nous ne la tranchons pas.

Et surtout : l'orientation Sud en haut est une convention de qibla — depuis
l'Irak, la Perse et l'Asie centrale, La Mecque est au sud — doublée d'un
précédent iranien. Elle ne porte aucune information sur la forme du monde. La
preuve tient dans l'exemple lui-même : la carte Sud en haut la plus célèbre est
celle d'un auteur qui écrit que la Terre est ronde.

La correction
─────────────
La section garde ce qui est vrai et fort — une carte encode des choix, la
précision des itinéraires est remarquable, l'orientation est signifiante — et
dit ce que ces cartographes pensaient réellement. Elle gagne au passage la
mention de la mesure d'al-Bīrūnī, qui est la seule expérience ancienne
géométriquement discriminante, et dont la faiblesse — la réfraction — est
exactement celle que notre protocole des trois mires contourne.

L'argument de fond de l'article — projection de Mercator, détours aériens,
verrouillage antarctique — n'est pas touché.
"""

import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "content", "articles",
                      "cartes-routes-boussoles-et-le-mystere-antarctique.json")

AVANT = """<p>Le monde islamique médiéval a produit des cartographes de premier rang : <strong>Al-Idrisi</strong> (1100–1165), <strong>Ibn Hawqal</strong> (Xᵉ siècle), <strong>Al-Biruni</strong> (973–1048). Une caractéristique frappante de leurs cartes : elles sont orientées avec le <strong>Sud en haut</strong>. Certaines sont centrées sur La Mecque, d'autres sur le monde islamique connu. Leurs routes commerciales et de pèlerinage sont d'une précision remarquable.</p>
<p>La <em>Tabula Rogeriana</em> d'Al-Idrisi (1154), réalisée pour le roi Roger II de Sicile, est considérée comme la carte la plus précise du monde médiéval. Orientée Sud en haut, elle représente l'ensemble de l'Eurasie et de l'Afrique connue avec une précision étonnante. Retournée à 180°, elle ressemble presque parfaitement aux cartes modernes.</p>"""

APRES = """<p>Le monde islamique médiéval a produit des cartographes de premier rang : <strong>al-Idrīsī</strong> (1100-1165), <strong>Ibn Ḥawqal</strong> (X<sup>e</sup> siècle), <strong>al-Bīrūnī</strong> (973-1048). Leurs itinéraires commerciaux et de pèlerinage sont d'une précision remarquable, et une caractéristique de leurs cartes saute aux yeux : elles sont orientées avec le <strong>Sud en haut</strong>. Certaines sont centrées sur La Mecque, d'autres sur le monde islamique connu.</p>

<h3 id="cartes-ce-que-ces-cartographes-pensaient">Ce que ces cartographes pensaient de la forme de la Terre</h3>

<p>Il faut le dire avant d'aller plus loin, parce que le rapprochement serait trompeur : <strong>al-Bīrūnī et al-Idrīsī tenaient la Terre pour sphérique</strong>, et le premier ne s'est pas contenté de l'admettre — il l'a mesurée.</p>

<p>Al-Bīrūnī a déterminé le rayon terrestre par la <strong>dépression de l'horizon</strong> relevée depuis un sommet, la forteresse de Nandana, dans le Pendjab. Cette méthode ne suppose pas seulement la courbure : elle n'a aucun sens sans elle. On mesure de combien l'horizon s'abaisse sous l'horizontale depuis une hauteur connue, et l'on en tire le rayon. Sur une surface étendue, cet angle est <strong>nul par construction</strong> et la mesure ne donne rien. Il a obtenu une valeur proche de celle admise aujourd'hui. Son <em>Taḥdīd nihāyāt al-amākin</em>, qui calcule les coordonnées des lieux et la direction de la qibla, est bâti d'un bout à l'autre sur de la trigonométrie sphérique.</p>

<p>Al-Idrīsī décrit la Terre comme ronde dans la <em>Nuzhat al-mushtāq</em>, le texte qui accompagne sa carte ; il a réalisé pour Roger II un planisphère d'argent, et il organise son ouvrage selon les sept <em>climats</em> ptoléméens, qui sont un découpage en bandes de latitude. Le cas d'Ibn Ḥawqal est différent et nous ne le tranchons pas : il relève de l'école de Balkhī, dont les cartes sont schématiques et sans projection, et sa position théorique propre sur la forme du monde est mal documentée.</p>

<p>Quant à l'orientation elle-même, elle est une <strong>convention de qibla</strong> : depuis l'Irak, la Perse et l'Asie centrale — les foyers de la géographie arabe — La Mecque est au sud, et l'on tourne la carte vers la direction de la prière. S'y ajoute un précédent iranien antérieur. Elle ne porte donc <strong>aucune information sur la forme du monde</strong>, et la preuve tient dans l'exemple lui-même : la carte Sud en haut la plus célèbre est celle d'un auteur qui écrit que la Terre est ronde. Le Nord en haut est une convention européenne, comme la section suivante le montre ; le Sud en haut en est une autre. Aucune des deux ne décrit une géométrie.</p>

<p>Pourquoi insister ? Parce que le raccourci inverse est celui que nous reprochons aux concordistes : <strong>enrôler une autorité pour une position qu'elle ne tenait pas</strong>. Al-Bīrūnī est même l'une des références que le camp sphériciste cite en premier. Un lecteur qui vérifie — et il doit vérifier — trouverait le procédé, et aurait raison de nous le reprocher.</p>

<div class="tei-enclair"><span class="tei-enclair-label">En clair</span><p>Mettre le Sud en haut, c'est comme afficher un plan de métro avec la sortie vers soi : c'est une question de commodité et d'orientation, pas de géométrie. Les cartographes arabes tournaient leurs cartes vers La Mecque parce qu'on prie dans cette direction. Cela ne dit rien de la forme de la Terre — et ceux qui ont dessiné les plus belles de ces cartes la tenaient pour ronde.</p></div>

<p>Reste que la mesure d'al-Bīrūnī mérite d'être regardée de près, parce qu'elle est la <strong>seule expérience ancienne géométriquement discriminante</strong>. Toutes les autres — l'ombre d'Ératosthène, la disparition des navires, la montée de l'Étoile polaire, la circumnavigation — sont compatibles avec deux géométries et ne tranchent donc pas. Celle-là tranche en principe. Sa faiblesse est ailleurs, et elle est sévère : l'angle mesuré vaut quelques minutes d'arc, et la <a href="/article/lhorizon-la-perspective-et-la-refraction">réfraction atmosphérique</a> le mord de plein fouet. Al-Bīrūnī posait la bonne question avec un rapport signal sur systématique défavorable. C'est précisément ce que notre <a href="/article/monter-l-experience-des-trois-mires">protocole des trois mires</a> cherche à corriger, en lisant un exposant plutôt qu'une amplitude.</p>

<h3 id="cartes-la-tabula-rogeriana">La Tabula Rogeriana</h3>

<p>La <em>Tabula Rogeriana</em> d'al-Idrīsī (1154), réalisée pour le roi Roger II de Sicile, est considérée comme la carte la plus précise du monde médiéval. Orientée Sud en haut, elle représente l'ensemble de l'Eurasie et de l'Afrique connue avec une précision étonnante. Retournée à 180°, elle ressemble presque parfaitement aux cartes modernes — ce qui est un compliment fait à son auteur, non un argument sur la forme du monde : coïncider avec une carte moderne, c'est coïncider avec une projection.</p>"""


def main():
    with open(CHEMIN, encoding="utf-8") as f:
        data = json.load(f)
    html = data["htmlBody"]

    if "Ce que ces cartographes pensaient" in html:
        print("  ✓ la correction est déjà en place")
        return 0
    if AVANT not in html:
        print("  ✗ le passage à corriger est introuvable")
        return 1

    html = html.replace(AVANT, APRES, 1)
    print("  ✓ passage corrigé")

    # Aucun encadré-clé n'est ajouté : l'article est de la catégorie
    # « observatory », dont le label imposé est « CE QUE MONTRENT LES DONNÉES »,
    # et le point établi ici est historique et philologique, pas métrologique.
    # Il est donc porté par la prose et par l'encadré « En clair ».

    data["htmlBody"] = html
    data["updated"] = "2026-08-06"
    with open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
