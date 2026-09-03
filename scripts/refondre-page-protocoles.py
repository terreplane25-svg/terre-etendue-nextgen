#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ramène le site à un seul protocole, et donne à la page sa raison d'être.

Ce que le script fait
─────────────────────
1. La page « Les protocoles » perd les sections propres au protocole de
   l'horizon — ce qu'il mesure, pourquoi la question est décidable, l'ordre de
   ses opérations — et gagne une section « Le protocole » qui, pour chaque
   document, énonce d'abord POURQUOI il existe, puis ce qu'il mesure, puis ce
   qu'il ne permet pas de conclure, puis le téléchargement. Le gabarit est
   explicite dans le texte, de façon qu'un second protocole s'ajoute sans
   inventer une nouvelle forme.
2. La page d'accueil présente le même document.
3. public/protocoles/ ne sert plus que ce document.
4. L'article « Monter l'expérience des trois mires » est retiré, ainsi que ses
   entrées de registre et les quinze renvois qui le visaient.

Ce que le script ne touche pas
──────────────────────────────
content/protocoles/depot/ et les sources HTML des protocoles retirés. Le dépôt
Zenodo du protocole de l'horizon reste ce qu'il est : un enregistrement daté,
que le retrait des fichiers du site ne rétracte pas. Ce qui disparaît, ce sont
les copies servies par le site, et les liens directs vers elles.

Chaque ancre est comptée avant écriture. Une ancre vue autrement qu'une fois
arrête tout sans rien modifier.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(RACINE, "content", "articles")
PAGE = os.path.join(ART, "les-protocoles-ce-que-c-est-et-pourquoi.json")
ACCUEIL = os.path.join(RACINE, "src", "app", "HomeClient.tsx")
PUBLIC = os.path.join(RACINE, "public", "protocoles")
PDF_SOURCE = os.path.join(RACINE, "content", "protocoles", "pdf",
                          "Protocole-visibilite-cible-eloignee.pdf")
PDF_NOM = "Protocole-visibilite-cible-eloignee.pdf"
LIEN = "/protocoles/" + PDF_NOM
SLUG_MIRES = "monter-l-experience-des-trois-mires"


def un(texte, vieux, neuf, etiquette):
    n = texte.count(vieux)
    if n != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1." % (etiquette, n))
    return texte.replace(vieux, neuf)


def charger(slug):
    with open(os.path.join(ART, slug + ".json"), encoding="utf-8") as f:
        return json.load(f)


