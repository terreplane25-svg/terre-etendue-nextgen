#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Applique au dossier des trous noirs la forme courte du dossier LIGO.

Ce que la forme courte veut dire, concrètement : une idée par section, un fait
établi par section, aucune digression, et le lecteur qui sait où il en est à
chaque instant. Le dossier LIGO le fait en six sections et 1 570 mots. Celui-ci
en faisait 8 318 en douze sections, et disait la même chose quatre fois.

Trois opérations, dans cet ordre de valeur.

1. Les redites. « Ce qu'on observe / ce qu'on en déduit » est le fil conducteur
   du dossier — et il était énoncé en entier dans l'avant-propos, redit en 6.1,
   redit en 8.1 et 8.2, puis récapitulé en 9.1 et 9.2. Le lecteur qui arrive à
   la synthèse a déjà lu quatre fois la même distinction. Elle est posée une
   fois, à sa place, et les rappels sautent.

2. Les deux théories alternatives. Logunov et Greiner occupaient 1 552 mots en
   deux sections, avec le détail des lois de conservation, du théorème de
   Noether, des nombres pseudo-complexes et des quasi-oscillateurs périodiques.
   Ce détail est de la physique théorique, il n'est pas de nous, et il ne
   change pas la conclusion : deux extensions publiées éliminent l'horizon en
   restant compatibles avec ce qu'on observe. C'est ce qui compte, et cela tient
   en une section.

3. La numérotation décimale. Les sous-sections portaient « 1.1, 2.1, 3.1 » en
   plus de la numérotation des sections, deux systèmes concurrents dans la même
   page. Le second saute.

Ce qui ne change pas : aucune affirmation n'est retirée, aucune source n'est
retirée, aucun chiffre n'est modifié. Ce qui part, ce sont des répétitions et du
développement théorique de seconde main. Les phrases conservées le sont mot pour
mot — on ne paraphrase pas ce qu'on n'a pas mesuré soi-même.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(RACINE, "content", "articles", "les-trous-noirs-existent-ils.json")


def decouper(html):
    """La page en (titre, corps), le préambule éventuel en tête."""
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", html, flags=re.S)
    tete = parts[0]
    blocs = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    return tete, blocs


# ── Avant-propos : la distinction posée une fois, sans le vocabulaire ────────
AVANT_PROPOS = """
<p class="tei-lede">On nous présente les trous noirs comme un fait acquis, démontré, photographié. Une question est rarement posée&nbsp;: qu'a-t-on réellement observé, et qu'a-t-on seulement déduit&nbsp;?</p>
<p>Tout ce dossier tient sur cette distinction, et il la tiendra jusqu'au bout. Un médecin qui lit 39&nbsp;°C sur un thermomètre observe un fait. Quand il dit «&nbsp;vous avez une infection bactérienne&nbsp;», il propose une interprétation — qui peut être juste, fausse, ou partielle. Confondre les deux est une erreur de méthode, pas une nuance de vocabulaire.</p>
<p>Nous ne cherchons pas à défaire la physique ni à promouvoir une théorie dissidente. La question n'est pas «&nbsp;la science a-t-elle tort&nbsp;?&nbsp;». Elle est&nbsp;: <strong>entre ce que les télescopes mesurent et ce qu'on en conclut, où passe exactement la frontière&nbsp;?</strong></p>
"""

