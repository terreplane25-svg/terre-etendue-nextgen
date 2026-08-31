#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retire l'appareil de correction : on applique, on ne raconte pas.

Le corpus et les protocoles gardaient trace de leurs propres versions : des
encadrés « Correction apportée à la version 1.1 », des titres « — ajouté en
1.3 », une section « Ce que nous corrigeons ici, et pourquoi ». Rien de tout
cela n'aide un lecteur qui arrive pour la première fois ; c'est une conversation
entre nous et notre passé, glissée au milieu de l'exposé.

Le principe retenu : un document se lit comme s'il paraissait aujourd'hui.
La correction est appliquée, le chiffre juste est le seul présent, et le
raisonnement qui justifie ce chiffre reste — c'est lui qui a de la valeur, pas
l'aveu. Ce qui doit rester consultable est le registre des corrections, qui
existe déjà comme page à part.

Deuxième retrait, de même nature : le rappel « il nous manque des données, la
charge est symétrique, nous avons déposé un protocole ». Cette question a son
article ; la répéter à chaque expérience la transforme en formule.

Aucune substance n'est perdue : chaque passage supprimé a été relu, et les
valeurs qu'il portait — 12,0 % et 9,5 % pour le contrôle A, la loi de hauteur
maximale de la Lune pour le contrôle B, les 5 338 m du Shkhara — sont conservées
là où elles servent, énoncées comme des faits et non comme des rectifications.

Ce script n'est PAS idempotent : il vise des passages précis. Chaque ancre est
vérifiée avant écriture, et le script s'arrête sans rien modifier si l'une
manque.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")


def couper(src, debut, fin, etiquette):
    """Supprime de `debut` (inclus) jusqu'à `fin` (exclu)."""
    i = src.find(debut)
    if i < 0:
        sys.exit("ancre de début introuvable : %s" % etiquette)
    j = src.find(fin, i)
    if j < 0:
        sys.exit("ancre de fin introuvable : %s" % etiquette)
    return src[:i] + src[j:]


def remplacer(src, vieux, neuf, etiquette):
    if src.count(vieux) != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1."
                 % (etiquette, src.count(vieux)))
    return src.replace(vieux, neuf)


