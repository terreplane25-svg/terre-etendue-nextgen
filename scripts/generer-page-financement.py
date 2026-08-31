#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Écrit la page « Financement et indépendance ».

Pourquoi cette page existe
──────────────────────────
Le site déclarait jusqu'ici, en tête de « Standards et méthode », n'avoir
« aucun financement » et « pas de dons sollicités ». La seconde moitié de cette
phrase cesse d'être vraie le jour où un bouton de don apparaît. Une déclaration
d'indépendance qui devient fausse sans que personne ne le dise vaut moins que
pas de déclaration du tout.

Cette page prend donc le relais : elle dit ce que le travail coûte, d'où vient
l'argent, ce qu'il ne peut pas acheter, et elle ouvre un registre des versements
tenu comme le registre des corrections — daté, chiffré, à charge.

Le registre est vide, et il doit l'être : aucun versement n'a été reçu. Un
compteur inventé a déjà été affiché sur ce site, sur la page des projets, et
retiré le 31 août 2026. C'est précisément ce qu'un registre public rend
impossible à répéter sans mentir sciemment.

Les chiffres de la section 01 sont les budgets réels de content/projets/projets.json,
recalculés poste par poste à l'exécution : ils ne sont pas recopiés à la main.
"""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "financement-et-independance"
CIBLE = os.path.join(RACINE, "content", "articles", SLUG + ".json")
PROJETS = os.path.join(RACINE, "content", "projets", "projets.json")

KOFI = "https://ko-fi.com/terreetendue"
DOI = "10.5281/zenodo.22167798"

# Les frais courants sont acquittés personnellement et ne sont pas l'objet de
# la collecte ; on ne les chiffre donc pas ici, faute de pouvoir les vérifier
# depuis le dépôt. Ce qui est chiffré, c'est ce que la collecte financerait.


def budgets():
    """Les campagnes budgétées, avec leur total recalculé poste par poste."""
    with open(PROJETS, encoding="utf-8") as f:
        projets = json.load(f)
    out = []
    for p in projets:
        total = sum(poste["montant"] for poste in p["budget"])
        if total != p["objectif"]:
            sys.exit("%s : les postes font %d €, l'objectif annoncé est %d €."
                     % (p["id"], total, p["objectif"]))
        if p["collecte"] or p["donateurs"]:
            sys.exit("%s : le registre est vide, mais la page des projets "
                     "affiche %s € et %s contributeurs."
                     % (p["id"], p["collecte"], p["donateurs"]))
        out.append((p["titre"], len(p["budget"]), total))
    return out


def h2(num, ident, titre):
    return ('<h2 id="%s"><span class="tei-section-num">%02d</span>%s</h2>\n'
            % (ident, num, titre))


def construire():
    camp = budgets()
    total = sum(c[2] for c in camp)
    lignes = []
    A = lignes.append

    A('<p class="tei-lede">Ce site n\'a jamais reçu un euro. Il peut désormais '
      'en recevoir&nbsp;: cette page dit lesquels, pour quoi, et ce que cet '
      'argent n\'achètera jamais. Le registre des versements ci-dessous est vide, '
      'et il le restera tant qu\'il n\'y aura rien à y écrire.</p>\n')

    # ── 01 ────────────────────────────────────────────────────────────────
    A(h2(1, "ce-que-ca-coute", "Ce que le travail coûte"))
    A("<p>Écrire ne coûte rien d'autre que du temps. L'hébergement et le nom de "
      "domaine sont acquittés personnellement et ne sont pas l'objet de cette "
      "collecte&nbsp;: ils seraient payés de la même manière si personne ne "
      "donnait jamais. Le dépôt du protocole sur Zenodo est gratuit, et le "
      "document est sous licence CC BY.</p>\n")
    A("<p>Ce qui coûte de l'argent, c'est le terrain. Une mesure demande des "
      "instruments, des déplacements, parfois une nuit sur place, et elle doit "
      "être refaite dans des conditions atmosphériques indépendantes — ce qui "
      "multiplie les déplacements plutôt que les instruments. Les trois campagnes "
      "préparées à ce jour sont budgétées poste par poste&nbsp;:</p>\n")
    A('<table class="tei-table">\n<thead><tr><th>campagne</th>'
      '<th>postes</th><th>budget</th></tr></thead>\n<tbody>\n')
    for titre, n, montant in camp:
        A("<tr><td>%s</td><td>%d</td><td>%d&nbsp;€</td></tr>\n"
          % (titre, n, montant))
    A("<tr><td><strong>Total</strong></td><td><strong>%d</strong></td>"
      "<td><strong>%d&nbsp;€</strong></td></tr>\n"
      % (sum(c[1] for c in camp), total))
    A("</tbody>\n</table>\n")
    A('<p><em>Budgets détaillés poste par poste sur la page des campagnes. '
      "Aucun de ces montants ne rémunère le temps passé&nbsp;: ce sont des frais, "
      "et rien d'autre.</em></p>\n")

    # ── 02 ────────────────────────────────────────────────────────────────
    A(h2(2, "d-ou-vient-l-argent", "D'où vient l'argent"))
    A("<p><strong>À ce jour&nbsp;: de nulle part.</strong> Aucun versement n'a "
      "été reçu, d'aucune source. Le registre de la section suivante est vide "
      "pour cette raison, et pour aucune autre.</p>\n")
    A("<p>Ce que ce site n'acceptera pas, quel qu'en soit le montant&nbsp;: "
      "publicité, contenu sponsorisé, lien d'affiliation, abonnement, mur payant, "
      "et tout partenariat — institutionnel, associatif ou confessionnel — qui "
      "assortirait son concours d'une attente sur ce qui est publié.</p>\n")
    A("<p>Ce qu'il accepte&nbsp;: des dons spontanés, sans contrepartie d'aucune "
      "sorte, versés par <a href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">"
      "Ko-fi</a>. La plateforme annonce ne prélever aucune commission sur les "
      "dons&nbsp;; les frais du prestataire de paiement, eux, s'appliquent et "
      "seront portés au registre comme une dépense. Nous n'avons pas vérifié la "
      "première affirmation autrement qu'en la lisant sur le site de la "
      "plateforme, et elle est classée en conséquence dans nos sources.</p>\n"
      % KOFI)

    # ── 03 ────────────────────────────────────────────────────────────────
    A(h2(3, "registre", "Le registre des versements"))
    A("<p>Il est tenu comme le registre des corrections&nbsp;: daté, chiffré, et "
      "à charge. Quatre règles le régissent.</p>\n")
    A("<ol>\n"
      "<li>Tout versement reçu y est inscrit dans les sept jours, avec sa date "
      "et son montant.</li>\n"
      "<li>Toute dépense y est inscrite avec son objet et son justificatif, y "
      "compris les frais de paiement.</li>\n"
      "<li>Le solde est publié. S'il ne tombe pas juste, c'est l'écart qui est "
      "publié, pas un arrondi.</li>\n"
      "<li>Si une campagne financée n'a pas lieu, les versements qui lui étaient "
      "destinés sont remboursés à qui les a faits, ou reversés à une autre "
      "campagne avec l'accord explicite du donateur.</li>\n"
      "</ol>\n")
    A('<div class="tei-data"><strong>État du registre au 31 août 2026</strong>'
      "<br/>Versements reçus&nbsp;: aucun · Total encaissé&nbsp;: 0&nbsp;€ · "
      "Dépenses&nbsp;: 0&nbsp;€ · Solde&nbsp;: 0&nbsp;€<br/>"
      "Ce bloc est la seule chose à mettre à jour quand un versement arrive.</div>\n")
    A("<p>Une précision qui a son importance, et qui n'est pas à notre "
      "avantage&nbsp;: la page des campagnes de ce site a affiché, de juin au "
      "31 août 2026, «&nbsp;175&nbsp;€ collectés · 12 contributeurs&nbsp;» pour "
      "la mesure de pression en altitude. Ce chiffre n'a jamais correspondu à un "
      "versement&nbsp;; il avait été écrit le jour de la création de la page et "
      "n'avait jamais été relu. Il est retiré, et il figure au "
      '<a href="/article/corrections">registre des corrections</a>. C\'est '
      "exactement ce qu'un registre public rend impossible à refaire sans mentir "
      "sciemment&nbsp;: c'est pour cela qu'il existe.</p>\n")

    # ── 04 ────────────────────────────────────────────────────────────────
    A(h2(4, "ce-que-l-argent-n-achete-pas", "Ce que l'argent n'achète pas"))
    A("<p>Un site dont la seule valeur est que ses conclusions ne dépendent pas "
      "de qui les paie doit écrire cette phrase-là sous une forme opposable. "
      "La voici, en cinq règles.</p>\n")
    A("<ol>\n"
      "<li><strong>Aucun accès anticipé.</strong> Un donateur ne voit pas les "
      "données avant leur publication. Personne ne les voit avant leur "
      "publication.</li>\n"
      "<li><strong>Aucune issue promise.</strong> Les résultats sont publiés "
      "quelle que soit l'issue. Le préenregistrement daté rend cette promesse "
      "vérifiable au lieu de la laisser déclarative&nbsp;: les prédictions et "
      "les critères de décision sont déposés avant la première mesure.</li>\n"
      "<li><strong>Aucun donateur cité en appui.</strong> Le nom d'un donateur "
      "n'apparaît jamais au soutien d'une affirmation. Une contribution "
      "financière n'est pas un argument.</li>\n"
      "<li><strong>Les gros versements sont déclarés.</strong> Tout versement "
      "dépassant la moitié du budget d'une campagne est déclaré sur la page de "
      "cette campagne, avec le nom du donateur s'il l'accepte. S'il le refuse, "
      "le versement est refusé — un financement majoritaire anonyme est "
      "exactement ce que cette page existe pour empêcher.</li>\n"
      "<li><strong>Aucune contrepartie.</strong> Pas de paliers, pas de "
      "remerciements gradués, pas d'accès privilégié, pas de vote sur les "
      "sujets traités.</li>\n"
      "</ol>\n")

    # ── 05 ────────────────────────────────────────────────────────────────
    A(h2(5, "travail-commande", "Si un travail est un jour commandé"))
    A("<p><strong>Aucun travail n'a été commandé ni facturé à ce jour</strong>, "
      "et rien n'est proposé à la vente. Il est possible qu'on nous demande un "
      "jour d'écrire un protocole pour un tiers. Les règles se posent avant, "
      "quand elles ne coûtent rien, et non le jour où une somme est sur la "
      "table.</p>\n")
    A("<ol>\n"
      "<li>Le protocole est <strong>publié en entier, gratuitement, sous "
      "CC BY</strong>. Ce qui est payé, c'est le travail — jamais l'exclusivité, "
      "et encore moins la conclusion.</li>\n"
      "<li>Le <strong>commanditaire est nommé en première page</strong> du "
      "document, comme un financement l'est dans une publication.</li>\n"
      "<li>Le <strong>préenregistrement est déposé avant toute donnée</strong>, "
      "avec ses critères de décision et ses issues — donc avant que quiconque, "
      "commanditaire compris, sache ce qui va en sortir.</li>\n"
      "</ol>\n")
    A('<div class="tei-enclair">\n<span class="tei-enclair-label">En clair</span>\n'
      "<p>Avec ces trois règles, un protocole commandé vaut exactement autant "
      "qu'un protocole spontané, et il peut être facturé sans rien fragiliser. "
      "Sans elles, le premier protocole payé rendrait suspects, rétroactivement, "
      "tous ceux qui l'ont précédé.</p>\n</div>\n")

    # ── 06 ────────────────────────────────────────────────────────────────
    A(h2(6, "contribuer", "Contribuer"))
    A("<p>Un don finance du terrain, et rien d'autre. Il n'ouvre aucun droit, "
      "n'attend aucun remerciement public, et ne change pas une ligne de ce qui "
      "sera écrit.</p>\n")
    A('<p style="margin:1.6rem 0"><a href="%s" target="_blank" '
      'rel="noopener noreferrer" style="display:inline-block;padding:14px 28px;'
      'border-radius:8px;background:var(--gold);color:#fff;font-weight:700;'
      'text-decoration:none">Faire un don · Ko-fi</a></p>\n' % KOFI)
    A("<p>Il y a trois autres façons de contribuer, et elles valent davantage "
      "que l'argent&nbsp;:</p>\n")
    A("<ul>\n"
      '<li><strong>Exécuter un protocole.</strong> C\'est ce qui manque le plus. '
      'Voir <a href="/article/participer-aux-campagnes-de-mesure">Participer aux '
      "campagnes de mesure</a>.</li>\n"
      "<li><strong>Signaler une erreur.</strong> Une erreur trouvée chez nous "
      "vaut mieux qu'un don&nbsp;: elle est inscrite au "
      '<a href="/article/corrections">registre des corrections</a>, datée, avec '
      "ce qui était affirmé et ce qui l'a remplacé.</li>\n"
      "<li><strong>Transmettre une observation</strong> avec sa date, sa "
      "position, l'altitude de l'œil et les conditions du jour. Une observation "
      "documentée est une donnée&nbsp;; sans ces quatre choses, ce n'est qu'une "
      "image.</li>\n"
      "</ul>\n")

    # ── Sources ───────────────────────────────────────────────────────────
    A(h2(7, "sources", "Sources"))
    A('<p class="tei-src-legende">Chaque source porte sa classe de vérifiabilité. '
      "Elle ne dit pas si la source est bonne, mais ce qu&#8217;elle permet de "
      "faire&nbsp;: <b>A</b> mesure directe, protocole et instrument connus "
      "&#8212; conclure. <b>B</b> chemin mesuré mais indirect &#8212; borner. "
      "<b>C</b> valeur rapportée, calculée depuis un modèle, ou source primaire "
      "non consultée &#8212; illustrer, jamais conclure. <b>D</b> déclarative, "
      "affirmée sans donnée jointe &#8212; rien. <b>renvoi</b> désigne un de nos "
      "propres articles, qui n&#8217;est pas une source. La grille est détaillée "
      'dans <a href="/article/standards-et-methode">Standards et méthode</a>.</p>\n')
    A("<ol>\n")
    A('<li><span class="tei-grade grade-a">A</span> Terre Etendue Islam, '
      "«&nbsp;Mesure de la dépression de l'horizon marin en fonction de "
      "l'altitude — protocole ouvert et préenregistré (FR/EN)&nbsp;», version 1.9, "
      'déposé le 30 août 2026. DOI&nbsp;: <a href="https://doi.org/%s" '
      'target="_blank" rel="noopener noreferrer">%s</a>. Licence CC BY 4.0. '
      "Document de nous, daté et figé&nbsp;: c'est ce qui rend vérifiable "
      "l'engagement de publier quelle que soit l'issue.</li>\n" % (DOI, DOI))
    A('<li><span class="tei-grade grade-d">D</span> Ko-fi, page de tarification '
      "— absence de commission sur les dons. Affirmation de la plateforme sur "
      "son propre service, sans donnée jointe et non vérifiée par nous. Elle est "
      "citée parce qu'elle engage la plateforme, pas parce qu'elle est "
      "établie.</li>\n")
    A('<li><span class="tei-grade grade-lien">renvoi</span> '
      '<a href="/article/standards-et-methode">Standards et méthode</a> — les '
      "règles générales du site, dont la grille de sourçage et la politique de "
      "correction. La déclaration d'indépendance y a été modifiée le 31 août 2026 "
      "pour tenir compte de cette page.</li>\n")
    A('<li><span class="tei-grade grade-lien">renvoi</span> '
      '<a href="/article/corrections">Registre des corrections</a> — dont '
      "l'entrée du 31 août 2026 sur le compteur de dons retiré.</li>\n")
    A('<li><span class="tei-grade grade-lien">renvoi</span> '
      '<a href="/article/les-protocoles-ce-que-c-est-et-pourquoi">Les protocoles '
      "— ce que c'est et pourquoi</a> — ce que finance le terrain, et pourquoi "
      "une observation seule ne tranche rien.</li>\n")
    A("</ol>\n")
    return "".join(lignes)


def main():
    html = construire()
    art = {
        "title": "Financement et indépendance",
        "description": (
            "D'où vient l'argent, ce qu'il finance, ce qu'il n'achète pas. "
            "Le registre des versements, les cinq règles qui bornent un don, et "
            "celles qui s'appliqueraient à un travail commandé."),
        "date": "2026-08-31",
        "updated": "2026-08-31",
        "author": "Terre Etendue",
        "category": "meta",
        "tags": ["financement", "independance", "transparence", "dons",
                 "conflits-d-interets", "registre"],
        "pinned": False,
        "htmlBody": html,
    }
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("écrit : %s (%d caractères de corps)" % (CIBLE, len(html)))


if __name__ == "__main__":
    main()
