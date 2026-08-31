#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deuxième passe sur le dossier des trous noirs : les deux sections restantes.

La première passe a retiré les redites et fusionné les deux sections de théories
alternatives. Restaient les deux plus longues, celles qui portent la matière :
« Qu'est-ce qu'un trou noir » et « Les hypothèses cachées ». On n'y coupe pas de
substance — il n'y en a pas à couper. On change la façon dont elle est servie.

Le défaut commun aux deux : chaque sous-section commençait par un préambule et
finissait par son point. Le lecteur devait aller au bout pour savoir ce qu'on lui
disait. Elles ouvrent maintenant sur l'affirmation, et développent ensuite.

Trois défauts propres :

— L'effondrement était expliqué deux fois de suite par deux analogies
  différentes, l'éponge puis la boule de neige, à quatre lignes d'écart. Une
  seule suffit ; l'autre partait avec le point technique qu'elle enrobait, qui
  est conservé.

— Greiner et Logunov étaient présentés ici avec leur biographie, puis présentés
  de nouveau avec la même biographie dans la section des alternatives. Une seule
  présentation, à la première mention.

— La question qui décide n'était jamais posée frontalement. Elle l'est
  maintenant, en ouverture de la section : de ces quatre hypothèses, lesquelles
  sont des faits mesurés, et lesquelles sont des commodités de calcul dont on
  n'a jamais montré qu'elles décrivaient la nature ?
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(RACINE, "content", "articles", "les-trous-noirs-existent-ils.json")


def bloc(corps, motif, jusqua=None):
    """Un fragment existant, repris mot pour mot."""
    i = corps.find(motif)
    if i < 0:
        sys.exit("Fragment introuvable : %s" % motif[:50])
    j = corps.find(jusqua, i) if jusqua else len(corps)
    return corps[i:j]


