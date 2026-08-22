#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report des verdicts vérifiés dans l'inventaire des faits établis.

content/corrections/faits-etablis.md relève les 240 encadrés-clés du site, avec
une colonne Verdict laissée vide. Les verdicts se remplissent au fil de
l'examen, et ce script y reporte ceux qui sont adossés à un contrôle
reproductible — c'est-à-dire ceux que produit verifier-encadres-empiriques.py.

Pourquoi un script plutôt qu'une saisie à la main
─────────────────────────────────────────────────
Trois des cinq premières annotations manuelles sont devenues fausses le jour où
la fonction cachee() a été corrigée. Elles disaient RESSERRER là où le calcul
refait dit RETIRER, et employaient un vocabulaire — « indécidable » — qu'on a
depuis abandonné parce qu'il confondait notre ignorance avec l'impossibilité de
savoir. Une annotation saisie à la main ne suit pas les corrections du calcul
qui la fonde ; une annotation reportée par script, si.

L'appariement se fait par (slug d'article, numéro d'encadré), les deux étant
présents de part et d'autre. Le script refuse d'écrire s'il ne retrouve pas ses
cibles, plutôt que d'annoter la mauvaise ligne.

    python3 scripts/annoter-faits-etablis.py            # rapport seul
    python3 scripts/annoter-faits-etablis.py --ecrire   # report effectif
