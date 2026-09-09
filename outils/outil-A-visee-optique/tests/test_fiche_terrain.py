"""
La fiche protocole terrain.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que la fiche est DÉRIVÉE de la simulation et n'invente rien : les hauteurs,
la distance et le coefficient employés sont ceux du calcul, et le milieu ne
déplace aucun chiffre.

Et surtout deux propriétés qui sont la raison d'être de la fiche :

  · la PRÉDICTION n'apparaît que dans le dernier bloc, celui qu'on ne lit
    qu'après la prise de vue. Une fiche qui l'annoncerait en tête ferait
    mesurer la valeur attendue, et la sortie ne vaudrait plus rien ;
  · chaque champ demandé porte un POURQUOI. Un champ sans motif est un champ
    rempli au hasard, et une valeur au hasard est pire qu'une case vide.

CE QU'ILS N'ÉTABLISSENT PAS
───────────────────────────
Rien sur l'utilisabilité réelle de la fiche par un volontaire sur une digue
un matin d'hiver. Cela se saurait en la faisant employer, pas en la testant.
"""

import pytest

from visee_optique.fiche_terrain import (
    CHAMPS_ECARTES,
    LARGEUR_TXT,
    MILIEUX,
    PIXELS_MIN_ECART,
    PREFIXE_REFERENCE_ATTENDU,
    FicheError,
    _replier,
    construire_fiche,
    nom_fichier,
    rendre_txt,
)
from visee_optique.simulation import juger

# ─────────────────────────────────────────────────────────────────────────────
# Fabrication
# ─────────────────────────────────────────────────────────────────────────────

# Une occultation choisie pour que ses chiffres soient RECONNAISSABLES dans le
# texte : « 40,2 » et « 36,5 » n'apparaissent nulle part ailleurs, ce qui
# permet de vérifier où la prédiction est écrite — et où elle ne l'est pas.
MASQUEE = 40.2
CIBLE_M = 110.0


def fiche(milieu="mer", masquee=MASQUEE, cible_m=CIBLE_M, verdict_cible_m=None, **kw):
    """Une fiche d'essai.

    `verdict_cible_m` permet de construire un verdict VALIDE tout en passant à
    la fiche une hauteur de cible hors domaine : sans cela, `juger` refusait le
    premier et le refus éprouvé n'était plus celui de `construire_fiche`.
    """
    p = dict(
        milieu=milieu, horodatage="2026-09-09T08:14:00Z",
        obs_latitude=50.94642, obs_longitude=1.75305, obs_libelle=None,
        cible_latitude=51.13152, cible_longitude=1.338825,
        cible_libelle="Falaises de Douvres",
        distance_m=35418.0, azimut_deg=302.4,
        hauteur_observateur_m=2.0, hauteur_cible_m=cible_m,
        masquee_enveloppe_min_m=38.1, masquee_enveloppe_max_m=44.9,
        k_employe=0.13, k_personnalise=False,
        verdict=juger(masquee, verdict_cible_m or cible_m),
    )
    p.update(kw)
    return construire_fiche(**p)


def texte_section(f, numero):
    """Tout le texte d'un bloc, réserves comprises."""
    s = [x for x in f.sections if x.numero == numero][0]
    morceaux = [s.titre]
    morceaux += [f"{k} {v}" for k, v in s.releves]
    morceaux += [f"{c.libelle} {c.unite or ''} {c.pourquoi}" for c in s.champs]
    morceaux += list(s.consignes)
    morceaux += list(s.reserves)
    return "\n".join(morceaux)


# ─────────────────────────────────────────────────────────────────────────────
# La structure
# ─────────────────────────────────────────────────────────────────────────────


def test_cinq_blocs_dans_l_ordre():
    f = fiche()
    assert [s.numero for s in f.sections] == ["01", "02", "03", "04", "05"]


def test_le_depot_est_le_dernier_bloc():
    """Il doit être la partie qu'on replie ou qu'on découpe avant de partir.

    Au milieu de la page, une consigne « ne pas lire avant » ne tient pas une
    seconde — l'œil a déjà lu.
    """
    f = fiche()
    assert f.sections[-1].sous_scelle is True
    assert [s.sous_scelle for s in f.sections].count(True) == 1


def test_chaque_champ_dit_pourquoi_il_est_demande():
    """Un champ sans motif est rempli au hasard, ou pas du tout."""
    for milieu in MILIEUX:
        for s in fiche(milieu).sections:
            for c in s.champs:
                assert c.pourquoi.strip(), (milieu, c.libelle)
                assert c.libelle.strip(), milieu


def test_les_omissions_sont_ecrites_avec_leur_motif():
    """Une omission qu'on ne peut pas lire ne peut pas être contestée."""
    f = fiche()
    assert len(f.champs_ecartes) == len(CHAMPS_ECARTES) >= 4
    for titre, motif in f.champs_ecartes:
        assert titre.strip() and len(motif) > 40, titre