# ════════════════════════════════════════════════════════════════════════════
# 1. Le protocole solaire : deux encadrés d'errata, deux mentions de version
# ════════════════════════════════════════════════════════════════════════════
def protocole_soleil():
    chemin = os.path.join(PROTOCOLES, "soleil-bilingue.html")
    src = open(chemin, encoding="utf-8").read()

    # Contrôle A. Ce que l'encadré disait vraiment : le test porte sur une loi
    # et non sur un nombre, parce que l'amplitude dépend du mois observé. Cet
    # avertissement est utile à qui exécute le protocole — c'est la mention de
    # la version fautive qui ne l'est pas.
    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction apport&#233;e "
        "&#224; la version 1.1</span>\n  <p>La version pr&#233;c&#233;dente "
        "annon&#231;ait &#171; 14,1 % de variation &#187; comme un r&#233;sultat "
        "&#224; retrouver.\n  <strong>C'&#233;tait une faute :</strong> 356 500 et "
        "406 700 km sont les extr&#234;mes <em>pluriannuels</em>,\n  pas ceux d'un "
        "mois quelconque. Un mois favorable donne 12,0 %, un mois d&#233;favorable\n"
        "  <strong>9,5 %</strong> seulement. Un observateur mesurant 9,5 % aurait "
        "conclu &#224; tort que sa\n  cha&#238;ne &#233;tait en d&#233;faut. Le test "
        "porte donc sur la loi, jamais sur une valeur pr&#233;-annonc&#233;e.</p>\n"
        "</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">Aucune valeur n'est "
        "pr&#233;-annonc&#233;e</span>\n  <p>L'amplitude &#224; attendre "
        "d&#233;pend du mois observ&#233;. Les 356 500 et 406 700 km souvent cit&#233;s "
        "sont les\n  extr&#234;mes <em>pluriannuels</em> de la distance lunaire, pas "
        "ceux d'un mois quelconque&#160;: un mois\n  favorable donne 12,0 %, un mois "
        "d&#233;favorable <strong>9,5 %</strong>. Un observateur qui attendrait un "
        "chiffre\n  fixe conclurait &#224; tort que sa cha&#238;ne est en "
        "d&#233;faut. <strong>Le contr&#244;le porte sur la loi</strong> "
        "&#8212;\n  la constance du produit &#952;&#215;d &#8212; et jamais sur une "
        "valeur donn&#233;e d'avance.</p>\n</div>",
        "encadré contrôle A FR")

    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction apport&#233;e "
        "&#224; la version 1.1</span>\n  <p>La version pr&#233;c&#233;dente parlait "
        "de &#171; la Lune au z&#233;nith &#187; et annon&#231;ait +1,67 %.\n  "
        "<strong>Le z&#233;nith est inaccessible &#224; la plupart des "
        "observateurs :</strong> la d&#233;clinaison\n  lunaire ne d&#233;passe pas "
        "&#177;28,6&#176;, donc &#224; la latitude &#966; la Lune ne monte jamais "
        "au-dessus de\n  90&#176; &#8722; |&#966;| + 28,6&#176;. &#192; Paris le "
        "maximum est de 69,7&#176; et le signal vaut 1,42 %, non 1,67 %. Le\n  "
        "protocole emploie d&#233;sormais la loi g&#233;n&#233;rale ci-dessus, "
        "valable &#224; toute latitude.</p>\n</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">Le z&#233;nith est "
        "inaccessible &#224; la plupart des observateurs</span>\n  <p>La "
        "d&#233;clinaison lunaire ne d&#233;passe pas &#177;28,6&#176;&#160;: "
        "&#224; la latitude &#966;, la Lune ne monte donc jamais\n  au-dessus de "
        "<code>90&#176; &#8722; |&#966;| + 28,6&#176;</code>. &#192; Paris le maximum "
        "atteignable est de 69,7&#176; et le\n  signal vaut <strong>1,42 %</strong>, "
        "non les 1,67 % qu'on obtiendrait au z&#233;nith. C'est pourquoi le\n  "
        "protocole emploie la loi g&#233;n&#233;rale ci-dessus, valable &#224; toute "
        "latitude, plut&#244;t qu'un chiffre unique.</p>\n</div>",
        "encadré contrôle B FR")

    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction to version 1.1"
        "</span>\n  <p>The previous version announced &#8220;14.1 per cent "
        "variation&#8221; as a figure to be recovered.\n  <strong>That was a "
        "mistake:</strong> 356 500 and 406 700 km are the <em>multi-year</em> "
        "extremes,\n  not those of an arbitrary month. A favourable month gives "
        "12.0 per cent, an unfavourable one\n  only <strong>9.5 per cent</strong>. "
        "An observer measuring 9.5 per cent would wrongly have\n  concluded the chain "
        "was at fault. The test therefore bears on the law, never on a pre-announced\n"
        "  value.</p>\n</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">No value is announced in "
        "advance</span>\n  <p>The amplitude to expect depends on the month observed. "
        "The 356 500 and 406 700 km often quoted\n  are the <em>multi-year</em> "
        "extremes of the lunar distance, not those of an arbitrary month: a\n  "
        "favourable month gives 12.0 per cent, an unfavourable one <strong>9.5 per "
        "cent</strong>. An observer\n  expecting a fixed figure would wrongly conclude "
        "the chain was at fault. <strong>The control bears\n  on the law</strong> "
        "&#8212; the constancy of the product &#952;&#215;d &#8212; and never on a "
        "value given in advance.</p>\n</div>",
        "encadré contrôle A EN")
    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction to version 1.1"
        "</span>\n  <p>The previous version spoke of &#8220;the Moon at the "
        "zenith&#8221; and announced +1.67 per cent.\n  <strong>The zenith is "
        "unreachable for most observers:</strong> lunar declination never exceeds\n"
        "  &#177;28.6&#176;, so at latitude &#966; the Moon never rises above "
        "90&#176; &#8722; |&#966;| + 28.6&#176;. In Paris the maximum\n  is 69.7&#176; "
        "and the signal is 1.42 per cent, not 1.67. The protocol now uses the general "
        "law\n  above, valid at any latitude.</p>\n</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">The zenith is out of reach "
        "for most observers</span>\n  <p>Lunar declination never exceeds "
        "&#177;28.6&#176;: at latitude &#966;, the Moon therefore never rises\n  above "
        "<code>90&#176; &#8722; |&#966;| + 28.6&#176;</code>. In Paris the attainable "
        "maximum is 69.7&#176; and the signal is\n  <strong>1.42 per cent</strong>, "
        "not the 1.67 one would obtain at the zenith. This is why the protocol\n  uses "
        "the general law above, valid at any latitude, rather than a single figure.</p>"
        "\n</div>",
        "encadré contrôle B EN")

    src = remplacer(src,
                    "Ce que la verticale donne gratuitement &#8212; ajout&#233; en 1.3",
                    "Ce que la verticale donne gratuitement", "label 1.3 FR")

    # Le tableau du budget d'erreur porte « ajouté en 1.3 » en tête de la
    # justification de deux lignes. La justification reste, la date part.
    for vieux, neuf in (("<strong>ajout&#233; en 1.3</strong> &#8212; ", ""),
                        ("<strong>added in 1.3</strong> &#8212; ", "")):
        if vieux in src:
            src = src.replace(vieux, neuf)

    open(chemin, "w", encoding="utf-8").write(src)
    return "soleil-bilingue.html"