# ── Les deux alternatives, en une section ───────────────────────────────────
ALTERNATIVES = """
<p>Deux extensions de la relativité générale, publiées dans des revues à comité de lecture par des physiciens de premier plan, éliminent l'une comme l'autre l'horizon des événements et la singularité — sans contredire ce qu'on observe. Nous les rapportons&nbsp;; nous n'en avons refait aucun calcul.</p>

<h3>La théorie relativiste de la gravitation (Logunov, 1988-1995)</h3>
<p>Anatoly Logunov, directeur de l'Institut de physique des hautes énergies de Protvino et membre de l'Académie des sciences de l'URSS, adresse trois reproches à la relativité générale&nbsp;: elle ne possède pas de lois de conservation strictes de l'énergie — problème relevé par Hilbert dès 1917 —, ses équations admettent pour un même système plusieurs solutions donnant des prédictions différentes, et elle autorise des topologies qui violent la causalité.</p>
<p>Sa théorie traite la gravitation comme un champ physique déployé dans un espace-temps plat, à la manière d'un champ électromagnétique. Elle prédit les mêmes résultats que la relativité générale partout où celle-ci a été testée. Mais l'effondrement gravitationnel y <strong>s'arrête juste au-delà du rayon de Schwarzschild</strong>&nbsp;: ni singularité, ni horizon.</p>

<div class="tei-enclair">
  <span class="tei-enclair-label">En clair</span>
  <p>Une loi de conservation garantit qu'une grandeur — l'énergie, par exemple — ne se crée ni ne se perd, quel que soit l'angle sous lequel on la regarde. Le reproche de Logunov est que dans la relativité générale, l'énergie de la gravitation change de valeur selon le point de vue mathématique choisi. C'est comme si le solde d'un compte dépendait de l'endroit d'où on le lit.</p>
</div>

<h3>La relativité générale pseudo-complexe (Greiner, 2014)</h3>
<p>Walter Greiner, fondateur de la physique des ions lourds, étend les équations d'Einstein en remplaçant les nombres réels par des nombres «&nbsp;pseudo-complexes&nbsp;». Il en sort automatiquement un terme supplémentaire, interprété comme une énergie noire répulsive&nbsp;: plus la matière se concentre, plus elle résiste. L'effondrement s'arrête avant le stade du trou noir et laisse un objet très dense, mais <strong>doté d'une vraie surface</strong>, dont la lumière peut encore s'échapper.</p>
<p>Cette théorie fait deux prédictions distinctes et testables. Le décalage vers le rouge n'y devient jamais infini, contrairement à ce que prédit un horizon. Et des étoiles à neutrons de quatre à six masses solaires y sont stables, là où la relativité générale impose l'effondrement au-delà de deux ou trois. L'observation en 2013 d'une étoile à neutrons de 2,01 masses solaires va dans ce sens sans trancher&nbsp;; une étoile nettement plus massive trancherait.</p>

<p>Ni l'une ni l'autre n'est marginale, et ni l'une ni l'autre n'est établie. La théorie de Logunov a reçu des critiques publiées, notamment de Zel'dovich et Grishchuk, auxquelles il a répondu. Aucune des deux n'a été soumise à un test observationnel qui la distinguerait formellement de la relativité générale dans les régimes extrêmes. C'est exactement ce qui rend la question ouverte au lieu de la trancher.</p>

<div class="tei-fait headquarters">
  <span class="tei-fait-label">FAIT ÉTABLI N°X</span>
  <p>Deux extensions publiées de la relativité générale — la théorie relativiste de la gravitation de Logunov et la relativité générale pseudo-complexe de Greiner — éliminent toutes deux l'horizon des événements et la singularité, tout en restant compatibles avec les observations connues.</p>
</div>
"""

# ── Synthèse : les trois blocs, sans la récapitulation de l'article ─────────
SYNTHESE = """
<h3>Ce qui est solidement établi</h3>
<p>Il existe au centre de nombreuses galaxies, dont la nôtre, des objets très massifs — de millions à milliards de masses solaires — concentrés dans des volumes très petits. C'est une inférence solide, fondée sur des mesures indépendantes et convergentes. Les ondes gravitationnelles existent&nbsp;: leur détection est une mesure instrumentale d'une déformation de l'espace-temps. Et la relativité générale fonctionne remarquablement bien dans les régimes modérés.</p>

<h3>Ce qui reste une inférence</h3>
<p>L'existence d'un horizon des événements n'a jamais été démontrée directement, et par définition elle ne peut pas l'être, puisqu'aucun signal n'en sort. Celle d'une singularité est entièrement théorique&nbsp;: elle repose sur l'extrapolation des équations dans un régime où elles ne peuvent plus être valides. Que les ondes détectées proviennent de la fusion de deux trous noirs plutôt que de deux objets compacts sans horizon est une interprétation — la plus naturelle dans le cadre de la relativité générale, mais une interprétation.</p>

<h3>Ce qui reste ouvert</h3>
<p>La question de la singularité est liée au problème non résolu de la gravitation quantique&nbsp;: toute conclusion définitive demande une théorie que nous n'avons pas. Le paradoxe de l'information est débattu depuis 1974, et celui du «&nbsp;mur de feu&nbsp;», soulevé en 2012, suggère que l'image du trou noir classique est incompatible avec les principes de la physique quantique. Enfin, la distinguabilité observationnelle entre un trou noir et un objet compact alternatif n'est pas acquise&nbsp;; l'Event Horizon Telescope amélioré, Einstein Telescope et LISA pourraient la trancher.</p>

<h3>Ce qu'on peut dire honnêtement</h3>
<p>Nous observons des objets compacts et massifs dont le comportement est remarquablement bien prédit par la relativité générale dans les régimes testables. Savoir s'ils possèdent exactement les caractéristiques que la théorie leur attribue dans ses régimes extrêmes — horizon, singularité, disparition définitive de l'information — reste ouvert.</p>
<p>Le consensus sur les trous noirs n'est ni une conspiration ni une erreur grossière&nbsp;: c'est le résultat d'une longue accumulation de travaux sérieux qui ont, jusqu'ici, résisté aux critiques. Et aucune des objections rapportées ici n'est définitive&nbsp;; les théories alternatives ont leurs propres hypothèses et leurs propres zones d'ombre. Reconnaître cela n'affaiblit pas le dossier&nbsp;: c'est ce qui le rend lisible.</p>
"""