# ─────────────────────────────────────────────────────────────────────────────
# L'analyse en aveugle : la propriété centrale
# ─────────────────────────────────────────────────────────────────────────────


def test_la_prediction_n_apparait_que_dans_le_bloc_sous_scelle():
    """Le point de toute la fiche.

    « 40,2 » et « 36,5 » sont les chiffres de la prédiction. S'ils
    apparaissaient dans le bloc des mesures ou dans les consignes, le
    volontaire les lirait avant de viser et mesurerait ce qu'on lui a annoncé.
    """
    f = fiche()
    for numero in ("01", "02", "03", "04"):
        t = texte_section(f, numero)
        assert "40,2" not in t, numero
        assert "36,5" not in t, numero
    scelle = texte_section(f, "05")
    assert "40,2" in scelle
    assert "36,5" in scelle


def test_le_bloc_sous_scelle_porte_l_horodatage_et_dit_ce_qu_il_ne_prouve_pas():
    f = fiche()
    t = texte_section(f, "05")
    assert "2026-09-09T08:14:00Z" in t
    # Un horodatage produit par la machine du visiteur n'atteste aucune
    # antériorité. Le taire laisserait croire à un dépôt opposable.
    assert "n'atteste aucune antériorité" in t


def test_l_exigence_de_cadrage_est_tiree_du_seuil_et_non_du_resultat():
    """La fuite d'aveuglement la plus facile à ne pas voir.

    Il faut dire au volontaire jusqu'où zoomer, et le nombre juste — 20 pixels
    divisés par la fraction réellement masquée — lui annonce cette fraction :
    20 sur 55 se retrouve en une division. Le nombre est donc tiré du SEUIL,
    qui ne dépend pas du résultat, et qui suffit puisqu'une visée
    discriminante exige toujours MOINS de pixels que le seuil.
    """
    px = [c for s in fiche().sections for c in s.champs if c.unite == "px"][0]
    assert "40,2" not in px.pourquoi
    assert "36,5" not in px.pourquoi
    assert str(PIXELS_MIN_ECART) in px.pourquoi
    # 20 pixels au seuil de 10 % : 200 pixels de cible, quelle que soit la visée.
    assert "200 pixels de haut" in px.pourquoi
    # Et le nombre ne bouge pas d'une visée à l'autre : s'il bougeait, il
    # porterait de l'information sur le résultat.
    for autre in (fiche(masquee=11.0), fiche(masquee=800.0), fiche(masquee=1.0)):
        p2 = [c for s in autre.sections for c in s.champs if c.unite == "px"][0]
        assert p2.pourquoi == px.pourquoi


# ─────────────────────────────────────────────────────────────────────────────
# Le milieu : il change les consignes, pas les chiffres
# ─────────────────────────────────────────────────────────────────────────────


def test_le_milieu_ne_deplace_aucun_chiffre():
    """La géométrie est la même sur un lac, en mer et sur terre.

    Sans ce test, ajouter un jour un ajustement « propre au milieu » dans la
    fiche passerait pour une amélioration, alors que ce serait un calcul
    fantôme fait hors du moteur épinglé.
    """
    depots = {m: texte_section(fiche(m), "05") for m in MILIEUX}
    valeurs = set(depots.values())
    assert len(valeurs) == 1, "le bloc de prédiction dépend du milieu"


def test_chaque_milieu_a_son_niveau_de_reference_et_sa_reserve():
    references = set()
    reserves = set()
    for m in MILIEUX:
        f = fiche(m)
        references.add(f.reference_verticale)
        reserves.add(MILIEUX[m]["reserve"])
        assert f.reference_verticale in texte_section(f, "01")
    assert len(references) == 3, "deux milieux partagent un niveau de référence"
    assert len(reserves) == 3, "deux milieux partagent une réserve"


def test_les_references_se_contractent_sans_faute():
    """« au-dessus de le niveau » est une faute, et elle s'imprimerait.

    Les phrases écrivent « du » et « au » par simple concaténation. C'est
    correct tant que chaque référence commence par « niveau », un masculin à
    consonne. Ajouter un milieu dont la référence commencerait par « la
    surface » produirait « du la surface » — mieux vaut un test rouge qu'une
    faute sur une fiche imprimée.
    """
    for m, d in MILIEUX.items():
        assert d["reference"].startswith(PREFIXE_REFERENCE_ATTENDU), m
    for m in MILIEUX:
        t = rendre_txt(fiche(m))
        # Le contrôle vise le PRÉFIXE, pas « de le » tout court : « on lui a
        # dit de le chercher » est correct, et un contrôle qui crie dessus
        # finit par être désactivé.
        for faute in ("de le " + PREFIXE_REFERENCE_ATTENDU,
                      "à le " + PREFIXE_REFERENCE_ATTENDU):
            assert faute not in t, (m, faute)