"""

import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTAIRE = os.path.join(RACINE, "content", "corrections", "faits-etablis.md")

# Verdicts adossés à scripts/verifier-encadres-empiriques.py. Le numéro renvoie
# à l'ordre des contrôles dans ce script ; la note dit ce qui est vérifié, en une
# phrase, de façon que la ligne du tableau se lise seule.
#
# Les deux fichiers emploient deux vocabulaires distincts, et c'est voulu : le
# vérificateur DIAGNOSTIQUE (faux, mal posé, hors sujet, à compléter), l'inventaire
# PRESCRIT (garder, resserrer, déclasser, retirer, à compléter). La correspondance
# retenue est :
#     FAUX        -> RETIRER      l'énoncé ne tient pas
#     MAL POSÉ    -> RETIRER      il attaque une prédiction qui n'est pas faite
#     HORS SUJET  -> DÉCLASSER    peut être vrai sans rien établir de la thèse
#     À COMPLÉTER -> À COMPLÉTER  seul verdict qui traverse les deux vocabulaires
# Le mot de diagnostic est conservé dans la note : la prescription seule ferait
# perdre la raison qui la fonde.
VERDICTS = {
    ("la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 3): (
        "RETIRER",
        "contrôle n°1. Faux. La « limite théorique de ≈ 90° » n'existe pas : une étoile "
        "de déclinaison δ est visible depuis toute latitude φ telle que |φ−δ| < 90°, "
        "soit 130,7° d'amplitude pour Alkaid et 180,0° pour une constellation "
        "équatoriale. Les 120° observés sont à l'intérieur de la prédiction du "
        "modèle que l'encadré présente comme réfuté."),
    ("la-perspective-pourquoi-les-objets-disparaissent", 3): (
        "RETIRER",
        "contrôle n°2. Les 19 100 m de d²/2R sont justes, mais « en déduire les "
        "altitudes » est la règle de pouce « 8 pouces par mille au carré moins la "
        "hauteur d'œil », fausse dès que la cible dépasse l'horizon. Sur la ligne "
        "Karagöl → Caucase elle fabrique 9 180 m de montagne cachée inexistante. "
        "Correctement calculée, l'observation est prédite par le modèle sphérique "
        "à réfraction ordinaire, et ne départage donc pas les deux modèles."),
    ("la-perspective-pourquoi-les-objets-disparaissent", 2): (
        "À COMPLÉTER",
        "contrôle n°3. La formule employée suppose un œil au ras de l'eau, ce qui "
        "n'est jamais le cas. La hauteur d'observation, absente de l'énoncé, est "
        "le paramètre qui décide — et l'article « Par rapport à quoi mesure-t-on "
        "une altitude ? » l'écrit lui-même à son encadré n°4."),
    ("lhorizon-la-perspective-et-la-refraction", 1): (
        "RETIRER",
        "contrôle n°4. Mal posé : les 20 m sont la chute de la *surface* sous la "
        "tangente, pas la descente apparente de l'horizon, qui est un ANGLE et vaut "
        "2,5′ à 1,7 m de hauteur d'œil. L'encadré compare des mètres à un angle."),
    ("le-theodolite-celeste", 1): (
        "RETIRER",
        "contrôle n°5. Mal posé : les 1 340 m relèvent d'une formule de visée "
        "terrestre appliquée à une étoile, dont la distance rend la parallaxe nulle. "
        "La grandeur calculée ne correspond à rien dans l'observation décrite."),
    ("cartes-routes-boussoles-et-le-mystere-antarctique", 4): (
        "RETIRER",
        "contrôle n°6. Mal posé : les 60 000 km sont un chemin parcouru, avec "
        "détours et retours, comparés à un périmètre. Deux grandeurs qui ne se "
        "comparent pas."),
    ("les-marees-contre-lheliocentrisme", 1): (
        "RESSERRER",
        "contrôle n°7. Le ratio est arithmétiquement juste — nous trouvons 11 741 "
        "contre 11 764 annoncés — mais l'inférence ne l'est pas : la marée dépend "
        "du GRADIENT du champ, pas de son intensité. Garder le chiffre, retirer la "
        "conclusion."),
    ("vols-avion-et-courbure-terrestre", 3): (
        "RETIRER",
        "contrôle n°8. Les encadrés 3, 4 et 5 sont réfutés par l'encadré n°8 du "
        "même article, qui concède ce qu'ils nient. Une contradiction interne ne "
        "se répare pas en resserrant : il faut choisir lequel des deux tient."),
    ("la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 4): (
        "GARDER",
        "contrôle n°9. Les 4°44′ de Nansen sont exacts et bien sourcés. Mais leur "
        "conséquence engage le site : si une réfraction de cet ordre « invalide "
        "toute observation d'horizon », elle invalide aussi Port-Saïd, le record de "
        "493 km, les navires au zoom, la planche de niveau et les douze sommets du "
        "théodolite. À garder, avec cette conséquence écrite."),
    ("la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas", 1): (
        "DÉCLASSER",
        "contrôle n°10. Hors sujet : le refroidissement sous la lumière lunaire "
        "porte sur la Lune, pas sur la figure de la Terre. Peut être vrai sans rien "
        "établir de ce que l'encadré prétend établir."),
    ("cartes-routes-boussoles-et-le-mystere-antarctique", 2): (
        "À COMPLÉTER",
        "contrôle n°11. Contredit par le corps du même article, qui concède vents, "
        "jet stream, demande commerciale et accords bilatéraux. Il manque le "
        "critère posé d'avance : quel écart, sur quelle route, ne serait explicable "
        "QUE par la géométrie."),
    ("la-perspective-lineaire", 2): (
        "RESSERRER",
        "contrôle n°12. Les 2 m à 6,8 km font bien 1,01′ : l'arithmétique est "
        "juste. Mais la conclusion « donc la disparition est optique et non "
        "géométrique » ne suit pas — à cette distance, un œil à 1,70 m a son "
        "horizon à 5,0 km et la cible est déjà masquée. Les deux causes agissent ; "
        "l'encadré en écarte une sans l'avoir calculée."),
    ("loeil-humain-la-machine-a-voir-qui-faconne-notre-realite", 2): (
        "RESSERRER",
        "contrôle n°13. La portée stéréoscopique vaut b/σ : 223 m pour une acuité "
        "ordinaire, 447 m pour une bonne, 670 m pour une excellente. Les 200 m "
        "annoncés sont la borne basse d'une fourchette de un à trois, donnée pour "
        "une limite, et le mot « totalement » ne convient pas."),
    ("le-pole-sud-nexiste-pas", 1): (
        "RESSERRER",
        "contrôle n°14. Les 2 900 km sont justes — le calcul donne 2 869 km. Mais "
        "géographique, magnétique, géomagnétique et d'inaccessibilité sont quatre "
        "DÉFINITIONS distinctes, que le modèle sphérique prédit non confondues. "
        "Leur écart n'établit rien : il faudrait deux mesures divergentes de la "
        "MÊME définition."),
    ("experiences-sous-pression-reduite", 2): (
        "GARDER",
        "contrôle n°15. L'équation d'Antoine donne 23,3 mbar à 20 °C et 69,8 mbar "
        "à 39 °C : les deux valeurs annoncées sont justes à moins d'un millibar. "
        "L'énoncé établit exactement ce qu'il prétend établir."),
    ("lhorizon-la-perspective-et-la-refraction", 4): (
        "RETIRER",
        "contrôle n°16. Les deux cas réunis ne disent pas la même chose. CHICAGO : "
        "aucun écart à combler — même sans réfraction, 240 m sont masqués sur 527 m "
        "et les deux tiers supérieurs restent visibles, ce qu'on photographie "
        "précisément ; les « 130 m manquants » viennent de la règle de pouce. "
        "ANVERS : le cas est réel, 3 789 m masqués en réfraction standard, et sa "
        "visibilité exige un conduit atmosphérique — que le calculateur du site "
        "associe lui-même à k = 0,38. Un cas sans anomalie et un cas de "
        "super-réfraction documentée, réunis sous un même énoncé."),
    ("la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 2): (
        "GARDER",
        "contrôle n°17. La mesure est exacte et c'est l'observable du protocole "
        "du diamètre solaire. Ce qu'elle écarte est une CLASSE de modèles : ceux "
        "qui posent un corps compact à hauteur finie, dont la loi en sin α "
        "donnerait 16,0′ à 30° de hauteur et 8,3′ à 15° au lieu des 32′ observés. "
        "Elle ne contraint pas les modèles où le disque visible n'est pas l'astre "
        "— projection, image formée par une couche atmosphérique — dont la taille "
        "est fixée par l'optique de formation et non par une distance. "
        "Correction apportée après remarque : la première rédaction concluait "
        "« réfute le Soleil local et confirme le Soleil lointain », ce qui "
        "outrepasse la portée de la mesure et contredit la section 02 de notre "
        "propre protocole solaire. Le fait reste à garder, avec sa portée exacte."),
    ("kings-dethroned-leffondrement-de-la-triangulation-stellaire", 1): (
        "RETIRER",
        "contrôle n°18. La taille de l'astre n'intervient nulle part : seule sa "
        "distance compte. Deux observateurs séparés d'une base b voient un astre "
        "lointain à la hauteur 90° − b/2R chacun — soit 40,5° pour une base de "
        "11 000 km. Les transits de Vénus s'observent précisément depuis de telles "
        "bases, le Soleil restant plusieurs heures au-dessus des deux horizons."),
    ("le-mythe-deratosthene", 5): (
        "RESSERRER",
        "contrôle n°19. Le cœur est juste : avec DEUX sites, la méthode des gnomons "
        "ne discrimine pas — un Soleil proche reproduit le résultat. Mais « la "
        "méthode est intrinsèquement non discriminante » est trop large : avec trois "
        "sites ou plus, la hauteur de Soleil impliquée par chaque paire doit être la "
        "même sur un plan, et elle ne l'est pas. C'est le nombre de sites qui décide, "
        "pas la méthode."),
    ("le-mythe-deratosthene", 6): (
        "GARDER",
        "contrôle n°20. L'arithmétique est exacte : 252 000 stades × 157,5 m donnent "
        "39 690 km, soit −0,8 % du réel ; × 185 m ils donnent 46 620 km, soit "
        "+16,5 %. Le point méthodologique — la « précision à 1 % » dépend d'un choix "
        "de stade fait en 1949 — est fondé et se vérifie au calcul."),
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 3): (
        "GARDER",
        "contrôle n°21. La formule barométrique standard entre 340 m et 1 465 m donne "
        "123,9 hPa, soit exactement les 124 hPa annoncés, et 92,9 mmHg contre les "
        "93 mm écrits. L'accord de 9 % avec les 84,6 mm historiques est correctement "
        "rapporté."),
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 4): (
        "RESSERRER",
        "contrôle n°22. Les trois premières valeurs se confirment au mètre près : "
        "5,0 km de portée depuis 1,70 m, 616 m masqués à 100 km, 4 199 m à 253 km. "
        "Les coefficients du Canigou ne se reproduisent pas exactement — 0,46 et "
        "0,21 contre 0,42 et 0,15 — mais le vrai défaut est ailleurs : ils sont "
        "calculés depuis 1,70 m et 160 m, hauteurs que personne n'emploie. Les "
        "photographies existantes du Canigou depuis la Provence sont prises de la "
        "Sainte-Victoire, 1 011 m, et du Garlaban, 714 m. Depuis ces sites, le "
        "coefficient critique est NÉGATIF — −0,187 et −0,146 — c'est-à-dire que le "
        "sommet serait visible même sans aucune réfraction. Comparer à une hauteur "
        "d'œil fictive fabrique une difficulté qui n'existe pas. Voir le contrôle "
        "n°36."),
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 6): (
        "GARDER",
        "contrôle n°23. Les valeurs SRTM sont conformes aux spécifications de la "
        "mission : onze jours, 60° N à 56° S, 16 m d'exactitude absolue et 10 m "
        "relative. Rien à resserrer."),
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 7): (
        "GARDER",
        "contrôle n°24. L'amplitude du géoïde, de −106 m à +85 m par rapport à "
        "l'ellipsoïde, est la valeur admise. L'énoncé est exact et son point — le "
        "zéro des altitudes est une surface physique, pas une forme géométrique — "
        "est celui qui compte."),
    ("la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre", 1): (
        "RETIRER",
        "contrôle n°25. Deux affirmations sont soudées, et la seconde ne tient pas. "
        "Voir Soleil et Lune éclipsée ensemble demande de « dépasser 180° », et le "
        "budget disponible vaut 2,61° : réfraction du Soleil 0,57°, réfraction de la "
        "Lune 0,57°, demi-diamètres 0,27° et 0,25°, parallaxe lunaire 0,95°. "
        "L'encadré ne compte que 0,5° et conclut à l'insuffisance — il oublie la "
        "seconde réfraction, les deux demi-diamètres et surtout la parallaxe, qui "
        "vaut à elle seule le double de ce qu'il retient."),
    ("la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas", 2): (
        "RETIRER",
        "contrôle n°26. Même défaut que le précédent : 2,61° sont disponibles contre "
        "les 0,5° comptés. Les 4°44′ de Nansen, invoqués en renfort, ne sont pas "
        "nécessaires ici — et les convoquer engage le site sur cinq de ses propres "
        "encadrés, comme le note le contrôle n°9."),
    ("la-perspective-atmospherique", 2): (
        "RESSERRER",
        "contrôle n°27. La plage de portées est réelle. Mais « donc la limite est "
        "atmosphérique et non géométrique » ne suit pas : les deux limites existent "
        "et c'est la plus courte qui s'applique. Même défaut logique qu'au contrôle "
        "n°12 — écarter une cause sans l'avoir calculée."),
    ("le-theodolite-celeste", 3): (
        "À COMPLÉTER",
        "contrôle n°28. Le jeu de données de l'article est nécessaire pour refaire "
        "le calcul. Une indication toutefois : une somme d'angles supérieure à 180° "
        "est impossible en trigonométrie PLANE et parfaitement normale en "
        "trigonométrie SPHÉRIQUE, où l'excès sphérique est proportionnel à l'aire du "
        "triangle. Un « triangle mathématiquement impossible » signale donc "
        "d'ordinaire qu'on a appliqué la trigonométrie plane à une base courbe."),
    ("lespace-une-frontiere-infranchissable", 1): (
        "RETIRER",
        "contrôle n°29. Le taux d'érosion est du bon ordre, mais la conclusion est "
        "inversée. La densité d'oxygène atomique DÉCROÎT de cinq ordres de grandeur "
        "entre 200 et 800 km : 3×10⁹ cm⁻³ à 200 km, 4×10⁷ à 400 km, 6×10⁴ à 800 km. "
        "L'érosion par l'oxygène atomique est un problème d'orbite basse, et il "
        "s'atténue en montant. « Les conditions empirent avec l'altitude » dit le "
        "contraire du fait."),
    ("lhorizon-la-perspective-et-la-refraction", 3): (
        "RESSERRER",
        "contrôle n°30. Le fait est exact — un fisheye 170° courbe l'horizon bien "
        "au-delà du réel. Mais « la courbure provient de l'objectif, pas de la "
        "surface » est trop fort : à 39 040 m la dépression vaut 6,33° et la flèche "
        "réelle de l'arc d'horizon atteint 0,22° sur 30° de champ, 0,66° sur 50°, "
        "1,40° sur 70°. Elle existe ; elle est seulement trop faible pour être vue "
        "sur un objectif standard."),
    ("vols-avion-et-courbure-terrestre", 8): (
        "GARDER",
        "contrôle n°31. Les 0,0098 m/s² sont exacts, et la conclusion — les "
        "enregistreurs ne permettent ni de constater ni d'écarter cette valeur — est "
        "la bonne. C'est aussi l'encadré qui réfute les n°3, 4 et 5 du même article : "
        "à garder, et à faire prévaloir sur eux."),
    ("la-pression-atmospherique-un-ocean-d-air-invisible", 1): (
        "GARDER",
        "contrôle n°32. Une canette de 66 mm de diamètre et 115 mm de haut offre "
        "0,0307 m², soit 3 109 N sous 1 013 hPa — 317 kgf. Les « environ 300 kg » "
        "annoncés sont justes."),
    ("leau-ne-ment-pas", 1): (
        "RESSERRER",
        "contrôle n°33. Les « plus de 7 mètres » viennent de d²/2R, qui vaut 7,8 m "
        "mais suppose un œil au ras de l'eau visant une cible au ras de l'eau. Avec "
        "l'œil à 0,20 m de Rowbotham, la formule exacte donne 5,5 m sans réfraction "
        "et 4,7 m à réfraction moyenne. L'observation reste discutable, mais le "
        "chiffre opposé est surévalué de 60 %."),
    ("leau-ne-ment-pas", 2): (
        "RETIRER",
        "contrôle n°34. Les 283 m sont d²/2R et non la hauteur masquée : depuis 1,70 m "
        "elle vaut 206,6 m à réfraction moyenne. Sur une silhouette de 527 m, les "
        "deux tiers supérieurs restent visibles — ce qu'on photographie précisément. "
        "Il n'y a aucune incompatibilité à expliquer. Même défaut que le contrôle "
        "n°16, sur le même cas."),
    ("pression-lumiere-halos-rayons-et-ondes", 1): (
        "RESSERRER",
        "contrôle n°35. Les 1 013 hPa sont exacts et les deux démonstrations valides. "
        "Mais la dernière proposition — « sa transition vers un prétendu vide spatial "
        "reste un problème physique non résolu » — est une affirmation distincte, non "
        "établie par la mesure qui précède. Garder la mesure, séparer la thèse."),
    ("cartes-routes-boussoles-et-le-mystere-antarctique", 1): (
        "À COMPLÉTER",
        "contrôle n°36. Le Canigou depuis la Provence — 277 km depuis la "
        "Sainte-Victoire — n'est pas une anomalie : le coefficient critique y vaut "
        "−0,187, le sommet serait visible même sans réfraction. Mais l'observation "
        "devient un TEST si l'on mesure la hauteur apparente. Le modèle sphérique "
        "prédit 1 647 m masqués, donc 1 137 m émergés, soit 14,1′ — 0,46 diamètre "
        "lunaire. Un Canigou visible en entier depuis son pied à 500 m ferait "
        "2 284 m, soit 28,3′ — 0,91 diamètre lunaire. Facteur deux, mesurable en "
        "pixels sur les clichés existants. À trancher par cette mesure."),
    ("200-ans-de-resultats-nuls-darago-a-einstein", 8): (
        "RESSERRER",
        "contrôle n°38. Le principe est sain : une hypothèse nulle doit être examinée. Mais « elle n'a jamais été sérieusement examinée » est faux — l'expérience d'Airy de 1871, avec sa lunette remplie d'eau, était conçue précisément pour cela. Garder le principe, retirer l'affirmation d'absence."),
    ("chronologie-de-la-tromperie-du-globe", 1): (
        "GARDER",
        "contrôle n°39. Exact, et c'est le site appliquant à une observation la rigueur qu'il réclame ailleurs. Le changement d'horizon avec la latitude ne départage effectivement pas les deux modèles."),
    ("chronologie-de-la-tromperie-du-globe", 2): (
        "GARDER",
        "contrôle n°40. Logiquement sain. À noter toutefois qu'il coupe dans les deux sens : un résultat obtenu depuis un postulat plan et confirmé par le calcul ne valide pas davantage ce postulat."),
    ("chronologie-de-la-tromperie-du-globe", 5): (
        "GARDER",
        "contrôle n°41. Exact. Les lois de Kepler sont cinématiques et ne portent aucun mécanisme ; le système de Tycho leur est géométriquement équivalent pour les positions planétaires. C'est un point classique et solide."),
    ("chronologie-de-la-tromperie-du-globe", 6): (
        "GARDER",
        "contrôle n°42. Sain, et coupe dans les deux sens comme le n°40."),
    ("chronologie-de-la-tromperie-du-globe", 9): (
        "RESSERRER",
        "contrôle n°43. L'énoncé est falsifiable, ce qui est sa qualité. Mais il attaque une prédiction que le modèle ne fait pas : au-delà de l'horizon radioélectrique, la propagation par onde ionosphérique, par conduit troposphérique et par diffraction est prévue et mesurée. Il n'y a « zone de silence » qu'en visibilité directe. Préciser la bande et le mode de propagation, sans quoi le test ne tranche rien."),
    ("chronologie-de-la-tromperie-du-globe", 10): (
        "RESSERRER",
        "contrôle n°44. Le critère de Popper est bien énoncé. Mais l'appliquer à une théorie qui produit par ailleurs des prédictions testées revient à juger l'ensemble sur une seule de ses conséquences. Dire de quelle prédiction précise on parle."),
    ("chronologie-de-la-tromperie-du-globe", 11): (
        "DÉCLASSER",
        "contrôle n°45. Le problème de la constante cosmologique est réel et l'écart de 10¹²⁰ est un embarras reconnu de la physique théorique. Mais il ne porte en rien sur la figure de la Terre : vrai ou faux, il n'établit rien de la thèse du site."),
    ("chronologie-de-la-tromperie-du-globe", 12): (
        "DÉCLASSER",
        "contrôle n°46. Argument ad hominem. Que von Braun ait menti sur les capacités de ses fusées pour des raisons de propagande ne porte pas sur ce que les fusées font. Peut être entièrement vrai sans rien établir."),
    ("dune-terre-plate-universelle-a-la-sphere-grecque", 3): (
        "RESSERRER",
        "contrôle n°47. Exact pour DEUX sites, comme au contrôle n°19 : le postulat sur les rayons détermine la conclusion. Faux dès trois sites, où les hauteurs de Soleil impliquées par chaque paire cessent de s'accorder sur un plan."),
    ("dune-terre-plate-universelle-a-la-sphere-grecque", 4): (
        "RESSERRER",
        "contrôle n°48. Vrai de l'ORIGINE de l'idée au VIᵉ siècle avant notre ère : le mobile pythagoricien est bien métaphysique. Faux de ce qui la soutient aujourd'hui. Distinguer la genèse d'une idée de sa base probante actuelle."),
    ("dune-terre-plate-universelle-a-la-sphere-grecque", 6): (
        "GARDER",
        "contrôle n°49. Exact. Les quatre arguments d'Aristote sont des inférences, non des preuves, et le plus fort — l'ombre circulaire pendant les éclipses — reste une inférence."),
    ("la-cosmologie-comme-instrument-de-domination", 1): (
        "DÉCLASSER",
        "contrôle n°50. Le rapprochement Philosophical Doctorate / philosophie est un jeu de mots étymologique, non un argument. La thèse sur les conséquences métaphysiques peut être vraie sans rien établir de la figure de la Terre."),
    ("la-cosmologie-comme-instrument-de-domination", 2): (
        "DÉCLASSER",
        "contrôle n°51. Ad hominem. Les convictions personnelles de Hawking ne portent pas sur la validité de ce qu'il a publié."),
    ("la-gravite-70-theories-et-aucune-preuve", 5): (
        "DÉCLASSER",
        "contrôle n°52. Même contenu que le n°45, et même verdict : l'écart de 10¹²⁰ sur Λ est réel et embarrassant, mais hors sujet pour la figure de la Terre."),
    ("la-rotation-terrestre-deux-experiences-zero-preuve", 5): (
        "RETIRER",
        "contrôle n°53. Les 38 µs/jour ne se décomposent pas comme l'encadré le suppose. Le calcul donne +45,7 µs pour le terme d'altitude seul, −7,2 µs pour la vitesse orbitale du satellite et +0,1 µs pour celle de la station au sol, soit +38,6 µs net. Un modèle « altitude-fréquence » seul prédirait 46 µs, pas 38 : l'écart vaut 19 % et se mesure sans difficulté. L'affirmation « un modèle altitude-fréquence produit la même correction » est donc fausse au chiffre près."),
    ("les-distances-cosmiques-au-dela-de-la-regle", 3): (
        "GARDER",
        "contrôle n°54. Exact, et reconnu comme tel en astronomie : les chandelles standard sont des étalons corrigés, et les incertitudes se propagent en cascade. Rien à resserrer."),
    ("les-trous-noirs-nexistent-pas", 7): (
        "RESSERRER",
        "contrôle n°55. Deux affirmations soudées. La circularité des modèles d'interprétation est une critique méthodologique recevable ; les « pressions institutionnelles » sont une thèse sur des personnes, qui ne se démontre pas de la même façon et n'établit rien du même ordre. Les séparer."),
    ("ligo-londe-qui-nexistait-pas", 3): (
        "RESSERRER",
        "contrôle n°56. Le filtrage adapté n'est pas circulaire au sens vicieux : il teste si les données contiennent un signal de la forme prédite, et la détection est confirmée par la cohérence des paramètres entre détecteurs. La remarque sur les harmoniques du réseau est recevable — et ces raies sont effectivement éliminées par filtres coupe-bande, ce que l'encadré mentionne lui-même."),
    ("ligo-londe-qui-nexistait-pas", 4): (
        "RESSERRER",
        "contrôle n°57. « Aucune réfutation définitive » renverse la charge de la preuve : c'est un argument tiré d'une absence. Et il ignore la contrepartie électromagnétique de GW170817, observée indépendamment par une soixantaine d'observatoires."),
    ("lire-le-ciel-avant-le-globe", 2): (
        "GARDER",
        "contrôle n°58. Exact — et c'est précisément pour cette raison que la hauteur du pôle ne peut PAS servir de variable indépendante pour tester la forme de la Terre : elle définit la latitude. C'est la circularité relevée à la version 1.1 du protocole du pôle céleste. Vrai, et à manier avec cette conséquence."),
    ("lire-le-ciel-avant-le-globe", 5): (
        "GARDER",
        "contrôle n°59. Exact et important : l'observation est antérieure et indépendante de son interprétation. C'est un des énoncés les mieux fondés de l'inventaire."),
    ("neptune-et-pluton-les-faux-triomphes", 5): (
        "RESSERRER",
        "contrôle n°60. Les paramètres A1, A2, A3 sont bien ajustés sur les observations. Mais un paramètre ajusté cesse d'être circulaire dès qu'il PRÉDIT le retour suivant, ce qui est le cas. La critique vise l'ajustement ; le test est la prédiction."),
    ("pourquoi-tout-remettre-en-question", 1): (
        "RESSERRER",
        "contrôle n°61. La distinction observation / expérimentation est réelle. Mais « l'observation seule ne peut pas vérifier » est trop fort : une science observationnelle peut faire des prédictions risquées et les voir échouer. Neptune et les anisotropies du fond diffus en sont deux exemples."),
    ("pourquoi-tout-remettre-en-question", 3): (
        "RESSERRER",
        "contrôle n°62. Le compte interventionniste de Woodward est une position parmi d'autres, et Woodward lui-même admet les expériences naturelles. Attribuer à la philosophie des sciences un verdict unanime qu'elle n'a pas rendu."),
    ("pourquoi-tout-remettre-en-question", 5): (
        "GARDER",
        "contrôle n°63. Exact et non contesté en astronomie : les distances cosmologiques sont inférées, non mesurées. Rien à resserrer — sinon que cela ne porte pas sur la figure de la Terre."),
    ("la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas", 3): (
        "RETIRER",
        "contrôle n°64. Le mois synodique n'est pas « strictement identique » : il varie de 29,27 à 29,83 jours, soit 13 heures d'amplitude et 1,9 %. Cette variation est calculée par le modèle standard, qui la prédit à partir des excentricités. L'encadré présente comme une anomalie une constance qui n'existe pas, et qui serait de toute façon prédite."),
    ("la-perspective-pourquoi-les-objets-disparaissent", 4): (
        "RETIRER",
        "contrôle n°65. Les trois prédictions citées sont réfutées par nos propres contrôles. L'horizon ne reste pas au niveau des yeux : il descend de 100′ depuis 3 107 m (protocole de dépression). Les objets zoomés ne réapparaissent pas tous : la hauteur masquée ne dépend pas du grossissement. Et la courbure ne « disparaît » pas avec un objectif standard : sa flèche vaut 0,22° sur 30° de champ à 39 km, trop faible pour être vue mais non nulle (contrôle n°30)."),
    ("le-theodolite-celeste", 2): (
        "À COMPLÉTER",
        "contrôle n°66. La cohérence interne d'un paramètre ajusté n'est pas une comparaison : les mêmes données traitées par le modèle sphérique produisent une distance Terre-Soleil cohérente elle aussi. Il faut confronter les deux ajustements sur le même jeu, et ce jeu — 11 320 points — doit être versé au dossier."),
    ("mesurer-la-courbure-sur-l-eau-cinq-campagnes", 3): (
        "GARDER",
        "contrôle n°67. Le compliment méthodologique est mérité : prédictions posées d'avance, conception symétrique, géométrie où un seul modèle peut passer. C'est le standard que nos propres protocoles cherchent à atteindre."),
    ("vols-avion-et-courbure-terrestre", 1): (
        "RESSERRER",
        "contrôle n°68. Le fait est exact. Mais les manuels énoncent aussi POURQUOI : l'approximation Terre plate non rotative est valide sur les durées et distances d'un vol, et les mêmes manuels donnent les termes correctifs pour la navigation longue distance. Citer l'hypothèse sans citer sa justification en change le sens."),
    ("vols-avion-et-courbure-terrestre", 7): (
        "RETIRER",
        "contrôle n°69. Réfuté par l'encadré n°8 du même article, que nous gardons : l'accélération centripète vaut 1 milli-g, sous la résolution des enregistreurs. Ce n'est pas de la circularité, c'est une résolution insuffisante — et les deux énoncés ne peuvent pas coexister."),
    ("dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne", 2): (
        "À COMPLÉTER",
        "contrôle n°70. La thèse est datable et vérifiable, mais elle relève de la pile textuelle et historique : il faut établir la chronologie des tafsīr avant et après la réception de Ptolémée. Rangée ici par le tri de surface, elle attend une consultation de sources."),
    ("monter-l-experience-des-trois-mires", 2): (
        "À COMPLÉTER",
        "contrôle n°71. Les rapports 1,1 et 6,1 proviennent de notre propre protocole ; leurs paramètres — hauteurs de mires, distance, incertitude de pointé — doivent être versés au dossier pour que le calcul soit refait. Le point de fond, que le facteur limitant est de savoir où commence la perche, est juste."),
}


def decouper(texte):
    """Rend [(slug, [(no_ligne, numero_encadre)])] dans l'ordre du fichier."""
    lignes = texte.split("\n")
    courant, table = None, []
    for i, l in enumerate(lignes):
        m = re.match(r"`([a-z0-9-]+)` — \d+ encadré", l)
        if m:
            courant = m.group(1)
            continue
        m = re.match(r"\|\s*(\d+)\s*\|", l)
        if m and courant:
            table.append((i, courant, int(m.group(1))))
    return lignes, table