# Paragraphes de redite à retirer, identifiés par un fragment sans ambiguïté.
REDITES = [
    # 6.1 rappelle la distinction posée dans l'avant-propos.
    "Nous avons vu en introduction",
    "Comme nous l'avons posé en avant-propos",
]


def main():
    with open(CH, encoding="utf-8") as f:
        art = json.load(f)
    html = art["htmlBody"]
    avant = len(re.sub(r"<[^>]+>", " ", html).split())

    tete, blocs = decouper(html)
    if len(blocs) != 12:
        sys.exit("12 sections attendues, %d trouvées." % len(blocs))

    # L'avant-propos garde sa figure : c'est elle qui porte la distinction.
    corps = blocs[0][1]
    i = corps.find('<div style="margin:24px auto;max-width:660px">')
    if i < 0:
        sys.exit("Figure de l'avant-propos introuvable.")
    blocs[0] = (blocs[0][0], AVANT_PROPOS + "\n" + corps[i:])

    # Les deux sections d'alternatives n'en font plus qu'une.
    titre_alt = ('<h2 id="tn-alternatives-theoriques"><span class="tei-section-num">05</span>'
                 "Deux alternatives publiées qui éliminent l'horizon</h2>")
    blocs[4:6] = [(titre_alt, ALTERNATIVES)]

    # La synthèse, sans sa récapitulation en quatre points de tout l'article.
    for n, (titre, _) in enumerate(blocs):
        if "tn-synthese" in titre:
            blocs[n] = (titre, SYNTHESE)
            break

    html = tete + "".join(t + c for t, c in blocs)

    for fragment in REDITES:
        for p in re.findall(r"<p>[^<]*%s.*?</p>" % re.escape(fragment), html, re.S):
            html = html.replace(p, "")

    # La numérotation décimale des sous-titres : un seul système par page.
    html = re.sub(r"(<h3[^>]*>)\s*\d+\.\d+\s*", r"\1", html)

    # Renumérotation des sections et des faits établis.
    c = [0]

    def sec(m):
        c[0] += 1
        return '<span class="tei-section-num">%02d</span>' % c[0]

    html = re.sub(r'<span class="tei-section-num">\d+</span>', sec, html)
    f = [0]

    def fait(m):
        f[0] += 1
        return 'tei-fait-label">FAIT ÉTABLI N°%d<' % f[0]

    html = re.sub(r'tei-fait-label">FAIT ÉTABLI N°[^<]*<', fait, html)

    art["htmlBody"] = html
    art["updated"] = "2026-08-31"
    with open(CH, "w", encoding="utf-8") as g:
        json.dump(art, g, ensure_ascii=False, indent=2)
        g.write("\n")

    apres = len(re.sub(r"<[^>]+>", " ", html).split())
    print("%d mots → %d (−%d %%), %d sections, %d faits établis."
          % (avant, apres, round(100 * (avant - apres) / avant), c[0], f[0]))


if __name__ == "__main__":
    main()