# ════════════════════════════════════════════════════════════════════════════
# 2. Le protocole du pôle céleste : deux titres datés
# ════════════════════════════════════════════════════════════════════════════
def protocole_pole():
    chemin = os.path.join(PROTOCOLES, "pole-celeste-bilingue.html")
    src = open(chemin, encoding="utf-8").read()
    src = remplacer(src,
                    "La déviation de la verticale &#8212; ajout&#233; en 1.2",
                    "La déviation de la verticale", "titre 1.2 FR")
    src = remplacer(src, "Deflection of the vertical &#8212; added in 1.2",
                    "Deflection of the vertical", "titre 1.2 EN")

    # Le point de méthode — mesurer une distance au sol plutôt que de porter la
    # hauteur du pôle contre la latitude — est ce qui empêche le test d'être
    # circulaire. Il reste, énoncé comme une exigence et non comme un repentir.
    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction apport&#233;e "
        "&#224; la version 1.0</span>\n  <p>La version 1.0 portait la hauteur du "
        "p&#244;le <em>contre la latitude</em>, et souffrait donc de\n  la m&#234;me "
        "circularit&#233; que le test 2. Le test est ici r&#233;exprim&#233; en "
        "<strong>distance au sol\n  mesur&#233;e &#224; l'odom&#232;tre</strong> "
        "depuis une station de r&#233;f&#233;rence. Les chiffres ne changent pas ;\n"
        "  la circularit&#233; dispara&#238;t.</p>\n</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">Pourquoi une distance au "
        "sol, et non une latitude</span>\n  <p>Porter la hauteur du p&#244;le "
        "<em>contre la latitude</em> rendrait ce test circulaire, de la m&#234;me "
        "mani&#232;re\n  que le test 2&#160;: la latitude est elle-m&#234;me "
        "d&#233;finie &#224; partir de la hauteur du p&#244;le. Le test s'exprime "
        "donc\n  en <strong>distance au sol mesur&#233;e &#224; "
        "l'odom&#232;tre</strong> depuis une station de r&#233;f&#233;rence, "
        "grandeur qui ne\n  doit rien &#224; l'astronomie. Les chiffres attendus sont "
        "les m&#234;mes ; la circularit&#233; dispara&#238;t.</p>\n</div>",
        "encadré circularité FR")
    src = remplacer(
        src,
        "<div class=\"box warn\">\n  <span class=\"lab\">Correction to version 1.0"
        "</span>\n  <p>Version 1.0 plotted pole altitude <em>against latitude</em>, "
        "and therefore suffered the same\n  circularity as test 2. The test is here "
        "re-expressed in <strong>ground distance measured by\n  odometer</strong> "
        "from a reference station. The figures do not change; the circularity\n  "
        "goes.</p>\n</div>",
        "<div class=\"box warn\">\n  <span class=\"lab\">Why a ground distance, and "
        "not a latitude</span>\n  <p>Plotting pole altitude <em>against latitude</em> "
        "would make this test circular, in the same way as\n  test 2: latitude is "
        "itself defined from the altitude of the pole. The test is therefore "
        "expressed\n  in <strong>ground distance measured by odometer</strong> from a "
        "reference station, a quantity that\n  owes nothing to astronomy. The expected "
        "figures are the same; the circularity goes.</p>\n</div>",
        "encadré circularité EN")

    open(chemin, "w", encoding="utf-8").write(src)
    return "pole-celeste-bilingue.html"


# ════════════════════════════════════════════════════════════════════════════
# 3. Les articles
# ════════════════════════════════════════════════════════════════════════════
def article(slug, transformer):
    chemin = os.path.join(ARTICLES, slug + ".json")
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    avant = data["htmlBody"]
    data["htmlBody"] = transformer(avant)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return slug, len(avant) - len(data["htmlBody"])


