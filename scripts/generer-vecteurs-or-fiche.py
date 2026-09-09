#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or de la fiche protocole terrain — épinglent le port au paquet Python.

La fiche est presque entièrement du TEXTE, et c'est ce qui la rend fragile : une
apostrophe droite devenue typographique, une coupure de ligne d'un mot plus
loin, un « du » redevenu « de le » ne cassent rien, ne lèvent rien, et
s'impriment. Ces vecteurs comparent donc le rendu caractère par caractère, pas
seulement la structure.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie ses propres cas. Deux propriétés valent tout le reste :

  · la PRÉDICTION ne figure que dans le bloc sous scellé. C'est la raison
    d'être de la fiche, et un cas qui ne la vérifierait plus passerait
    silencieusement ;
  · le MILIEU ne déplace aucun chiffre. Trois milieux dont les blocs de dépôt
    diffèreraient signaleraient un calcul fantôme fait dans la fiche.

    python3 scripts/generer-vecteurs-or-fiche.py
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_A = os.path.join(RACINE, "outils", "outil-A-visee-optique")
CIBLE = os.path.join(RACINE, "src", "lib", "visee-optique", "vecteurs-or-fiche.json")

sys.path.insert(0, PAQUET_A)
try:
    import visee_optique  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from visee_optique.fiche_terrain import (  # noqa: E402
    CHAMPS_ECARTES,
    LARGEUR_TXT,
    MILIEUX,
    PIXELS_MIN_ECART,
    PREFIXE_REFERENCE_ATTENDU,
    _replier,
    construire_fiche,
    nom_fichier,
    rendre_txt,
)
from visee_optique.simulation import (  # noqa: E402
    format_k,
    format_metres,
    format_pourcent,
    juger,
)

#: Des valeurs où l'arrondi se joue, épinglées à part.
#:
#: Le « %.*f » du Python arrondit les égalités DEMI VERS LE PAIR ; le `toFixed`
#: et le `toLocaleString` du navigateur les arrondissent à l'écart de zéro.
#: 1,25 devenait donc 1,2 dans le paquet et 1,3 à l'écran — sur le seuil en
#: mètres, affiché ET imprimé sur la fiche. C'est ce vérificateur qui l'a
#: trouvé ; à l'œil, les deux valeurs sont plausibles.
#:
#: Les égalités EXACTES (0,25 ; 1,25 ; 0,125) sont mêlées à des quasi-égalités
#: (1,35 ; 1,45 ; 1,85) qui n'en sont pas : sans les secondes, un port qui
#: traiterait toute décimale finissant par 5 comme une égalité passerait.
ARRONDIS = [
    0.0, -0.0, 0.25, 0.75, 1.25, 1.75, 2.25, 1.35, 1.45, 1.85, 1.55, 1.65,
    0.125, 0.375, 12.5 * 0.1, 2.5 * 0.1, -1.25, -0.04, 9.95, 99.95,
    0.05, 1234.5, 1e-9, 40.25, 110.0 * 0.1,
]

# L'horodatage est FIXE : la fiche ne lit jamais l'horloge, et des vecteurs
# horodatés au moment de leur génération changeraient à chaque exécution.
HORODATAGE = "2026-09-09T08:14:00Z"

BASE = dict(
    horodatage=HORODATAGE,
    obs_latitude=50.94642, obs_longitude=1.75305, obs_libelle=None,
    cible_latitude=51.13152, cible_longitude=1.338825,
    cible_libelle="Falaises de Douvres",
    distance_m=35418.0, azimut_deg=302.4,
    hauteur_observateur_m=2.0, hauteur_cible_m=110.0,
    masquee_enveloppe_min_m=38.1, masquee_enveloppe_max_m=44.9,
    k_employe=0.13, k_personnalise=False,
)


def cas(nom, **kw):
    p = dict(BASE)
    masquee = kw.pop("masquee", 40.2)
    p.update(kw)
    p["verdict"] = juger(masquee, p["hauteur_cible_m"])
    return (nom, p)