def main():
    ecrire = "--ecrire" in sys.argv
    texte = open(INVENTAIRE, encoding="utf-8").read()
    lignes, table = decouper(texte)

    index = {(slug, n): i for i, slug, n in table}
    manquants = [k for k in VERDICTS if k not in index]
    if manquants:
        print("  ✗ cibles introuvables dans l'inventaire :")
        for slug, n in manquants:
            print("      %s, encadré n°%d" % (slug, n))
        print("    Rien n'est écrit : mieux vaut ne pas annoter que d'annoter à côté.")
        return 1

    modifs, inchanges = [], 0
    for (slug, n), (verdict, note) in sorted(VERDICTS.items()):
        i = index[(slug, n)]
        cells = lignes[i].split("|")
        # | (vide) | n° | énoncé | verdict | (vide)
        if len(cells) < 5:
            print("  ✗ ligne %d mal formée" % (i + 1))
            return 1
        neuf = " **%s** — %s " % (verdict, note.replace("|", "\\|"))
        if cells[3].strip() == neuf.strip():
            inchanges += 1
            continue
        ancien = cells[3].strip()
        cells[3] = neuf
        lignes[i] = "|".join(cells)
        modifs.append((slug, n, ancien, verdict))

    print("Inventaire : %d encadrés relevés." % len(table))
    print("Verdicts adossés à un contrôle reproductible : %d." % len(VERDICTS))
    print()
    for slug, n, ancien, verdict in modifs:
        etat = "vide" if not ancien else ("PÉRIMÉ : " + ancien[:56])
        print("  · %-52s n°%d" % (slug[:52], n))
        print("      %-14s ← %s" % (verdict, etat))
    if inchanges:
        print()
        print("  %d déjà à jour." % inchanges)

    reste = len(table) - len(VERDICTS)
    print()
    print("  Restant à examiner : %d encadrés." % reste)

    if not ecrire:
        print()
        print("  (rapport seul — relancer avec --ecrire pour reporter)")
        return 0
    with open(INVENTAIRE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))
    print()
    print("  ✓ %s mis à jour" % os.path.relpath(INVENTAIRE, RACINE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