def perspective(h):
    # Les deux sections partent en bloc : le chiffre juste (5 338 m) et le
    # raisonnement qui l'établit sont déjà au-dessus, dans le tableau et dans
    # l'encadré-clé. Ne restait que le récit de la version fautive.
    h = couper(h, "<h3>Ce que nous corrigeons ici, et pourquoi</h3>",
               '<h2 id="tableau-general">', "sections errata + charge symétrique")

    # Le même aveu, en incise, dans la discussion de la méthode.
    h = remplacer(
        h,
        "façon de faire, que nous avons nous-mêmes employée dans une version "
        "précédente de cette page, n'a pas de sens physique.",
        "façon de faire n'a pas de sens physique.",
        "incise « version précédente »")

    # Le cas de Washington's Rock reste, parce qu'il est instructif : c'est une
    # observation qu'on avance souvent et qui ne démontre rien. Ce qui part,
    # c'est le récit de son passage dans nos propres pages.
    h = remplacer(
        h,
        "<p><em>Un cas que nous retirons.</em> Cette section citait auparavant les "
        "skylines de New York et de Philadelphie vues simultanément depuis "
        "Washington's Rock, en additionnant les deux distances pour obtenir "
        "193&nbsp;km et 244&nbsp;m de courbure. L'addition n'a pas de sens&nbsp;: "
        "ce sont deux visées distinctes d'une soixantaine de kilomètres chacune, "
        "et depuis 122&nbsp;m d'altitude la sphère n'y masque qu'une trentaine de "
        "mètres. Elle prédit donc les deux panoramas. Le cas ne prouvait rien et "
        "il est écarté.</p>",
        "<p><em>Un cas qu'il faut écarter.</em> On avance souvent les skylines de "
        "New York et de Philadelphie vues simultanément depuis Washington's Rock, "
        "en additionnant les deux distances pour obtenir 193&nbsp;km et "
        "244&nbsp;m de courbure. L'addition n'a pas de sens&nbsp;: ce sont deux "
        "visées distinctes d'une soixantaine de kilomètres chacune, et depuis "
        "122&nbsp;m d'altitude la sphère n'y masque qu'une trentaine de mètres. "
        "Elle prédit donc les deux panoramas sans difficulté. L'observation est "
        "réelle&nbsp;; elle ne démontre rien.</p>",
        "incise « cas retiré »")
    return h


def vols_avion(h):
    return remplacer(
        h,
        "<p>C'est ici que nous devons corriger ce que cet article affirmait. Nous "
        "en tirions que si l'avion suivait une sphère, le gyroscope enregistrerait "
        "ce basculement continu, et que son silence valait démonstration. "
        "<strong>C'est faux, et pour une raison technique vérifiable dans n'importe "
        "quel manuel de pilotage.</strong></p>",
        "<p>On en tire souvent que si l'avion suivait une sphère, le gyroscope "
        "enregistrerait ce basculement continu, et que son silence vaudrait "
        "démonstration. <strong>C'est faux, et pour une raison technique vérifiable "
        "dans n'importe quel manuel de pilotage.</strong></p>",
        "aveu vols-avion")


def main():
    faits = [protocole_soleil(), protocole_pole()]
    for slug, gain in (article("la-perspective-pourquoi-les-objets-disparaissent",
                               perspective),
                       article("vols-avion-et-courbure-terrestre", vols_avion)):
        faits.append("%s (−%d caractères)" % (slug, gain))

    # Contrôle final : plus aucune trace de l'appareil de correction.
    restes = []
    for dossier, ext in ((PROTOCOLES, ".html"), (ARTICLES, ".json")):
        for nom in sorted(os.listdir(dossier)):
            if not nom.endswith(ext):
                continue
            txt = open(os.path.join(dossier, nom), encoding="utf-8").read()
            for motif in (r"[Cc]orrection apport", r"[Cc]orrection made in version",
                          r"version pr&#233;c&#233;dente", r"version précédente",
                          r"[Tt]he previous version", r"ajout&#233; en 1\.",
                          r"added in 1\.", r"nous corrigeons",
                          r"nous devons corriger", r"charge est symétrique"):
                if re.search(motif, txt):
                    restes.append("%s : %s" % (nom, motif))
    if restes:
        sys.exit("il reste :\n  " + "\n  ".join(restes))

    print("Appareil de correction retiré de :")
    for f in faits:
        print("  ·", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