def ecrire(slug, data):
    with open(os.path.join(ART, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ─────────────────────────────────────────────────────────────────────────────
# La nouvelle section « Le protocole »
# ─────────────────────────────────────────────────────────────────────────────
SECTION_PROTOCOLE = '''<h2 id="le-protocole"><span class="tei-section-num">04</span>Le protocole</h2>
<p>Un protocole n&#8217;est pas un mode d&#8217;emploi. C&#8217;est un engagement pris avant de regarder&#160;: voici ce que je vais mesurer, voici ce que chaque mod&#232;le pr&#233;dit, voici l&#8217;&#233;cart &#224; partir duquel je dirai que &#231;a ne colle pas. Chaque document que nous publions ici s&#8217;ouvre donc sur la m&#234;me chose &#8212; <strong>pourquoi il existe</strong> &#8212; avant de dire ce qu&#8217;il mesure et ce qu&#8217;il ne permet pas de conclure.</p>

<h3>Portion visible d&#8217;une cible &#233;loign&#233;e au-dessus de la mer</h3>

<p><strong>Pourquoi ce protocole existe.</strong> La question qu&#8217;on entend partout est mal pos&#233;e. &#171;&#160;Voit-on encore le b&#226;timent &#224; cette distance&#160;?&#160;&#187; appelle une r&#233;ponse par oui ou par non, et une r&#233;ponse par oui ou par non se laisse expliquer par trop de causes&#160;: la brume, la r&#233;solution de l&#8217;objectif, le contraste, l&#8217;heure, la patience de celui qui regarde. Deux personnes de bonne foi peuvent regarder la m&#234;me photographie et n&#8217;en tirer rien de commun.</p>
<p>Il existe pourtant une grandeur que l&#8217;image contient r&#233;ellement et qui, elle, se mesure&#160;: <strong>la fraction de la hauteur de la cible qui reste visible</strong>. Elle est continue, born&#233;e entre z&#233;ro et un, et les mod&#232;les g&#233;om&#233;triques en concurrence n&#8217;en pr&#233;disent pas la m&#234;me valeur. C&#8217;est la seule raison d&#8217;&#234;tre de ce document&#160;: remplacer une alternative par une mesure.</p>
<p>La deuxi&#232;me raison tient &#224; ce qui se passe d&#8217;habitude apr&#232;s coup. Quand l&#8217;observation ne correspond pas &#224; l&#8217;attente, on invoque la r&#233;fraction&#160;; quand elle correspond, on n&#8217;en parle pas. Le protocole ferme cette porte&#160;: l&#8217;intervalle de r&#233;fraction admis, le seuil &#224; partir duquel un &#233;cart compte, et les crit&#232;res qui &#233;cartent une image sont fix&#233;s et dat&#233;s <em>avant</em> que les images soient vues. Dans les deux sens.</p>

<div class="tei-fait experiences">
<span class="tei-fait-label">CE QUE L&#8217;EXP&#201;RIENCE MESURE</span>
<p>La fraction visible d&#8217;une cible dont la hauteur, l&#8217;altitude de base et la position sont &#233;tablies par des sources ind&#233;pendantes de la photographie &#8212; fiche d&#8217;ouvrage, plan cot&#233;, relev&#233; g&#233;od&#233;sique, registre horodat&#233;. Cette fraction mesur&#233;e est confront&#233;e &#224; celle que pr&#233;dit chaque mod&#232;le d&#233;pos&#233;, avec l&#8217;enveloppe d&#8217;incertitude que produisent la g&#233;od&#233;sie et l&#8217;atmosph&#232;re.</p>
</div>

<p><strong>Ce qu&#8217;il ne permet pas de conclure.</strong> Il ne mesure pas le rayon de la Terre. Il ne d&#233;montre aucun mod&#232;le. Une conclusion d&#8217;incompatibilit&#233; porterait sur le couple g&#233;om&#233;trie-propagation pris ensemble, jamais sur une seule de ses deux moiti&#233;s. Et le verdict le plus fr&#233;quent, quand les donn&#233;es atmosph&#233;riques manquent, est <em>ind&#233;termin&#233;</em>&#160;: ni pour, ni contre.</p>

<p><a href="''' + LIEN + '''"><strong>T&#233;l&#233;charger le protocole</strong></a> &#8212; 36 pages, fran&#231;ais, PDF. Trente-cinq rubriques&#160;: fondement th&#233;orique, &#233;quations compl&#232;tes, exemple num&#233;rique v&#233;rifi&#233; par deux voies ind&#233;pendantes, six r&#233;gimes de r&#233;fraction, g&#233;od&#233;sie, mat&#233;riel, validation des images, analyse en aveugle, r&#233;solution angulaire, incertitudes, sensibilit&#233;, contr&#244;les, r&#233;plication, pr&#233;-enregistrement, crit&#232;res de d&#233;cision, audit critique, checklist de terrain, fiche d&#8217;observation, structure d&#8217;archivage et bibliographie dont le statut de v&#233;rification est d&#233;clar&#233; entr&#233;e par entr&#233;e.</p>

<div class="tei-fait experiences">
<span class="tei-fait-label">TROIS CHOSES QUI NE SE N&#201;GOCIENT PAS</span>
<p>Le <strong>seuil</strong> &#224; partir duquel un &#233;cart compte est d&#233;pos&#233; et dat&#233; avant que les images soient vues. La conclusion doit tenir sur <strong>toute l&#8217;enveloppe d&#8217;incertitude</strong>&#160;: si une seule combinaison admissible des param&#232;tres r&#233;concilie l&#8217;observation et la pr&#233;diction, le mod&#232;le n&#8217;est pas r&#233;fut&#233;. Et <strong>aucun verdict n&#8217;est certifi&#233; par un seul analyste</strong> &#8212; trois mesures en aveugle, toute divergence rendant le r&#233;sultat ind&#233;termin&#233;.</p>
</div>

<p>Un grossissement fort est autoris&#233;, y compris num&#233;rique&#160;: il ne change ni la distance, ni la trajectoire des rayons, ni ce qu&#8217;une surface interpose. Ce qui est exig&#233;, c&#8217;est de documenter la cha&#238;ne de traitement et de conserver le fichier d&#8217;origine.</p>

<p><em>Les autres documents que nous avons publi&#233;s ont &#233;t&#233; retir&#233;s. Ils avaient chacun leur forme, leur vocabulaire et leur niveau d&#8217;exigence, et cette h&#233;t&#233;rog&#233;n&#233;it&#233; est exactement ce qu&#8217;un lecteur ne devrait pas avoir &#224; d&#233;m&#234;ler. Ceux qui reviendront reviendront sous la forme ci-dessus.</em></p>
'''


def refondre_page():
    data = charger("les-protocoles-ce-que-c-est-et-pourquoi")
    h = data["htmlBody"]

    def section(numero):
        m = re.search(r'<h2 id="[^"]+"><span class="tei-section-num">%s</span>'
                      r'[^<]+</h2>' % numero, h)
        if not m:
            sys.exit("section %s introuvable" % numero)
        fin = h.find('<h2 ', m.end())
        return h[m.start(): fin if fin > 0 else len(h)]

    # Les sections propres au protocole de l'horizon s'en vont avec lui.
    for numero, etiquette in (("03", "ce que mesure le protocole de l'horizon"),
                              ("04", "pourquoi la question est décidable"),
                              ("05", "l'ordre des opérations"),
                              ("07", "les protocoles")):
        h = un(h, section(numero), "", "section " + etiquette)

    # « Ce qu'un protocole ne fait pas » devient la section 03, et perd sa
    # phrase sur un protocole qui n'est plus publié.
    h = un(h,
           '<h2 id="ce-quun-protocole-ne-fait-pas"><span class="tei-section-num">06</span>',
           '<h2 id="ce-quun-protocole-ne-fait-pas"><span class="tei-section-num">03</span>',
           "numéro de la section « ce qu'un protocole ne fait pas »")
    h = un(h,
           "Le protocole de l'horizon détermine si δ croît comme √h ou reste "
           "nul&nbsp;; c'est beaucoup, ce n'est pas tout.",
           "Le protocole publié ici mesure quelle fraction d'une cible reste "
           "visible et la confronte à ce que chaque modèle prédit&nbsp;; c'est "
           "beaucoup, ce n'est pas tout.",
           "phrase sur le protocole de l'horizon")

    # La nouvelle section 04, insérée avant les sources.
    m = re.search(r'<h2 id="[^"]+"><span class="tei-section-num">08</span>'
                  r'[^<]*Sources</h2>', h)
    if not m:
        sys.exit("section Sources introuvable")
    h = h[:m.start()] + SECTION_PROTOCOLE + "\n" + h[m.start():]
    h = un(h, '<span class="tei-section-num">08</span>',
           '<span class="tei-section-num">05</span>', "numéro des sources")

    h = re.sub(r"\n{3,}", "\n\n", h).strip() + "\n"
    data["htmlBody"] = h
    data["description"] = (
        "Un protocole n'est pas un mode d'emploi : c'est un engagement pris "
        "avant de regarder. Les six règles que nous nous imposons, ce qu'un "
        "protocole ne fait pas, et le document publié — la portion visible "
        "d'une cible éloignée au-dessus de la mer, avec sa raison d'être.")
    ecrire("les-protocoles-ce-que-c-est-et-pourquoi", data)
    return len(h)


# ─────────────────────────────────────────────────────────────────────────────
# Les quinze renvois vers l'article retiré
# ─────────────────────────────────────────────────────────────────────────────
A = '<a href="/article/%s">' % SLUG_MIRES
P = '<a href="/article/les-protocoles-ce-que-c-est-et-pourquoi">'

RENVOIS = {
    "cartes-routes-boussoles-et-le-mystere-antarctique": [
        ("C'est précisément ce que notre " + A + "protocole des trois "
         "mires</a> cherche à corriger, en lisant un exposant plutôt qu'une "
         "amplitude.",
         "C'est précisément ce que notre " + P + "protocole d'observation "
         "photographique</a> cherche à corriger, en mesurant une fraction "
         "plutôt qu'une amplitude, et en bornant la réfraction au lieu de la "
         "laisser libre."),
    ],
    "glossaire": [
        (" Voir " + A + "Monter l'expérience des trois mires</a>.</li>",
         "</li>"),
    ],
    "index-thematique": [
        ('<li>' + A + "Monter l'expérience des trois mires</a> "
         '<span class="tei-index-pilier">Expériences</span> '
         '<span class="tei-index-tags">courbure · eau · fleche · '
         'reproductible</span></li>', ""),
        ('<li>' + A + "Monter l'expérience des trois mires</a> "
         '<span class="tei-index-pilier">Expériences</span> '
         '<span class="tei-index-tags">pre-enregistrement · protocole · '
         'puits-de-tranquillisation · refraction</span></li>', ""),
    ],
    "mesurer-la-courbure-sur-l-eau-cinq-campagnes": [
        ("<p><strong>Si vous voulez la faire plutôt que la lire :</strong> le "
         "mode d'emploi complet — matériel, fabrication, protocole pas à pas — "
         "est dans " + A + "Monter l'expérience des trois mires</a>. Le "
         "présent article donne l'analyse ; celui-là donne les gestes.</p>",
         "<p><strong>Si vous voulez mesurer plutôt que lire :</strong> le "
         "document publié est " + P + "le protocole d'observation "
         "photographique</a>, qui mesure la fraction visible d'une cible "
         "éloignée. Le présent article donne l'analyse des campagnes "
         "passées ; celui-là donne la méthode.</p>"),
        ("<p>Sa fabrication, sa coupe détaillée et le reste du mode d'emploi — "
         "matériel, montage, feuille de relevé — sont dans l'article "
         "compagnon : " + A + "Monter l'expérience des trois mires</a>.</p>",
         ""),
        ('<li><span class="tei-grade grade-lien">renvoi</span> Article lié : '
         + A + "Monter l'expérience des trois mires</a> — le mode d'emploi : "
         "matériel, fabrication du puits, protocole et feuille de "
         "relevé.</li>", ""),
    ],
    "ou-est-allah-le-uluww-et-la-forme-du-monde": [
        (A + "protocoles expérimentaux</a>", P + "protocoles expérimentaux</a>"),
    ],
    "participer-aux-campagnes-de-mesure": [
        ("Le mode d'emploi est là&nbsp;: " + A + "Monter l'expérience des "
         "trois mires</a>.",
         "La méthode publiée est " + P + "le protocole d'observation "
         "photographique</a>."),
        ('<li><span class="tei-grade grade-lien">renvoi</span> ' + A
         + "Monter l'expérience des trois mires</a> — le mode d'emploi "
         "complet.</li>", ""),
    ],
    "un-traite-ottoman-contre-la-sphericite-1314h": [
        ("et c'est la raison pour laquelle notre " + A + "protocole des trois "
         "mires</a> est construit pour ne dépendre d'aucune valeur de rayon "
         "terrestre supposée.",
         "et c'est la raison pour laquelle notre " + P + "protocole "
         "d'observation photographique</a> pose explicitement la valeur de "
         "rayon qu'il teste, au lieu de s'appuyer sur elle sans le dire."),
        ("mais sur l'" + A + "exposant de la loi hauteur-distance</a>. La "
         "réfraction change l'amplitude de l'effet ; elle ne change pas la "
         "puissance de <em>d</em>.",
         "mais sur une grandeur continue, la " + P + "fraction visible de la "
         "cible</a>. La réfraction en déplace la valeur prédite ; le protocole "
         "en borne l'intervalle avant l'observation plutôt que de l'ajuster "
         "après."),
        (" · " + A + "Monter l'expérience des trois mires</a>", ""),
    ],
}


def nettoyer_renvois():
    total = 0
    for slug, paires in RENVOIS.items():
        data = charger(slug)
        h = data["htmlBody"]
        for vieux, neuf in paires:
            n = h.count(vieux)
            if n < 1:
                sys.exit("renvoi introuvable dans %s :\n  %r" % (slug, vieux[:120]))
            h = h.replace(vieux, neuf)
            total += n
        reste = h.count(SLUG_MIRES)
        if reste:
            sys.exit("%s : %d renvoi(s) non traité(s)" % (slug, reste))
        h = re.sub(r"\n{3,}", "\n\n", h)
        data["htmlBody"] = h
        ecrire(slug, data)
    return total


def retirer_article():
    chemin = os.path.join(ART, SLUG_MIRES + ".json")
    if os.path.exists(chemin):
        os.remove(chemin)

    # Registres : image de couverture, notice de nature, nœud et arêtes du graphe.
    img = os.path.join(RACINE, "src", "lib", "article-images.ts")
    s = open(img, encoding="utf-8").read()
    s = re.sub(r'\n *"%s": `[^`]*`,' % re.escape(SLUG_MIRES), "", s, count=1)
    open(img, "w", encoding="utf-8").write(s)

    nat = os.path.join(RACINE, "src", "lib", "nature-articles.ts")
    s = open(nat, encoding="utf-8").read()
    i = s.find("  '%s': {" % SLUG_MIRES)
    if i < 0:
        sys.exit("notice de nature introuvable")
    j = s.find("\n  },\n", i)
    s = s[:i] + s[j + len("\n  },\n"):]
    open(nat, "w", encoding="utf-8").write(s)

    nex = os.path.join(RACINE, "src", "lib", "nexus-data.ts")
    s = open(nex, encoding="utf-8").read()
    marque = "/* @@ */"
    s = re.sub(r'\{[^{}]*"(?:id|source|target)"[^{}]*\}',
               lambda m: marque if SLUG_MIRES in m.group(0) else m.group(0), s)
    s = re.sub(r',\s*' + re.escape(marque), "", s)
    s = re.sub(re.escape(marque) + r',\s*', "", s)
    s = s.replace(marque, "")
    open(nex, "w", encoding="utf-8").write(s)
    return sum(SLUG_MIRES in open(os.path.join(RACINE, p), encoding="utf-8").read()
               for p in ("src/lib/article-images.ts", "src/lib/nature-articles.ts",
                         "src/lib/nexus-data.ts"))


# ─────────────────────────────────────────────────────────────────────────────
# Page d'accueil et fichiers servis
# ─────────────────────────────────────────────────────────────────────────────
def refondre_accueil():
    s = open(ACCUEIL, encoding="utf-8").read()
    s = un(s, "Protocole de recevabilité — version 3.0",
           "Protocole expérimental — version 1.0", "bandeau")
    s = un(s,
           "Une photographie ne prouve rien tant qu’on ne peut pas dire d’où elle vient",
           "Quelle part de l’objet devrait être visible, et quelle part l’est vraiment",
           "titre")
    i = s.find("          <p style={{ fontSize: 17, color: '#a8b8cc'")
    j = s.find("          <div style={{ display: 'flex', gap: 14", i)
    if i < 0 or j < 0:
        sys.exit("corps du bloc protocole introuvable")
    s = s[:i] + """          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 18px' }}>
            «&nbsp;Voit-on encore le bâtiment à cette distance&nbsp;?&nbsp;» appelle une réponse par oui
            ou par non, et une réponse par oui ou par non se laisse expliquer par la brume, l’objectif,
            le contraste ou l’heure. La question devient mesurable si on la pose autrement&nbsp;:
            <strong style={{ color: '#F4F8FC' }}> quelle fraction de la hauteur de la cible reste
            visible</strong>, et que prédit chaque modèle géométrique pour cette même fraction&nbsp;?
          </p>
          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 34px' }}>
            Le seuil à partir duquel un écart compte est déposé et daté avant que les images soient
            vues. La conclusion doit tenir sur toute l’enveloppe d’incertitude. Et aucun verdict n’est
            certifié par un seul analyste. La conclusion prend trois valeurs&nbsp;: compatible,
            incompatible, indéterminé — et l’indéterminé n’est une preuve ni pour ni contre.
          </p>
""" + s[j:]
    s = un(s, '<a href="/protocoles/Protocole-photographie-objet-eloigne.pdf"',
           '<a href="%s"' % LIEN, "lien du PDF")
    s = un(s, "Télécharger le PDF · bilingue", "Télécharger le PDF · 36 pages",
           "libellé du bouton")
    i = s.find("          <p style={{ fontSize: 13.5, color: '#6f829c'")
    j = s.find("        </div>\n      </div>", i)
    if i < 0 or j < 0:
        sys.exit("pied du bloc protocole introuvable")
    s = s[:i] + """          <p style={{ fontSize: 13.5, color: '#6f829c', lineHeight: 1.65, marginTop: 26, maxWidth: 760 }}>
            Version 1.0, 36 pages, français. Trente-cinq rubriques, de la géométrie aux critères de
            décision, avec l’audit critique du protocole par lui-même et une bibliographie dont le
            statut de vérification est déclaré entrée par entrée. Licence CC BY 4.0.
          </p>
""" + s[j:]
    open(ACCUEIL, "w", encoding="utf-8").write(s)


def nettoyer_public():
    retires = []
    if not os.path.exists(PDF_SOURCE):
        sys.exit("PDF absent : %s" % PDF_SOURCE)
    os.makedirs(PUBLIC, exist_ok=True)
    import shutil
    shutil.copy2(PDF_SOURCE, os.path.join(PUBLIC, PDF_NOM))
    for nom in sorted(os.listdir(PUBLIC)):
        if nom != PDF_NOM and nom.lower().endswith(".pdf"):
            os.remove(os.path.join(PUBLIC, nom))
            retires.append(nom)
    return retires


def main():
    taille = refondre_page()
    renvois = nettoyer_renvois()
    restes = retirer_article()
    refondre_accueil()
    retires = nettoyer_public()

    print("Page des protocoles : %d caractères, section « Le protocole » "
          "avec sa raison d'être" % taille)
    print("Renvois traités     : %d dans %d articles"
          % (renvois, len(RENVOIS)))
    print("Registres résiduels : %d (attendu 0)" % restes)
    print("Accueil             : bloc remplacé")
    print("PDF retirés de public/protocoles/ :")
    for n in retires:
        print("  - %s" % n)
    print("PDF servi : %s" % PDF_NOM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