CAS = [
    cas("mer, visée discriminante", milieu="mer"),
    cas("lac, visée discriminante", milieu="lac"),
    cas("terre, visée discriminante", milieu="terre"),
    # Les cas suivants existent parce que, sans eux, plusieurs ruptures
    # délibérées du port ne changeraient rien au rendu. Chacun isole UNE
    # dimension que les autres ne discriminent pas.
    cas("mer, visée non discriminante", milieu="mer", masquee=1.0),
    cas("mer, cible entièrement sous l'horizon", milieu="mer", masquee=800.0),
    cas("mer, k déclaré par l'analyste", milieu="mer",
        k_employe=0.25, k_personnalise=True),
    cas("lac, sans libellé de cible", milieu="lac", cible_libelle=None),
    cas("mer, observateur libellé", milieu="mer",
        obs_libelle="Cap Blanc-Nez, plateforme haute"),
    # Une occultation nulle : l'exigence de cadrage venant du seuil, elle doit
    # rester formulable. La version précédente divisait par la fraction.
    cas("terre, occultation nulle", milieu="terre", masquee=0.0),
    # Une cible courte et une visée longue : les chiffres changent d'ordre de
    # grandeur, ce qui éprouve les formateurs autrement que le cas de base.
    # Cible de 12,5 m : le seuil vaut 1,25 m, une égalité EXACTE. C'est ce cas
    # qui a révélé que le port arrondissait dans l'autre sens.
    cas("lac, cible courte sur visée longue", milieu="lac",
        distance_m=128450.0, hauteur_cible_m=12.5, masquee=980.0,
        masquee_enveloppe_min_m=910.4, masquee_enveloppe_max_m=1100.7),
    # k = 0,125 : une égalité exacte sur DEUX décimales, que le cas précédent
    # ne couvre pas.
    cas("mer, k déclaré sur une égalité d'arrondi", milieu="mer",
        k_employe=0.125, k_personnalise=True),
]


def champ_en_dict(c):
    return {
        "libelle": c.libelle, "unite": c.unite,
        "pourquoi": c.pourquoi, "obligatoire": c.obligatoire,
    }


def fiche_en_dict(f, distance_m):
    return {
        "milieu": f.milieu,
        "milieu_nom": f.milieu_nom,
        "reference_verticale": f.reference_verticale,
        "titre": f.titre,
        "sous_titre": f.sous_titre,
        "horodatage": f.horodatage,
        "discriminante": f.discriminante,
        "nom_fichier": nom_fichier(f, distance_m),
        "champs_ecartes": [list(x) for x in f.champs_ecartes],
        "sections": [
            {
                "numero": s.numero,
                "titre": s.titre,
                "releves": [list(x) for x in s.releves],
                "champs": [champ_en_dict(c) for c in s.champs],
                "consignes": list(s.consignes),
                "reserves": list(s.reserves),
                "sous_scelle": s.sous_scelle,
            }
            for s in f.sections
        ],
        # Le rendu complet, caractère par caractère. C'est lui qui attrape une
        # apostrophe, une coupure de ligne ou une contraction qui divergent.
        "txt": rendre_txt(f),
    }


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "visee_optique.fiche_terrain (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "constantes": {
            "pixels_min_ecart": PIXELS_MIN_ECART,
            "largeur_txt": LARGEUR_TXT,
            "prefixe_reference_attendu": PREFIXE_REFERENCE_ATTENDU,
            "milieux": {k: dict(d) for k, d in MILIEUX.items()},
            "champs_ecartes": [list(x) for x in CHAMPS_ECARTES],
        },
        # Le replieur est épinglé À PART : c'est lui qui décide de toutes les
        # coupures de ligne, et une divergence d'un seul mot y déplacerait tout
        # le reste du document.
        "replis": [
            {"texte": t, "largeur": l, "premier": p, "suite": s,
             "lignes": _replier(t, l, p, s)}
            for t, l, p, s in [
                ("un deux trois quatre cinq six sept huit neuf dix", 20, "  * ", "    "),
                ("un deux trois quatre cinq six sept huit neuf dix", 20, "  * ", None),
                ("court " + "A" * 40 + " fin", 20, "  ", None),
                # Le mot trop long EN PREMIÈRE POSITION. Sans ce cas, retirer
                # la garde « ou la ligne courante est vide » ne changeait rien :
                # le mot long ne commençait jamais une ligne, et la rupture
                # survivait au vérificateur.
                ("A" * 40 + " fin", 20, "  ", None),
                ("B" * 30, 12, "  · ", "    "),
                ("", 20, "  · ", "    "),
                ("mot", 3, "", None),
                ("  espaces    multiples   ici  ", 20, "  ", None),
                ("Une visée à 35,42 km — l'écart fait 3,90 minutes d'arc.", 30, "  1. ", "     "),
            ]
        ],
        # La convention d'arrondi, épinglée sur des valeurs choisies. Sans
        # cela, un port qui emploierait `toFixed` passerait tant qu'aucun cas
        # de fiche ne tomberait sur une égalité exacte — ce qui a été le cas
        # jusqu'à ce qu'une cible de 12,5 m en produise une.
        "arrondis": [
            {"valeur": x, "metres": format_metres(x),
             "pourcent": format_pourcent(x), "k": format_k(x)}
            for x in ARRONDIS
        ],
        "cas": [],
    }

    for nom, p in CAS:
        f = construire_fiche(milieu=p["milieu"], **{
            k: x for k, x in p.items() if k != "milieu"})
        v["cas"].append({
            "nom": nom,
            "entree": {k: x for k, x in p.items() if k != "verdict"},
            "verdict": {
                "discriminante": p["verdict"].discriminante,
                "motif": p["verdict"].motif,
                "hauteur_masquee_base_m": p["verdict"].hauteur_masquee_base_m,
                "fraction_masquee_base": p["verdict"].fraction_masquee_base,
                "hauteur_masquee_plat_m": p["verdict"].hauteur_masquee_plat_m,
                "ecart_entre_modeles_m": p["verdict"].ecart_entre_modeles_m,
                "seuil_applique": p["verdict"].seuil_applique,
            },
            "fiche": fiche_en_dict(f, p["distance_m"]),
        })

    controle(v)

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d cas, %d replis" % (len(v["cas"]), len(v["replis"])))
    return 0


