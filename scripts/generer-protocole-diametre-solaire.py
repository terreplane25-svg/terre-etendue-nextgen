#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit le protocole « Le diamètre du Soleil, du zénith à l'horizon ».

Pourquoi celui-ci, et pourquoi maintenant
─────────────────────────────────────────
C'est l'observable qui départage le plus nettement un Soleil lointain d'un
Soleil local, et personne ne l'a mesurée proprement dans le débat — on la
discute, on la calcule de travers, on montre des captures d'écran de vidéos
YouTube. Elle demande un appareil photo, un filtre solaire et une journée.

Ce qui la rend décisive
───────────────────────
Un Soleil local à hauteur h au-dessus d'un plan est vu à la portée s = h/sin(α),
où α est son élévation. Son diamètre angulaire varie donc comme sin(α) : à 30°
d'élévation il devrait faire la MOITIÉ de sa taille au zénith. Un Soleil à
150 millions de kilomètres, lui, ne change pas de taille dans la journée — sa
distance varie de moins de 0,01 % entre le zénith et l'horizon.

Entre 60° et 10° d'élévation, le modèle local prédit un passage de 27,7′ à 5,6′.
Le modèle standard prédit 32,0′ dans les deux cas. L'écart est de 22′ contre un
budget instrumental de 0,13′ au 300 mm : rapport signal sur bruit d'environ 200.

Et la réfraction ne peut pas sauver la mise, pour une raison métrologique
précise : elle agit verticalement. Près de l'horizon elle relève le bord
inférieur de 35,4′ et le supérieur de 28,8′, ce qui aplatit le disque d'environ
21 % — un effet réel, visible, et bien documenté. Le diamètre HORIZONTAL, lui,
n'est pas touché. Mesurer l'horizontal retire donc la réfraction du débat au
lieu de la laisser servir d'explication à tout.

Toutes les valeurs de ce fichier sont recalculées à l'exécution.
"""
import json
import math
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "mesurer-le-diametre-du-soleil"
CIBLE = os.path.join(RACINE, "content", "articles", SLUG + ".json")

H_LOCAL = 5000.0        # km — altitude du Soleil dans le modèle local courant
THETA_ZENITH = 32.0     # ′ — diamètre angulaire observé au zénith
REFRACTION_BAS = 35.4   # ′ — relèvement du bord inférieur à l'horizon
REFRACTION_HAUT = 28.8  # ′ — relèvement du bord supérieur


def theta_local(alpha):
    """Diamètre angulaire d'un Soleil local, en minutes d'arc."""
    return THETA_ZENITH * math.sin(math.radians(alpha))


def echelle(focale_mm, capteur_mm, pixels):
    """Secondes d'arc par pixel, et erreur sur un diamètre lu à ±1,5 px."""
    taille_px = capteur_mm / pixels / 1000.0
    sec_par_px = math.degrees(taille_px / (focale_mm / 1000.0)) * 3600
    return sec_par_px, 2 * 1.5 * sec_par_px / 60.0