def test_la_maree_n_est_demandee_qu_en_mer():
    """Sur un lac elle n'existe pas, sur terre la question n'a pas de sens."""
    def libelles(m):
        return " | ".join(c.libelle for s in fiche(m).sections for c in s.champs)

    assert "marée" in libelles("mer")
    assert "marée" not in libelles("lac")
    assert "marée" not in libelles("terre")
    # La cote d'un lac est demandée, mais sans obligation : beaucoup de lacs
    # n'ont pas d'échelle visible, et exiger une valeur inventerait une donnée.
    cotes = [c for s in fiche("lac").sections for c in s.champs
             if "Cote du lac" in c.libelle]
    assert len(cotes) == 1 and cotes[0].obligatoire is False


def test_la_seconde_temperature_suit_le_milieu():
    def libelles(m):
        return " | ".join(c.libelle for s in fiche(m).sections for c in s.champs)

    assert "Température de l'eau en surface" in libelles("mer")
    assert "Température de l'eau en surface" in libelles("lac")
    assert "Température de l'eau" not in libelles("terre")
    assert "deux mètres du sol" in libelles("terre")


def test_les_temperatures_disent_qu_elles_n_entrent_pas_dans_le_calcul():
    """Le point le plus facile à travestir de toute la fiche.

    Le simulateur tourne sur k = 0,13 ; il ne dérive pas k des températures.
    Demander ces deux valeurs sans le dire laisserait croire que la fiche
    affine le calcul, alors qu'elles servent à le CONTESTER après coup.
    """
    t = " ".join(c.pourquoi for s in fiche().sections for c in s.champs)
    assert "n'entre PAS dans le calcul" in t
    assert "contester" in t


def test_sur_terre_la_reserve_de_relief_est_ecrite():
    """Une visée terrestre est plus faible, et le taire serait un mensonge.

    Le sol intermédiaire n'est pas une surface de référence, et le simulateur
    ne modélise aucun relief : une base masquée peut l'être par un pli de
    terrain.
    """
    t = texte_section(fiche("terre"), "01")
    assert "AUCUN relief" in t
    assert "pli de terrain" in t
    # Et la consigne de terrain qui va avec : photographier le trajet.
    consignes = " ".join(fiche("terre").sections[2].consignes)
    assert "terrain intermédiaire" in consignes
    assert "ligne d'eau" not in consignes


def test_sur_l_eau_la_ligne_d_eau_est_le_repere():
    consignes = " ".join(fiche("mer").sections[2].consignes)
    assert "ligne d'eau" in consignes


# ─────────────────────────────────────────────────────────────────────────────
# Les cas limites du verdict
# ─────────────────────────────────────────────────────────────────────────────


def test_une_visee_non_discriminante_le_dit_avant_de_partir():
    """Sinon on fait la sortie pour rien, et on l'apprend en rentrant."""
    f = fiche(masquee=1.0)  # 0,9 % de 110 m : sous le seuil
    assert f.discriminante is False
    limites = [s for s in f.sections if s.numero == "04"][0]
    assert "n'est PAS discriminante" in limites.reserves[0]


def test_une_visee_discriminante_ne_porte_pas_cet_avertissement():
    """Sans ce contrôle, l'avertissement pourrait être là toujours."""
    f = fiche()
    limites = [s for s in f.sections if s.numero == "04"][0]
    assert all("n'est PAS discriminante" not in r for r in limites.reserves)


def test_cible_entierement_sous_l_horizon_signalee():
    """Au-delà de 100 %, l'observation devient binaire et la réfraction règne.

    C'est le cas où « je l'ai vue quand même » s'explique le plus facilement
    autrement que par le modèle, et il faut que le volontaire le sache.
    """
    f = fiche(masquee=800.0)  # 727 % de 110 m
    t = texte_section(f, "05")
    assert "dépasse 100" in t
    assert "690,0 m" in t, "l'enfouissement au-delà du sommet n'est pas chiffré"


def test_une_occultation_nulle_ne_casse_pas_la_fiche():
    """Le cas où les deux modèles prédisent la même chose, exactement.

    L'exigence de cadrage venant du seuil et non du résultat, il n'y a plus de
    division par zéro possible — ce test le CONSTATE plutôt que de le supposer,
    parce que la version précédente divisait bien par la fraction.
    """
    f = fiche(masquee=0.0)
    assert f.discriminante is False
    px = [c for s in f.sections for c in s.champs if c.unite == "px"][0]
    assert "200 pixels de haut" in px.pourquoi
    assert len(rendre_txt(f)) > 1000