def main():
    with open(CH, encoding="utf-8") as f:
        art = json.load(f)
    html = art["htmlBody"]
    avant = len(re.sub(r"<[^>]+>", " ", html).split())

    parts = re.split(r"(<h2[^>]*>.*?</h2>)", html, flags=re.S)
    idx = {}
    for i in range(1, len(parts) - 1, 2):
        m = re.search(r'id="([^"]+)"', parts[i])
        idx[m.group(1)] = i

    # ══ 02 — Qu'est-ce qu'un trou noir ══════════════════════════════════════
    c = parts[idx["tn-bases"] + 1]
    fig_courbure = bloc(c, '<div style="margin:24px auto', "<h3")
    enclair_recette = bloc(c, '<div class="tei-enclair">', "</div>") + "</div>"
    fig_singularite = c[c.find('<div style="margin', c.find("« au sens strict »")):]
    # tout ce qui suit le troisième h3 : figures, tableau, fait établi
    apres_h3 = c[c.find("</h3>", c.find("« au sens strict »")) + 5:]
    apres_h3 = apres_h3[apres_h3.find("<div style=\"margin"):] if "<div style=\"margin" in apres_h3 else apres_h3

    BASES = """
<p>Un trou noir, au sens où l'entendent les astrophysiciens, n'est pas «&nbsp;un objet très dense&nbsp;». C'est un objet qui possède <strong>trois caractéristiques</strong>, et les trois ne sont pas au même niveau de preuve. Cette section les pose&nbsp;; tout le reste du dossier porte sur les deux dernières.</p>

<h3>Une idée ancienne, un nom récent</h3>
<p>En 1783, le géologue anglais John Michell imagine une «&nbsp;étoile sombre&nbsp;» dont la vitesse de libération dépasserait celle de la lumière&nbsp;; Laplace développe la même idée en 1796. Ces intuitions reposaient sur la mécanique de Newton, où la lumière est faite de particules soumises à la gravité.</p>
<p>Avec la relativité générale d'Einstein, en 1915, le cadre change&nbsp;: la gravité n'est plus une force mais une courbure de l'espace-temps. Un trou noir y devient une région où la courbure est si extrême que même le chemin le plus court ne permet plus à la lumière de s'échapper.</p>
%(fig_courbure)s

<h3>Le rayon de Schwarzschild&nbsp;: une taille critique, pas un objet</h3>
<p>En 1916, quelques semaines après la publication des équations d'Einstein, Karl Schwarzschild — alors sur le front russe — en trouve la première solution exacte pour un objet sphérique sans rotation. Elle prédit un <strong>rayon critique</strong>&nbsp;: comprimez n'importe quelle masse en dessous, et rien, pas même la lumière, n'en ressort. Pour le Soleil, ce rayon vaut environ 3&nbsp;kilomètres&nbsp;; pour la Terre, environ 9&nbsp;millimètres.</p>
<p>C'est ici qu'il faut être précis, parce que tout le débat en découle&nbsp;: <strong>l'existence d'une solution mathématique ne dit pas que la nature produit l'objet correspondant.</strong> Les équations d'Einstein admettent des solutions qui décrivent des situations physiquement inaccessibles, ou valables dans des conditions idéales que rien ne réalise.</p>
%(enclair_recette)s

<h3>Les trois caractéristiques, et leur statut</h3>
<p>Eric Lerner — physicien des plasmas américain, fondateur de Lawrenceville Plasma Physics et auteur de travaux critiques sur la cosmologie standard — les résume ainsi&nbsp;: une <strong>concentration extrême de matière</strong>&nbsp;; un <strong>horizon des événements</strong>, frontière au-delà de laquelle aucune information ne revient&nbsp;; une <strong>singularité centrale</strong>, point sans dimensions où la densité deviendrait infinie.</p>
<p>La première est observée. Les deux autres ne l'ont jamais été, et l'une des deux ne peut pas l'être par construction. C'est tout l'objet de ce dossier.</p>
%(apres_h3)s""" % {
        "fig_courbure": fig_courbure.rstrip(),
        "enclair_recette": enclair_recette.rstrip(),
        "apres_h3": apres_h3.rstrip(),
    }
    parts[idx["tn-bases"] + 1] = BASES

    # ══ 04 — Les hypothèses cachées ═════════════════════════════════════════
    c = parts[idx["tn-hypotheses"] + 1]
    hl_nue = bloc(c, '<div class="tei-highlight"><p>Une singularité nue')
    hl_nue = hl_nue[:hl_nue.find("</div>") + 6]
    hl_retro = bloc(c, '<div class="tei-highlight"><p>Si cette perte')
    hl_retro = hl_retro[:hl_retro.find("</div>") + 6]
    fait = c[c.find('<div class="tei-fait'):]

    HYPOTHESES = """
<p>Le trou noir «&nbsp;au sens strict&nbsp;» ne sort pas des observations&nbsp;: il sort de calculs qui reposent sur quatre hypothèses. La question qui décide n'est donc pas «&nbsp;les trous noirs existent-ils&nbsp;?&nbsp;» mais celle-ci&nbsp;: <strong>ces quatre hypothèses sont-elles des faits mesurés, ou des commodités de calcul dont personne n'a montré qu'elles décrivaient la nature&nbsp;?</strong> Les voici, une par une.</p>

<h3>Première hypothèse&nbsp;: la symétrie parfaite</h3>
<p>Les solutions classiques — Schwarzschild pour un objet sans rotation, Kerr pour un objet en rotation — supposent une matière distribuée de façon exactement sphérique ou axiale, sans la moindre irrégularité. <strong>Cette symétrie n'existe nulle part dans la nature</strong>&nbsp;: les étoiles réelles tournent, portent des champs magnétiques, des irrégularités de densité, et interagissent avec leur environnement.</p>
<p>Wolfgang Kundt, professeur d'astrophysique à l'Université de Bonn, souligne dans «&nbsp;Astrophysics without Black Holes&nbsp;» (2013) que les théorèmes de singularité de Penrose et Hawking reposent sur des hypothèses très restrictives. Selon les calculs analytiques qu'il cite, l'effondrement complet conduit généralement non pas à des trous noirs mais à des <strong>singularités nues</strong> — le cas du trou noir correspondant à un sous-ensemble de configurations d'une symétrie extrême, de mesure nulle parmi toutes les configurations possibles.</p>
%(hl_nue)s
<p>Autrement dit&nbsp;: même en accordant que des singularités existent, rien n'établit qu'elles soient cachées derrière un horizon.</p>

<h3>Deuxième hypothèse&nbsp;: la pression nulle</h3>
<p>Le modèle d'Oppenheimer et Snyder de 1939, fondement de la théorie, suppose que la pression à l'intérieur de l'étoile en effondrement est <strong>nulle</strong>. Les auteurs ne s'en cachent pas&nbsp;: ils écrivent n'avoir «&nbsp;pas pu intégrer les équations sauf dans le cas où la pression est posée égale à zéro&nbsp;». C'est une commodité mathématique, et elle est physiquement fausse — une étoile réelle a une pression interne qui s'oppose à l'effondrement.</p>
<p>La réponse conventionnelle est qu'au-delà d'une masse critique, environ deux à trois masses solaires pour une étoile à neutrons, aucune forme connue de pression n'arrête l'effondrement. La relativité générale pseudo-complexe de Walter Greiner en propose une autre&nbsp;: des effets quantiques absents du calcul classique produiraient une pression répulsive supplémentaire, suffisante pour l'arrêter.</p>

<h3>Troisième hypothèse&nbsp;: l'effondrement silencieux</h3>
<p>Les calculs classiques supposent que l'étoile s'effondre <strong>sans perdre de masse par rayonnement</strong>. Or Hawking a montré en 1974 que les trous noirs doivent émettre un rayonnement thermique dû à des effets quantiques près de l'horizon — un résultat que la physique théorique tient pour bien établi. S'il est réel, il doit rétroagir sur l'effondrement lui-même.</p>
<p>C'est ce qu'examine Laura Mersini-Houghton dans «&nbsp;Backreaction of Hawking Radiation on a Gravitationally Collapsing Star&nbsp;» (2014). Sa conclusion&nbsp;: en tenant compte de cette rétroaction, l'étoile <strong>rebondit à un rayon fini</strong>, avant que l'horizon et la singularité aient eu le temps de se former.</p>
<div class="tei-enclair">
<span class="tei-enclair-label">En clair</span>
<p>Imaginez une éponge gorgée d'eau qu'on presse&nbsp;: plus on serre, plus elle rejette de l'eau, si bien qu'on n'arrive jamais à la tasser complètement. L'étoile «&nbsp;rejette&nbsp;» de l'énergie sous forme de rayonnement pendant qu'elle se comprime, et cette fuite l'empêche d'atteindre l'état de trou noir. Elle s'arrête juste avant.</p>
</div>
%(hl_retro)s

<h3>Quatrième hypothèse&nbsp;: que la théorie vaille encore là-bas</h3>
<p>La relativité générale a été vérifiée dans notre système solaire&nbsp;: déviation de la lumière par le Soleil, avance du périhélie de Mercure, décalage gravitationnel des fréquences, retard des signaux radio. Tous ces tests portent sur des régimes de <strong>gravité modérée</strong>.</p>
<p>Un trou noir est un régime de gravité extrême, sans commune mesure avec ce qui a été testé. Extrapoler les équations jusqu'à une singularité, c'est supposer que la théorie reste exacte dans des conditions des milliards de milliards de fois plus intenses que celles où on l'a vérifiée. Ce n'est pas une certitude expérimentale&nbsp;; c'est une extrapolation, et il faut l'appeler par son nom.</p>
<p>Anatoly Logunov et ses collaborateurs vont plus loin dans leur article de 1988 (<em>Uspekhi Fizicheskikh Nauk</em>)&nbsp;: la relativité générale contiendrait des ambiguïtés mathématiques qui rendent ses prédictions non uniques dans certaines configurations. Sa théorie alternative est examinée en section&nbsp;05.</p>
%(fait)s""" % {"hl_nue": hl_nue, "hl_retro": hl_retro, "fait": fait.rstrip()}
    parts[idx["tn-hypotheses"] + 1] = HYPOTHESES

    html = parts[0] + "".join(parts[1:])

    # La biographie de Greiner et de Logunov n'a plus à être répétée en 05.
    for double in [
        " — l'un des physiciens théoriciens les plus influents du XX<sup>e</sup> siècle, "
        "père fondateur de la physique des ions lourds —",
    ]:
        html = html.replace(double, "")

    art["htmlBody"] = html
    art["updated"] = "2026-08-31"
    with open(CH, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")

    apres = len(re.sub(r"<[^>]+>", " ", html).split())
    print("%d mots → %d (−%d %%)" % (avant, apres, round(100 * (avant - apres) / avant)))


if __name__ == "__main__":
    main()