def main():
    sec_px, err = echelle(300, 23.5, 6000)
    signal = theta_local(60) - theta_local(10)
    rsb = signal / err
    aplat = 100 * (REFRACTION_BAS - REFRACTION_HAUT) / THETA_ZENITH

    lignes = [
        '<p class="tei-lede">Un Soleil local à 5 000 km devrait faire la moitié '
        'de sa taille du zénith quand il descend à 30° d\'élévation. Un Soleil à '
        '150 millions de kilomètres ne change pas de taille de la journée. '
        'L\'écart entre les deux prédictions est de %s minutes d\'arc&nbsp;; un '
        'téléobjectif de 300&nbsp;mm en mesure %s. Cette page dit comment '
        'trancher.</p>\n' % (("%.0f" % signal), ("%.2f" % err).replace(".", ",")),

        '<div class="tei-fait experiences">\n'
        '  <span class="tei-fait-label">CE QUE L\'EXPÉRIENCE ÉTABLIT</span>\n'
        '  <p>Le diamètre angulaire du Soleil en fonction de son élévation. Les '
        'deux modèles en font des prédictions incompatibles et écrites d\'avance. '
        'Aucune donnée institutionnelle n\'entre dans la mesure.</p>\n</div>\n',

        # ── 01 ────────────────────────────────────────────────────────────
        '<h2 id="observable"><span class="tei-section-num">01</span>L\'observable, '
        'et pourquoi c\'est la bonne</h2>\n',
        "<p>On mesure une seule grandeur&nbsp;: le <strong>diamètre angulaire "
        "horizontal du Soleil</strong>, en minutes d'arc, en fonction de son "
        "<strong>élévation au-dessus de l'horizon</strong>. Rien d'autre. Pas de "
        "distance, pas de taille réelle, pas de modèle supposé.</p>\n",
        "<p>Sa force tient à ceci&nbsp;: elle ne demande aucune donnée qu'on "
        "devrait croire sur parole. L'élévation se lit au fil à plomb ou se "
        "calcule depuis l'heure et le lieu&nbsp;; le diamètre se compte en pixels "
        "sur une image. Les deux se vérifient sur la photographie elle-même, que "
        "n'importe qui peut réclamer et refaire.</p>\n",

        # ── 02 ────────────────────────────────────────────────────────────
        '<h2 id="predictions"><span class="tei-section-num">02</span>Ce que '
        'chaque modèle prédit</h2>\n',
        "<p>Un Soleil placé à une hauteur <em>h</em> au-dessus d'un plan est vu à "
        "la portée <em>s</em> = <em>h</em>/sin(α), où α est son élévation. Son "
        "diamètre angulaire varie donc comme <strong>sin(α)</strong>. Un Soleil à "
        "150 millions de kilomètres, lui, voit sa distance changer de moins de "
        "0,01&nbsp;% entre le zénith et l'horizon&nbsp;: son diamètre ne bouge "
        "pas de la journée.</p>\n",
        '<table class="tei-table">\n<thead><tr><th>élévation du Soleil</th>'
        '<th>modèle local<br><small>h = 5 000 km</small></th>'
        '<th>modèle standard</th><th>écart</th></tr></thead>\n<tbody>\n',
    ]
    for a in (60, 45, 30, 20, 10):
        loc = theta_local(a)
        fr = lambda v: ("%.1f" % v).replace(".", ",")
        lignes.append("<tr><td>%d°</td><td>%s&#8242;</td><td>%s&#8242;</td>"
                      "<td><strong>%s&#8242;</strong></td></tr>\n"
                      % (a, fr(loc), fr(THETA_ZENITH), fr(THETA_ZENITH - loc)))
    lignes += [
        "</tbody>\n</table>\n",
        '<p><em>Le modèle local est calibré pour tomber juste au zénith&nbsp;: '
        "c'est le traitement le plus favorable qu'on puisse lui accorder. Avec "
        "une hauteur plus grande, l'écart diminue&nbsp;; mais aucune hauteur ne "
        "l'annule, parce que la loi en sin(α) ne dépend pas de <em>h</em>.</em></p>\n",
        '<div class="tei-enclair">\n<span class="tei-enclair-label">En clair</span>\n'
        "<p>Une lampe accrochée au plafond d'un hangar paraît plus petite quand on "
        "s'en éloigne, parce qu'on la voit de plus loin en diagonale. Une lampe "
        "située à des kilomètres au-dessus ne change pas de taille quand on "
        "traverse le hangar&nbsp;: quelques centaines de mètres ne comptent pas "
        "face à des kilomètres. La question est de savoir dans lequel des deux "
        "hangars nous vivons, et le Soleil répond tout seul si on le "
        "photographie.</p>\n</div>\n",

        # ── 03 ────────────────────────────────────────────────────────────
        '<h2 id="refraction"><span class="tei-section-num">03</span>Pourquoi la '
        'réfraction ne peut pas sauver la mise</h2>\n',
        "<p>L'objection est connue et elle mérite une réponse chiffrée&nbsp;: "
        "«&nbsp;la réfraction atmosphérique compense la perspective et maintient "
        "la taille apparente&nbsp;». Elle se teste, et elle échoue sur un point "
        "précis.</p>\n",
        "<p>Près de l'horizon, la réfraction relève le bord inférieur du disque "
        "de %s&#8242; et le bord supérieur de %s&#8242;. L'écart entre les "
        "deux <strong>aplatit le disque d'environ %.0f&nbsp;%%</strong> — c'est "
        "l'ovale bien connu du Soleil couchant, réel et photographiable. Mais "
        "cet effet est <strong>vertical</strong>. Le diamètre "
        "<strong>horizontal</strong> n'est pas touché&nbsp;: les deux bords "
        "gauche et droite sont à la même altitude, donc relevés de la même "
        "quantité.</p>\n" % (("%.1f" % REFRACTION_BAS).replace(".", ","),
                             ("%.1f" % REFRACTION_HAUT).replace(".", ","), aplat),
        '<div class="tei-highlight"><p>C\'est ce qui rend la mesure décisive. En '
        "mesurant le diamètre <strong>horizontal</strong>, on retire la réfraction "
        "du débat au lieu de la laisser servir d'explication à tout. Une "
        "réfraction qui maintiendrait la taille apparente devrait le faire dans "
        "les deux axes&nbsp;; elle ne le fait que dans un. Et l'aplatissement "
        "observé prouve précisément qu'elle agit verticalement.</p></div>\n",

        # ── 04 ────────────────────────────────────────────────────────────
        '<h2 id="unites"><span class="tei-section-num">04</span>Une erreur '
        'd\'unités à écarter d\'abord</h2>\n',
        "<p>Un calcul circule, des deux côtés du débat, qui conclut qu'un Soleil "
        "de 1&#8239;392&#8239;000&nbsp;km de diamètre placé à 100&#8239;000&nbsp;km "
        "ferait 0,8° dans le ciel, «&nbsp;proche de ce qu'on voit&nbsp;». "
        "<strong>Le résultat est faux d'un facteur mille</strong>&nbsp;: il a été "
        "obtenu avec 100&#8239;000&#8239;000&nbsp;km. À "
        "100&#8239;000&nbsp;km, un objet de 1&#8239;392&#8239;000&nbsp;km de "
        "diamètre occuperait <strong>%.0f°</strong> du ciel — il envelopperait "
        "l'observateur.</p>\n" % (2 * math.degrees(math.atan(696000.0 / 100000.0))),
        "<p>Il faut le dire, parce que ce calcul est repris tel quel dans des "
        "publications qui se veulent sérieuses, et qu'il discrédite la question "
        "qu'il prétend poser. Le modèle local cohérent n'est pas «&nbsp;le Soleil "
        "des manuels, mais plus près&nbsp;»&nbsp;: c'est un Soleil <strong>petit "
        "et proche</strong>. Pour faire %.0f&#8242; au zénith depuis "
        "%.0f&#8239;000&nbsp;km, il doit mesurer environ <strong>%.0f&nbsp;km de "
        "diamètre</strong>. C'est cette version-là que le protocole teste, parce "
        "que c'est la seule qui tienne debout.</p>\n"
        % (THETA_ZENITH, H_LOCAL / 1000,
           2 * H_LOCAL * math.tan(math.radians(THETA_ZENITH / 60 / 2))),

        # ── 05 ────────────────────────────────────────────────────────────
        '<h2 id="materiel"><span class="tei-section-num">05</span>Matériel</h2>\n',
        '<div class="tei-data"><strong>Sécurité — à lire avant tout le '
        "reste</strong><br/>Ne jamais viser le Soleil sans filtre, ni à l'œil ni "
        "au viseur optique. Un téléobjectif concentre assez d'énergie pour "
        "détruire une rétine en une fraction de seconde et pour brûler un "
        "capteur. Le filtre se pose <strong>devant</strong> l'objectif, jamais "
        "derrière.</div>\n",
        "<ul>\n"
        "<li>Un appareil photo à objectif interchangeable et un "
        "<strong>téléobjectif de 300&nbsp;mm ou plus</strong>. La focale ne doit "
        "pas changer d'une prise à l'autre — zoom scotché en butée, ou focale "
        "fixe.</li>\n"
        "<li>Un <strong>filtre solaire pleine ouverture</strong> de densité 5 "
        "(film type AstroSolar ou équivalent certifié), posé devant l'objectif.</li>\n"
        "<li>Un trépied.</li>\n"
        "<li>Un moyen de connaître l'heure à la seconde et la position à "
        "100&nbsp;m près — un téléphone suffit.</li>\n"
        "</ul>\n",

        # ── 06 ────────────────────────────────────────────────────────────
        '<h2 id="protocole"><span class="tei-section-num">06</span>Protocole</h2>\n',
        "<ol>\n"
        "<li><strong>Choisir une journée dégagée</strong>, du lever au coucher si "
        "possible. Une seule journée suffit&nbsp;; deux valent mieux.</li>\n"
        "<li><strong>Fixer la focale et ne plus y toucher.</strong> C'est la "
        "règle la plus importante du protocole&nbsp;: tout le résultat repose sur "
        "une échelle angulaire constante. Photographier une fois une mire au sol "
        "pour vérifier après coup que la focale n'a pas bougé.</li>\n"
        "<li><strong>Photographier le Soleil toutes les trente minutes</strong>, "
        "en notant l'heure exacte de chaque cliché. Viser une exposition qui ne "
        "sature pas le disque&nbsp;: un bord surexposé s'élargit, et c'est le "
        "principal piège de cette mesure.</li>\n"
        "<li><strong>Prendre trois clichés à chaque fois</strong>, pour disposer "
        "d'une dispersion et non d'un point unique.</li>\n"
        "<li><strong>Descendre le plus bas possible</strong>&nbsp;: c'est "
        "au-dessous de 20° d'élévation que les deux modèles s'écartent le plus. "
        "Un horizon marin ou de plaine est préférable.</li>\n"
        "<li><strong>Noter la météo</strong> — température, pression, humidité, "
        "et l'état du ciel près de l'horizon.</li>\n"
        "</ol>\n",
        "<p>Le dépouillement&nbsp;: pour chaque image, mesurer le "
        "<strong>diamètre horizontal en pixels</strong>, converti en minutes "
        "d'arc par l'échelle de l'objectif. Calculer l'élévation du Soleil depuis "
        "l'heure et le lieu. Porter le diamètre en fonction du sinus de "
        "l'élévation.</p>\n",

        # ── 07 ────────────────────────────────────────────────────────────
        '<h2 id="budget"><span class="tei-section-num">07</span>Budget '
        'd\'erreur</h2>\n',
        '<table class="tei-table">\n<thead><tr><th>poste</th><th>valeur</th>'
        '<th>remarque</th></tr></thead>\n<tbody>\n'
        "<tr><td>Échelle d'un 300&nbsp;mm sur capteur APS-C</td>"
        "<td>%s&#8243;/pixel</td><td>disque solaire = %d pixels</td></tr>\n"
        "<tr><td>Lecture des deux bords à ±1,5 pixel</td>"
        "<td>±%s&#8242;</td><td>poste dominant</td></tr>\n"
        "<tr><td>Turbulence atmosphérique</td><td>&lt; 0,1&#8242;</td>"
        "<td>moyennée sur trois clichés</td></tr>\n"
        "<tr><td>Variation annuelle réelle du diamètre</td><td>±0,55&#8242;</td>"
        "<td>négligeable sur une journée</td></tr>\n"
        "<tr><td><strong>Signal à mesurer, de 60° à 10°</strong></td>"
        "<td><strong>%s&#8242;</strong></td><td>prédiction du modèle local</td></tr>\n"
        "</tbody>\n</table>\n" % (("%.2f" % sec_px).replace(".", ","),
                                  int(THETA_ZENITH * 60 / sec_px),
                                  ("%.2f" % err).replace(".", ","),
                                  ("%.1f" % signal).replace(".", ",")),
        '<div class="tei-fait experiences">\n'
        '  <span class="tei-fait-label">CE QUE L\'EXPÉRIENCE ÉTABLIT</span>\n'
        "  <p>Rapport signal sur bruit d'environ <strong>%.0f</strong> avec un "
        "simple téléobjectif de 300&nbsp;mm. Ce n'est pas une mesure difficile&nbsp;: "
        "c'est une mesure que personne n'a publiée proprement.</p>\n</div>\n" % rsb,

        # ── 08 ────────────────────────────────────────────────────────────
        '<h2 id="criteres"><span class="tei-section-num">08</span>Les critères '
        'de décision, écrits avant la première photographie</h2>\n',
        "<p>Ils sont posés maintenant, et ils ne bougeront pas quand les données "
        "arriveront.</p>\n",
        "<ol>\n"
        "<li><strong>Issue 1 — Soleil lointain.</strong> Si le diamètre "
        "horizontal reste constant à ±1&#8242; sur toute la plage d'élévation "
        "parcourue, le Soleil local à quelques milliers de kilomètres est écarté, "
        "et nous le publierons ainsi, sans atténuation.</li>\n"
        "<li><strong>Issue 2 — Soleil local.</strong> Si le diamètre suit "
        "sin(α) à ±10&nbsp;%, le modèle standard est en difficulté sur cette "
        "observable, et il faudra le dire aussi nettement.</li>\n"
        "<li><strong>Issue 3 — ni l'un ni l'autre.</strong> Si le diamètre varie "
        "sans suivre sin(α), ni l'un ni l'autre modèle ne rend compte de la "
        "mesure, et c'est ce résultat-là qui sera publié — c'est le plus "
        "intéressant des trois.</li>\n"
        "</ol>\n",
        "<p><strong>Dans les trois cas, les images brutes sont publiées.</strong> "
        "Pas les courbes&nbsp;: les fichiers, avec leurs métadonnées, pour que "
        "n'importe qui refasse le dépouillement sans nous croire.</p>\n",

        # ── 09 ────────────────────────────────────────────────────────────
        '<h2 id="sources"><span class="tei-section-num">09</span>Sources</h2>\n',
        '<p class="tei-src-legende">Chaque source porte sa classe de '
        "vérifiabilité. Elle ne dit pas si la source est bonne, mais ce "
        "qu&#8217;elle permet de faire&nbsp;: <b>A</b> mesure directe, protocole "
        "et instrument connus &#8212; conclure. <b>B</b> chemin mesuré mais "
        "indirect &#8212; borner. <b>C</b> valeur rapportée, calculée depuis un "
        "modèle, ou source primaire non consultée &#8212; illustrer, jamais "
        "conclure. <b>D</b> déclarative, affirmée sans donnée jointe &#8212; "
        "rien. <b>renvoi</b> désigne un de nos propres articles, qui n&#8217;est "
        'pas une source. La grille est détaillée dans <a href="/article/'
        'standards-et-methode">Standards et méthode</a>.</p>\n',
        "<ol>\n"
        '<li><span class="tei-grade grade-a">A</span> Les valeurs de ce protocole '
        "sont calculées, non rapportées&nbsp;: θ = 2·arctan(R/s) avec "
        "s = h/sin(α), et l'échelle angulaire d'un objectif par sa focale et la "
        "taille de photosite. Le script qui les produit est "
        "<code>scripts/generer-protocole-diametre-solaire.py</code>&nbsp;; elles "
        "se refont en trois lignes.</li>\n"
        '<li><span class="tei-grade grade-b">B</span> U.S. Naval Observatory, '
        "<em>Astronomical Almanac</em> — réfraction à l'horizon, relèvement du "
        "bord inférieur d'environ 35&#8242;. Valeur tabulée, issue d'un modèle "
        "atmosphérique standard&nbsp;: elle borne, elle ne conclut pas.</li>\n"
        '<li><span class="tei-grade grade-c">C</span> Variation annuelle du '
        "diamètre solaire apparent, de 31,6&#8242; à 32,7&#8242; entre aphélie et "
        "périhélie. Valeur d'éphéméride, calculée depuis le modèle standard "
        "lui-même&nbsp;: citée pour situer un ordre de grandeur, pas comme "
        "preuve.</li>\n"
        '<li><span class="tei-grade grade-d">D</span> Le calcul en circulation '
        "concluant qu'un Soleil de 1&#8239;392&#8239;000&nbsp;km à "
        "100&#8239;000&nbsp;km ferait 0,8°. Affirmé sans vérification "
        "d'unités&nbsp;; refait ici, il donne 164°. Cité pour être écarté.</li>\n"
        '<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/'
        'les-protocoles-ce-que-c-est-et-pourquoi">Les protocoles — ce que c\'est '
        "et pourquoi</a> — les six règles que ce document applique.</li>\n"
        '<li><span class="tei-grade grade-lien">renvoi</span> <a href="/article/'
        'la-perspective-pourquoi-les-objets-disparaissent">La perspective</a> — '
        "pourquoi un point de fuite ne fait pas descendre un objet sous "
        "l'horizon.</li>\n"
        "</ol>\n",
    ]

    art = {
        "title": "Mesurer le diamètre du Soleil, du zénith à l'horizon",
        "description": (
            "Un Soleil local à 5 000 km devrait perdre la moitié de sa taille "
            "entre le zénith et 30° d'élévation ; un Soleil lointain n'en perd "
            "rien. Un téléobjectif, un filtre solaire, une journée — et le "
            "critère de décision écrit d'avance."),
        "date": "2026-08-31",
        "updated": "2026-08-31",
        "author": "Terre Etendue",
        "category": "experiences",
        "tags": ["soleil", "diametre-angulaire", "protocole", "refraction",
                 "perspective", "pre-enregistrement"],
        "pinned": False,
        "htmlBody": "".join(lignes),
    }
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("signal 60°→10° : %.1f′ · budget instrumental : %.2f′ · rapport %.0f"
          % (signal, err, rsb))


if __name__ == "__main__":
    main()