def test_l_enveloppe_de_refraction_disparait_quand_k_est_declare():
    """Afficher une enveloppe contredirait ce que l'analyste affirme connaître."""
    standard = texte_section(fiche(), "05")
    declare = texte_section(fiche(k_employe=0.25, k_personnalise=True), "05")
    assert "Enveloppe de réfraction" in standard
    assert "Enveloppe de réfraction" not in declare
    assert "TOUTE l'enveloppe" in standard
    assert "TOUTE l'enveloppe" not in declare


def test_le_k_employe_est_celui_du_calcul():
    t = texte_section(fiche(k_employe=0.25, k_personnalise=True), "01")
    assert "k = 0,25" in t
    assert "déclaré par vous" in t
    assert "k = 0,13" not in t


# ─────────────────────────────────────────────────────────────────────────────
# Les refus
# ─────────────────────────────────────────────────────────────────────────────


def test_milieu_inconnu_refuse():
    with pytest.raises(FicheError, match="Milieu inconnu"):
        fiche("océan")


def test_horodatage_vide_refuse():
    """Sans lui, le bloc de dépôt ne dit plus à quel moment la valeur a été fixée."""
    with pytest.raises(FicheError, match="horodatage"):
        fiche(horodatage="   ")


@pytest.mark.parametrize("kw", [
    {"distance_m": 0.0},
    {"distance_m": -1.0},
    {"cible_m": 0.0, "verdict_cible_m": CIBLE_M},
    {"hauteur_observateur_m": -0.5},
])
def test_parametres_hors_domaine_refuses(kw):
    with pytest.raises(FicheError):
        fiche(**kw)


# ─────────────────────────────────────────────────────────────────────────────
# Le rendu texte
# ─────────────────────────────────────────────────────────────────────────────


def test_aucune_ligne_ne_depasse_la_largeur():
    """Une ligne trop longue est recassée par le lecteur de courriel, au hasard."""
    for m in MILIEUX:
        for ligne in rendre_txt(fiche(m)).splitlines():
            assert len(ligne) <= LARGEUR_TXT, (m, len(ligne), ligne)


def test_le_fichier_se_termine_par_un_saut_de_ligne():
    """Convention des fichiers texte ; certains outils avalent la dernière ligne."""
    t = rendre_txt(fiche())
    assert t.endswith("\n")
    assert not t.endswith("\n\n")


def test_le_rendu_est_deterministe():
    """Aucune horloge, aucun aléa : deux appels donnent le même octet."""
    assert rendre_txt(fiche()) == rendre_txt(fiche())


def test_les_consignes_sont_en_retrait_pendant():
    """La deuxième ligne d'une consigne ne doit pas revenir à la marge.

    Sans retrait pendant, la numérotation cesse de se lire et la liste devient
    un pavé où l'on ne voit plus où commence chaque point.
    """
    lignes = rendre_txt(fiche()).splitlines()
    i = [j for j, l in enumerate(lignes) if l.startswith("  1. Trépied")][0]
    suite = lignes[i + 1]
    assert suite.startswith("     ") and suite[5] != " ", suite


def test_le_texte_porte_tous_les_blocs_et_le_scelle_en_dernier():
    t = rendre_txt(fiche())
    positions = [t.index("%s · " % n) for n in ("01", "02", "03", "04", "05")]
    assert positions == sorted(positions)
    assert "À NE LIRE QU'APRÈS LA PRISE DE VUE" in t
    # L'avertissement d'aveuglement précède les chiffres de la prédiction.
    assert t.index("À ne pas lire avant") < t.index("40,2")


def test_le_nom_de_fichier_est_sans_surprise():
    """Ni deux-points, ni accent, ni espace : ce nom traverse tous les systèmes."""
    n = nom_fichier(fiche(), 35418.0)
    assert n == "fiche-terrain-mer-35-km.txt"
    assert all(c.isalnum() or c in "-." for c in n), n


# ─────────────────────────────────────────────────────────────────────────────
# Le replieur, écrit à la main pour que le port produise les mêmes coupures
# ─────────────────────────────────────────────────────────────────────────────


def test_replier_respecte_la_largeur_et_le_retrait():
    lignes = _replier("un deux trois quatre cinq six sept huit", 20, "  * ", "    ")
    assert all(len(l) <= 20 for l in lignes)
    assert lignes[0].startswith("  * ")
    assert all(l.startswith("    ") and not l.startswith("  * ") for l in lignes[1:])


def test_replier_ne_coupe_pas_un_mot_plus_long_que_la_largeur():
    """Couper au milieu d'un nombre serait pire que la ligne longue."""
    mot = "A" * 40
    lignes = _replier("court %s fin" % mot, 20, "  ")
    assert mot in "".join(lignes)
    assert any(len(l) > 20 for l in lignes), "le mot long a été coupé"


def test_replier_sur_un_texte_vide_ne_rend_pas_de_ligne_de_blancs():
    assert _replier("", 20, "  · ") == ["  ·"]