def controle(v):
    """Revérifie que les vecteurs épinglent bien ce qu'ils prétendent épingler."""
    par_nom = {c["nom"]: c for c in v["cas"]}

    # 1. La propriété centrale : la prédiction ne figure que sous scellé.
    #
    # La recherche est DÉLIMITÉE, pas une simple sous-chaîne : « 0,0 » se
    # trouve dans « 110,0 », et une occultation nulle faisait échouer le
    # contrôle sur la hauteur de la cible. Un contrôle qui crie sur un cas sain
    # finit par être désactivé, ce qui est pire que pas de contrôle.
    for c in v["cas"]:
        f = c["fiche"]
        masquee = ("%.1f" % c["verdict"]["hauteur_masquee_base_m"]).replace(".", ",")
        motif = re.compile(r"(?<![0-9,])%s(?![0-9])" % re.escape(masquee))
        for s in f["sections"]:
            if s["sous_scelle"]:
                continue
            texte = json.dumps(s, ensure_ascii=False)
            assert not motif.search(texte), (
                "la hauteur masquée (%s) apparaît dans le bloc %s de « %s » : "
                "l'analyse en aveugle est perdue" % (masquee, s["numero"], c["nom"])
            )
        scelle = [s for s in f["sections"] if s["sous_scelle"]]
        assert len(scelle) == 1, c["nom"]
        assert scelle[0] is f["sections"][-1], (
            "le bloc sous scellé n'est pas le dernier dans « %s »" % c["nom"])
        assert motif.search(json.dumps(scelle[0], ensure_ascii=False)), c["nom"]

    # 2. Le milieu ne déplace aucun chiffre : les trois blocs de dépôt des
    #    visées discriminantes de base doivent être identiques.
    depots = {
        m: json.dumps(par_nom["%s, visée discriminante" % m]["fiche"]["sections"][-1],
                      ensure_ascii=False)
        for m in ("mer", "lac", "terre")
    }
    assert len(set(depots.values())) == 1, (
        "le bloc de prédiction dépend du milieu : un calcul se fait dans la fiche"
    )

    # 3. Les trois milieux diffèrent réellement ailleurs. Sans ce contrôle, un
    #    port qui ignorerait le milieu passerait le point 2 sans effort.
    premiers = {m: json.dumps(par_nom["%s, visée discriminante" % m]["fiche"]["sections"][0],
                              ensure_ascii=False) for m in ("mer", "lac", "terre")}
    assert len(set(premiers.values())) == 3, (
        "deux milieux rendent le même premier bloc : le cas ne discrimine rien")

    # 4. Les contractions du niveau de référence : « au-dessus de le niveau »
    #    est une faute, et elle s'imprime. Le contrôle vise le PRÉFIXE et non
    #    « de le » tout court — « on lui a dit de le chercher » est correct, et
    #    un contrôle qui crie dessus finit par être désactivé.
    prefixe = v["constantes"]["prefixe_reference_attendu"]
    for c in v["cas"]:
        t = c["fiche"]["txt"]
        for faute in ("de le " + prefixe, "à le " + prefixe):
            assert faute not in t, (c["nom"], faute)

    # 5. Aucune ligne ne dépasse la largeur, dans aucun cas.
    for c in v["cas"]:
        trop = [l for l in c["fiche"]["txt"].splitlines()
                if len(l) > v["constantes"]["largeur_txt"]]
        assert not trop, (c["nom"], trop[:2])

    # 6. L'exigence de cadrage est la MÊME partout : elle vient du seuil, pas
    #    du résultat. Si elle variait, elle porterait de l'information sur le
    #    résultat et fuiterait hors du scellé.
    pixels = set()
    for c in v["cas"]:
        px = [ch["pourquoi"] for s in c["fiche"]["sections"] for ch in s["champs"]
              if ch["unite"] == "px"]
        assert len(px) == 1, c["nom"]
        pixels.add(px[0])
    assert len(pixels) == 1, "l'exigence de cadrage varie d'une visée à l'autre"

    # 7. Les cas anti-rupture discriminent encore ce pour quoi ils existent.
    nd = par_nom["mer, visée non discriminante"]["fiche"]
    assert nd["discriminante"] is False
    assert any("n'est PAS discriminante" in r
               for s in nd["sections"] for r in s["reserves"])
    enfouie = par_nom["mer, cible entièrement sous l'horizon"]["fiche"]
    assert any("dépasse 100 %" in r
               for s in enfouie["sections"] for r in s["reserves"]), (
        "le cas de cible enfouie ne déclenche plus sa réserve")
    declare = par_nom["mer, k déclaré par l'analyste"]["fiche"]
    assert "Enveloppe de réfraction" not in json.dumps(declare, ensure_ascii=False)
    standard = par_nom["mer, visée discriminante"]["fiche"]
    assert "Enveloppe de réfraction" in json.dumps(standard, ensure_ascii=False)
    sans_libelle = par_nom["lac, sans libellé de cible"]["fiche"]
    assert "Falaises" not in json.dumps(sans_libelle, ensure_ascii=False), (
        "le cas sans libellé en porte un : la branche n'est pas éprouvée")
    avec_libelle = par_nom["mer, observateur libellé"]["fiche"]
    assert "Cap Blanc-Nez" in json.dumps(avec_libelle, ensure_ascii=False)

    # 8. Le replieur : au moins un cas doit réellement replier, un autre
    #    déborder. Des cas qui tiendraient tous sur une ligne n'épingleraient
    #    aucune coupure.
    assert any(len(r["lignes"]) > 1 for r in v["replis"])
    assert any(any(len(l) > r["largeur"] for l in r["lignes"]) for r in v["replis"]), (
        "aucun cas de mot plus long que la largeur : le débordement n'est pas épinglé")
    assert any(r["lignes"] == ["  ·"] for r in v["replis"])

    # 9. La convention d'arrondi est réellement mise à l'épreuve : il faut au
    #    moins une égalité exacte QUI DESCEND (1,25 → 1,2) et une
    #    quasi-égalité QUI MONTE (1,85 → 1,9). Sans les deux, un port qui
    #    arrondirait toujours dans le même sens passerait.
    par_valeur = {a["valeur"]: a for a in v["arrondis"]}
    assert par_valeur[1.25]["metres"] == "1,2", (
        "l'égalité exacte ne descend plus : la convention n'est plus épinglée")
    assert par_valeur[1.85]["metres"] == "1,9", (
        "la quasi-égalité ne monte plus : un port qui traiterait tout « 5 » "
        "comme une égalité passerait")
    assert par_valeur[0.125]["k"] == "0,12"
    assert par_valeur[-0.04]["metres"] == "-0,0", "le signe du zéro est perdu"
    # Et le cas de fiche qui l'a révélé le montre encore.
    court = par_nom["lac, cible courte sur visée longue"]["fiche"]
    assert "soit 1,2 m ici" in json.dumps(court, ensure_ascii=False), (
        "le seuil de la cible de 12,5 m ne vaut plus 1,2 : le cas ne "
        "discrimine plus la convention d'arrondi")

    print("  9 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
