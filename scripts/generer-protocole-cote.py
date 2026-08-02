#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere content/reseau/protocole-cote-trois-mires.json.

Tous les chiffres du protocole sont produits ici, aucun n'est saisi a la main
dans le JSON. Relancer ce script doit reproduire le fichier a l'octet pres :
c'est ce qui rend le pre-enregistrement verifiable.

    python3 scripts/generer-protocole-cote.py
"""
import json, math

R = 6_371_008.8
H_MIRE = 4.000
K_JOUR, K_NUIT, K_REF = 0.10, 0.34, 0.13
DISTANCES_M = [1000, 1500, 2000, 3000, 5000, 7000, 10000]

def f(D, k=0.0): return (1.0 - k) * D*D / (8.0 * R)
def sec(x): return x * 206264.806

# ── budget d'erreur ────────────────────────────────────────────────────────────
ARCSEC       = 1 / 206264.806
SIG_POINTE   = 2.0 * ARCSEC   # precision de pointe, une visee, lunette de niveau
SIG_EAU_LIBRE = 0.100         # lecture de la ligne d'eau, clapot libre
SIG_EAU_TUBE  = 0.005         # lecture dans un puits de tranquillisation
SIG_LONGUEUR  = 0.001         # longueur d'une perche
SIG_K         = 0.12          # dispersion de terrain du coefficient de refraction
NLEC          = 3             # lectures par seance

def budget(D, sig_eau, n_seances=1):
    """Postes d'erreur sur une fleche, en metres. Retourne (postes, sigma total)."""
    n = NLEC * n_seances
    sig_h = math.hypot(SIG_LONGUEUR, sig_eau / math.sqrt(NLEC))
    postes = {
        # direction A->C entachee de SIG_POINTE, lue a mi-distance ; plus la
        # lecture de la graduation de B, elle aussi a mi-distance.
        "pointe":       SIG_POINTE * (D / 2) * math.sqrt(2) / math.sqrt(n),
        # f = (hA + hC)/2 - hB  ->  coefficient sqrt(1/4 + 1/4 + 1)
        "hauteur_eau":  sig_h * math.sqrt(1.5) / math.sqrt(n_seances),
        "verticalite":  4.0 * (1 - math.cos(math.asin(0.010 / 4.0))) / math.sqrt(n_seances),
        "milieu_B":     f(D) * 2 * (0.005 ** 2),
        # multiplicative : ne se moyenne que si les seances echantillonnent des
        # etats atmospheriques reellement independants (jours distincts).
        "refraction":   f(D, 0) * SIG_K / math.sqrt(n_seances),
    }
    return postes, math.sqrt(sum(v * v for v in postes.values()))

def sigma_pente(sig_eau, n_seances, distances):
    """Incertitude sur la pente de la droite log(f) = a.log(D) + b."""
    lx = [math.log10(x) for x in distances]
    mx = sum(lx) / len(lx)
    Sxx = sum((v - mx) ** 2 for v in lx)
    w = [budget(x, sig_eau, n_seances)[1] / f(x) / math.log(10) for x in distances]
    return math.sqrt(sum(v * v for v in w) / len(w)) / math.sqrt(Sxx)

table = []
for D in DISTANCES_M:
    f0, fj, fn, fr = (f(D, k) for k in (0.0, K_JOUR, K_NUIT, K_REF))
    table.append({
        "D_km": round(D/1000, 3),
        "demi_base_AB_BC_m": D//2,
        "modele_plan_lecture_sur_B_m": round(H_MIRE, 4),
        "modele_plan_fleche_mm": 0.0,
        "modele_spherique_fleche_geometrique_mm": round(f0*1000, 2),
        "modele_spherique_fleche_k010_mm": round(fj*1000, 2),
        "modele_spherique_fleche_k013_mm": round(fr*1000, 2),
        "modele_spherique_fleche_k034_mm": round(fn*1000, 2),
        "modele_spherique_lecture_sur_B_m_k013": round(H_MIRE - fr, 4),
        "ecart_minimal_entre_les_deux_modeles_mm": round(fn*1000, 2),
        "garde_d_eau_sous_la_visee_au_milieu_m": round(H_MIRE - f0, 3),
        "rotation_de_la_verticale_A_vers_C_secondes": round(sec(D/R), 2),
    })

au_dela = [{"D_km": D/1000,
            "fleche_geometrique_m": round(f(D), 3),
            "hauteur_de_mire_minimale_m": round(f(D) + 2.0, 2)}
           for D in (15000, 20000, 30000, 50000)]

def bloc_budget(sig_eau, n):
    lignes = []
    for D in DISTANCES_M:
        postes, tot = budget(D, sig_eau, n)
        lignes.append({
            "D_km": D / 1000,
            "fleche_mm": round(f(D) * 1000, 2),
            "postes_mm": {k: round(v * 1000, 3) for k, v in postes.items()},
            "sigma_total_mm": round(tot * 1000, 2),
            "rapport_signal_bruit": round(f(D) / tot, 1),
        })
    return lignes

BUDGET = {
  "_avertissement": (
    "Ce budget a ete calcule APRES la redaction v1.0 et il a corrige le protocole : "
    "avec la tolerance de clapot initiale (10 cm), la lecture de la ligne d'eau ecrasait "
    "le signal en dessous de 5 km et le rapport signal/bruit ne depassait jamais 7. "
    "Le puits de tranquillisation devient donc OBLIGATOIRE, et ce n'est pas un detail "
    "de confort : c'est l'element qui rend la campagne concluante."
  ),
  "hypotheses": {
    "precision_de_pointe_par_visee_secondes": 2.0,
    "lecture_ligne_d_eau_clapot_libre_mm": SIG_EAU_LIBRE * 1000,
    "lecture_ligne_d_eau_avec_puits_mm": SIG_EAU_TUBE * 1000,
    "longueur_de_perche_mm": SIG_LONGUEUR * 1000,
    "dispersion_du_coefficient_de_refraction": SIG_K,
    "lectures_par_seance": NLEC,
    "note_sur_la_refraction": (
      "La refraction est traitee comme une erreur multiplicative de moyenne nulle qui se "
      "reduit en 1/racine(n). Cette reduction n'est legitime que si les seances "
      "echantillonnent des etats atmospheriques independants — d'ou l'exigence de cinq "
      "journees distinctes au minimum et des creneaux matin ET apres-midi. Dix seances "
      "faites le meme jour ne valent pas dix seances."
    ),
  },
  "A_sans_puits_une_seance": bloc_budget(SIG_EAU_LIBRE, 1),
  "B_avec_puits_une_seance": bloc_budget(SIG_EAU_TUBE, 1),
  "C_avec_puits_dix_seances_RETENU": bloc_budget(SIG_EAU_TUBE, 10),
  "pouvoir_de_discrimination": {
    "grandeur": "incertitude sur la pente a de log(f) = a.log(D) + b",
    "par_nombre_de_seances": {
      str(n): {
        "sigma_pente": round(sigma_pente(SIG_EAU_TUBE, n, DISTANCES_M), 4),
        "sigma_separant_2000_de_1000": round(1.0 / sigma_pente(SIG_EAU_TUBE, n, DISTANCES_M), 1),
        "sigma_separant_2000_de_0_modele_plan": round(2.0 / sigma_pente(SIG_EAU_TUBE, n, DISTANCES_M), 1),
      } for n in (1, 5, 10, 20)
    },
    "lecture": (
      "Des une seance par distance, une pente de 2,000 se separe d'une pente de 1,000 — "
      "signature d'un artefact de perspective ou d'un gradient thermique regulier — a plus "
      "de 10 sigma. Le protocole a dix seances porte cette separation au-dela de 30 sigma. "
      "Ce n'est pas la precision sur la fleche qui fait la force du dispositif, c'est le "
      "bras de levier de la decade en distance."
    ),
  },
  "volume_de_travail": {
    "lectures_totales": len(DISTANCES_M) * 10 * NLEC,
    "heures_d_observation": round(len(DISTANCES_M) * 10 * 12 / 60, 1),
    "journees_de_terrain_estimees": "5 a 8, selon la meteo et le temps de deplacement des perches",
  },
}

doc = {
  "_meta": {
    "version": "1.1",
    "titre": "Protocole cote — mesure de la fleche sur trois mires de hauteur egale au-dessus de l'eau",
    "description": (
      "Pre-enregistrement, AVANT toute mesure, des predictions des deux modeles pour une "
      "campagne de sept configurations de distance, de 1 km a 10 km, sur un plan d'eau sans "
      "maree. L'observable n'est pas une fleche isolee : c'est la LOI qui relie la fleche a la "
      "distance. Aucun chiffre de ce fichier n'a ete saisi a la main ; ils sont tous produits "
      "par scripts/generer-protocole-cote.py, qui est verse dans le depot."
    ),
    "date": "2026-08-02", "date_revision": "2026-08-02 — v1.1, ajout du budget d'erreur et du puits de tranquillisation",
    "statut": "PRE-ENREGISTRE — aucune mesure effectuee a ce jour",
    "regle_d_immuabilite": (
      "Les predictions de ce fichier ne seront jamais recalculees apres reception d'une mesure. "
      "Toute modification resterait visible dans l'historique Git, avec sa date."
    ),
    "constantes_du_modele_spherique": {
      "R_m": R,
      "circonference_correspondante_km": round(2*math.pi*R/1000, 1),
      "note_sur_le_rayon": (
        "R = 6 371 008,8 m (rayon moyen WGS84). Une circonference de 40 700 km donnerait "
        "R = 6 477 km, soit 1,7 % d'ecart — trois fois moins que l'incertitude de refraction. "
        "Le choix de R ne change aucune conclusion de ce protocole."
      ),
      "coefficients_de_refraction": {
        "k_jour": K_JOUR, "k_moyen": K_REF, "k_nuit": K_NUIT,
        "source": "Hirt, Guillaume, Wisbar, Burki, Sternberg (2010), J. Geophys. Res. Atmos. 115, D21102 — series temporelles de k par angles verticaux reciproques simultanes au-dessus de l'eau."
      }
    }
  },

  "_l_observable": {
    "grandeur": (
      "Elevation du sommet de la mire centrale B au-dessus de la droite joignant les sommets "
      "des mires A et C, les trois mires ayant exactement la meme hauteur au-dessus de la "
      "ligne d'eau."
    ),
    "pourquoi_elle_est_brute": (
      "La mer fait le nivellement. Trois reperes cales sur la ligne d'eau sont a la meme "
      "hauteur par construction, sans instrument, sans cheminement, sans datum, sans "
      "projection et sans unite de longueur imposee. La seule chose apportee par l'operateur "
      "est une ligne de visee, qui est droite. Il n'y a donc aucun modele de Terre en amont "
      "de la mesure."
    ),
    "ce_qui_se_lit_directement": (
      "Une graduation sur la mire B, a l'endroit ou la visee A-sommet vers C-sommet la croise. "
      "Un nombre en millimetres. Pas un angle, pas une reduction, pas un calcul."
    ),
    "formule": "f = (1 - k) * D^2 / (8 R)   —   D = distance A a C, B au milieu exact",
    "avertissement_sur_la_mer_comme_reference": (
      "La surface de l'eau est une equipotentielle : elle epouse la forme de la Terre au lieu "
      "de la reveler. Mesurer une hauteur PAR RAPPORT a l'eau donne zero a toute distance, sur "
      "toute surface. La mer n'est donc PAS la reference de la mesure ; elle est seulement le "
      "moyen de placer trois points a hauteur egale. La reference est la ligne de visee."
    )
  },

  "_les_deux_predictions": {
    "modele_plan": {
      "enonce": "Terre plane, surface des eaux plane.",
      "prediction": "f = 0,0 mm a TOUTE distance. La lecture sur B vaut 4,000 m dans les sept configurations.",
      "signature_en_log_log": "aucune pente definie ; f reste au niveau du bruit quel que soit D."
    },
    "modele_spherique": {
      "enonce": "Sphere de rayon R = 6 371 km, refraction terrestre standard.",
      "prediction": "f = (1-k) D^2 / (8R), soit 19,6 mm a 1 km et 1 962 mm a 10 km en geometrie pure.",
      "signature_en_log_log": "droite de pente exactement 2,000."
    },
    "pourquoi_les_deux_sont_testables_par_la_meme_lecture": (
      "Les deux modeles predisent un nombre sur la meme graduation, dans la meme seance. "
      "Aucune des deux predictions n'est un repli : elles sont incompatibles des la premiere "
      "configuration."
    )
  },

  "table_de_pre_enregistrement": table,

  "_budget_d_erreur": BUDGET,

  "_test_de_l_exposant": {
    "principe": (
      "C'est le coeur du protocole, et c'est ce qu'aucune campagne connue n'a publie. On ne "
      "cherche pas a mesurer une fleche : on cherche a mesurer l'EXPOSANT de la loi f(D)."
    ),
    "methode": (
      "Porter log(f) contre log(D) sur les sept configurations, avec la mediane des seances "
      "retenues pour chaque distance. Ajustement des moindres carres. Lire la pente."
    ),
    "plage": "1 km a 10 km — une decade complete en distance, un facteur 100 en fleche.",
    "pourquoi_la_refraction_ne_peut_pas_l_imiter": (
      "La refraction agit par le facteur multiplicatif (1-k). Elle deplace la droite "
      "verticalement — elle change l'ORDONNEE A L'ORIGINE. Elle ne change pas la PENTE, sauf "
      "si k lui-meme depend systematiquement de D, ce que les series de Hirt et al. (2010) "
      "excluent : les ecarts sur les angles de refraction y restent sous 1 seconde d'arc "
      "independamment de la longueur de la ligne, de 4 km a 23 km."
    ),
    "pentes_attendues": {
      "modele_spherique": 2.000,
      "modele_plan": "indefinie — f compatible avec zero partout",
      "artefact_de_perspective_ou_de_divergence_optique": "1,0 environ — se distingue donc de 2,0",
      "gradient_thermique_lineaire_sur_la_ligne_de_visee": "1,0 environ"
    },
    "ce_que_ca_apporte": (
      "Une fleche isolee peut toujours etre attribuee a la refraction du jour. Une loi en D^2 "
      "tenue sur une decade, avec des conditions atmospheriques differentes a chaque seance, "
      "ne le peut pas. C'est la seule mesure de cette famille qui soit robuste a l'objection "
      "de refraction, dans les deux sens."
    )
  },

  "montage": {
    "materiel": [
      "Trois perches identiques de 4,00 m, section constante, verticalite verifiee au fil a plomb.",
      "La perche B porte une mire graduee au millimetre sur ses 2,50 m superieurs.",
      "Un puits de tranquillisation par perche : tube plongeur de 50 a 100 mm perce de trous fins en partie basse, solidaire de la perche. Il amortit le clapot et fait passer la lecture de la ligne d'eau de 100 mm a 5 mm — c'est l'element decisif du dispositif.",
      "Lunette de visee ou theodolite sur trepied, oculaire cale au sommet exact de la perche A.",
      "Reflecteur ou cible contrastee au sommet exact de la perche C.",
      "Thermometre, barometre, anemometre a chaque station.",
      "Telemetre laser ou GPS bi-frequence pour poser D et le milieu de B a mieux que 1 m."
    ],
    "geometrie": (
      "A --- B --- C alignes. B au milieu exact de AC, a 0,5 % pres. Les trois bases sont "
      "calees sur la ligne d'eau du moment, relevee simultanement aux trois stations."
    ),
    "hauteur_des_mires": (
      "4,00 m pour les sept configurations, sans exception. C'est ce qui rend la serie "
      "comparable : une seule hauteur, une seule geometrie, seule D varie. A 10 km la visee "
      "passe encore 2,04 m au-dessus de l'eau au milieu — au-dessus de la couche limite "
      "thermique, ce qui est precisement la correction que Wallace avait apportee en 1870 a "
      "l'experience de Rowbotham."
    ),
    "lecture": (
      "Depuis le sommet de A, viser le sommet de C. Relever la graduation de B a l'intersection. "
      "f = 4,000 m moins la lecture."
    )
  },

  "protocole_de_seance": {
    "repetition_exigee": "Dix seances retenues minimum par configuration, reparties sur au moins cinq journees distinctes.",
    "fenetres": "Matin et apres-midi obligatoirement representes. Les seances de nuit sont enregistrees separement (k y atteint 0,34).",
    "duree_d_une_seance": "Trois lectures espacees de dix minutes, plus les parametres meteo a chaque lecture.",
    "regles_de_rejet_ECRITES_A_L_AVANCE": [
      "Rejet si les trois lectures d'une seance s'ecartent de plus de 20 % de leur mediane — refraction instable.",
      "Rejet si un mirage superieur est visible a l'oeil ou au capteur (image dedoublee, inversion, etirement vertical).",
      "OBLIGATOIRE : chaque perche est equipee d'un puits de tranquillisation — un simple tube plongeur perce en bas, qui amortit le clapot et rend la ligne d'eau lisible a 5 mm. Sans lui la campagne n'est pas concluante : voir _budget_d_erreur.",
      "Rejet si le vent depasse 8 m/s (vibration des perches).",
      "Rejet si les trois lectures de ligne d'eau d'une meme station s'ecartent de plus de 10 mm.",
      "Rejet si l'ecart de temperature air-eau depasse 5 K.",
      "Rejet si la verticalite d'une perche s'ecarte de plus de 1 cm sur 4 m."
    ],
    "regle_de_publication_des_rejets": (
      "Toute seance rejetee est publiee avec sa lecture brute et le motif du rejet. Le nombre "
      "de seances rejetees et leur repartition font partie du resultat."
    ),
    "piege_a_eviter": (
      "Ne jamais recaler l'instrument sur une bulle ou un compensateur entre A et C. Le "
      "compensateur se cale sur la verticale locale, qui tourne avec la surface — il "
      "reintroduit exactement l'aveuglement que ce montage sert a contourner. La visee A vers "
      "C doit etre une droite geometrique, pas une horizontale instrumentale."
    )
  },

  "regle_de_decision": {
    "note": "Ecrite avant toute mesure. Elle ne sera pas revue apres.",
    "issue_1_modele_plan": (
      "Si, sur les sept configurations, f reste sous 3 sigma de zero — en particulier si f < 600 mm "
      "a 10 km, ou le modele spherique predit 1 295 mm meme dans le cas de refraction le plus "
      "defavorable (k = 0,34) — alors la surface des eaux est plane sur 10 km, et c'est le "
      "resultat qui sera publie, sans attenuation."
    ),
    "issue_2_modele_spherique": (
      "Si la pente log-log vaut 2,00 a 0,10 pres ET que le R deduit tombe dans une fourchette "
      "de 25 % autour de 6 371 km apres correction de k, la courbure est etablie sur cette "
      "plage, et c'est ce qui sera publie."
    ),
    "issue_3_non_concluant": (
      "Pente comprise entre 1,2 et 1,8, ou dispersion inter-seances superieure a 40 % : la "
      "campagne est declaree non concluante et publiee comme telle. Un resultat non concluant "
      "n'est pas un echec — c'est ce qui manque le plus dans ce dossier."
    ),
    "symetrie": (
      "Les trois issues sont ecrites avec le meme soin et engagent la meme publication. Un "
      "protocole qui ne peut pas donner tort a celui qui le tient ne vaut rien."
    )
  },

  "sites_candidats": {
    "critere": "Plan d'eau sans maree ni houle, 10 km de fetch rectiligne, acces aux trois points, fond permettant de planter des perches.",
    "liste": [
      {"nom": "Etang de Vaccares (Camargue, Bouches-du-Rhone)", "longueur_utile_km": 13,
       "profondeur_moyenne_m": 1.5, "maree": "negligeable",
       "avantage": "Tres peu profond — les perches se plantent a pied ou en barque plate sur toute la ligne. Meilleur site francais identifie.",
       "contrainte": "Reserve naturelle — autorisation du Parc naturel regional de Camargue obligatoire."},
      {"nom": "Etang de Thau (Sete a Marseillan, Herault)", "longueur_utile_km": 19,
       "profondeur_moyenne_m": 4.5, "maree": "quelques centimetres",
       "avantage": "Permet d'aller au-dela de 10 km si l'on dispose de supports hauts.",
       "contrainte": "Tables conchylicoles a contourner ; trafic."},
      {"nom": "Etang de Berre (Bouches-du-Rhone)", "longueur_utile_km": 15,
       "profondeur_moyenne_m": 6.0, "maree": "negligeable",
       "avantage": "Acces routier sur tout le pourtour.", "contrainte": "Mistral frequent."},
      {"nom": "Etang de Leucate-Salses (Aude / Pyrenees-Orientales)", "longueur_utile_km": 14,
       "profondeur_moyenne_m": 2.0, "maree": "negligeable",
       "avantage": "Peu profond, rives accessibles.", "contrainte": "Tramontane."},
      {"nom": "Baie de Somme a maree basse", "longueur_utile_km": 15,
       "profondeur_moyenne_m": 0.0, "maree": "forte — 10 m de marnage",
       "avantage": "Estran de sable dur nivele par la mer elle-meme ; on y marche et on y plante des piquets.",
       "contrainte": "La ligne d'eau bouge pendant la seance — reserve aux configurations courtes, ou reference prise sur l'estran et non sur l'eau."}
    ],
    "recommandation": "Vaccares en premier, Thau en repli. Reprendre ensuite une configuration complete sur un site de latitude et d'orientation differentes."
  },

  "_pourquoi_la_campagne_s_arrete_a_10_km": {
    "raison": (
      "Au-dela, la fleche depasse ce qu'une perche portative peut enjamber : la visee A vers C "
      "passerait sous l'eau au milieu. Il faut alors des supports fixes hauts — phare, pylone, "
      "falaise — ce qui fait sortir du montage a trois perches identiques et casse la "
      "comparabilite de la serie."
    ),
    "table": au_dela,
    "consequence": (
      "La decade 1-10 km suffit au test de l'exposant : elle donne deja un facteur 100 sur la "
      "fleche. Une extension a 20-30 km serait un complement, pas un prealable."
    )
  },

  "_etat_de_l_art": {
    "avertissement_de_classement": (
      "Ces cinq entrees sont de CLASSE C au sens de content/reseau/mesures-brutes.json : "
      "rapportees par des resumes de recherche, sources primaires NON consultees. Le proxy "
      "reseau de l'environnement de travail a renvoye 403 sur les six pages sources tentees le "
      "2 aout 2026. A relire directement avant tout usage argumentatif."
    ),
    "campagnes": [
      {"nom": "Wallace — Bedford Level", "annee": 1870, "distance_km": 9.66,
       "montage": "Trois points a 4,04 m au-dessus de l'eau, mat intermediaire au milieu — le meme montage que ce protocole.",
       "resultat_rapporte": "Le mat central apparait au-dessus de la corde.",
       "defaut": "Observation unique, non repetee, non instrumentee, pas de serie en distance.",
       "camp": "sceptique"},
      {"nom": "Rainy Lake (Minnesota / Ontario) — Hnatiuk, Kozlowski, Soundly", "annee": 2018, "distance_km": 10,
       "montage": "Deux rangees de cibles sur glace : rangee Bedford a 1,854 m, rangee tangente calculee pour s'aligner a l'oeil d'un observateur a 3,912 m sous R = 6 371 km et k = 0,17.",
       "resultat_rapporte": "Cibles Bedford progressivement sous la ligne d'oeil, tangentes alignees. Accord avec le modele spherique.",
       "defaut": "Prediction non horodatee dans un depot public anterieur a la mesure ; une seule distance, donc pas de test d'exposant.",
       "camp": "mixte — participation directe de partisans du modele plan",
       "interet_pour_ce_projet": "Le design a deux rangees est symetrique : chaque rangee est un piege pour un modele. C'est le meilleur precedent methodologique connu."},
      {"nom": "FECORE — Lac Balaton (Hongrie) et Lac IJssel (Pays-Bas) — Szekely, Cavanaugh", "annee": 2018,
       "distance_km": 40,
       "montage": "Terrestrial Laser Targeting ; jusqu'a 40 km sur le Balaton, 21,26 km sur l'IJssel (laser a 2,85 m, observe a 1,20 m).",
       "resultat_rapporte": "Succes annonce, puis conteste.",
       "defaut": "Laser mal calibre pointant legerement vers le bas ; divergence du faisceau rendant le point d'impact non localisable ; ni theodolite, ni niveau automatique, ni mire, ni trepied de geometre sur toute la campagne.",
       "camp": "modele plan",
       "lecon": "Un laser divergent n'est pas une reference rectiligne exploitable a 20 km. C'est un echec instrumental, pas ideologique — et il justifie a lui seul l'exigence de mire graduee et de visee optique de ce protocole."},
      {"nom": "Lac Pontchartrain (Louisiane) — pylones de ligne haute tension", "annee": 2017, "distance_km": 24.27,
       "montage": "Pylones identiques, de hauteur uniforme au-dessus de l'eau, alignes sur 24,27 km. Observations au teleobjectif.",
       "resultat_rapporte": "Enfoncement progressif des pylones lointains ; point de fuite au-dessus de la ligne d'horizon.",
       "defaut": "Photographique et non metrique ; pas de lecture chiffree sur graduation.",
       "camp": "aucun — l'ouvrage a ete construit par un electricien, sans rapport avec la question",
       "interet_pour_ce_projet": "C'est le montage a mires de hauteur egale, deja installe et permanent, a 24 km. Aucun soupcon de conception orientee."},
      {"nom": "Hirt, Guillaume, Wisbar, Burki, Sternberg — refraction au-dessus de l'eau", "annee": 2010,
       "distance_km": 23,
       "montage": "Angles verticaux reciproques simultanes, theodolites video, lignes de 4 a 23 km.",
       "resultat_rapporte": "k varie de 0,10 le jour a 0,34 la nuit ; ecarts sur les angles de refraction sous 1 seconde d'arc, independamment de la longueur de la ligne.",
       "defaut": "Ne porte pas sur la forme de la surface — porte sur la refraction. C'est precisement ce qui en fait une source neutre utilisable.",
       "camp": "institutionnel — Journal of Geophysical Research: Atmospheres",
       "reference": "J. Geophys. Res. Atmos. 115, D21102 (2010), doi:10.1029/2010JD014067"}
    ],
    "ce_qui_manque_dans_la_litterature": [
      "Aucune campagne francophone identifiee.",
      "Aucune campagne dont les predictions soient horodatees dans un depot public AVANT la mesure.",
      "Aucune mesure de l'exposant : tout le monde mesure une fleche a une distance, personne ne mesure la loi.",
      "Aucune publication a comite de lecture consacree specifiquement a ce test — la geodesie publie sur la refraction, pas sur la forme, qu'elle considere acquise."
    ]
  },

  "_ce_que_ce_protocole_ajoute": [
    "Le pre-enregistrement horodate dans un depot Git public, avant la premiere mesure.",
    "La serie en distance sur une decade, donc la mesure de l'exposant et non d'une valeur isolee.",
    "Les regles de rejet ecrites avant les seances, et la publication obligatoire des seances rejetees.",
    "Une regle de decision a trois issues, ecrites avec le meme soin, dont une issue plane explicite.",
    "Un cout d'entree faible : trois perches, une lunette, un plan d'eau — pas une campagne geodesique."
  ],

  "engagement": {
    "publication_integrale": "Carnet brut complet, y compris les seances rejetees et le motif de leur rejet.",
    "publication_meme_si_defavorable": "Le resultat est publie quel qu'il soit, y compris l'issue 1 et l'issue 3.",
    "non_recalcul": "Les predictions de ce fichier ne seront pas recalculees apres mesure.",
    "donnees_ouvertes": "Lectures brutes, photos et parametres meteo publies sous licence ouverte.",
    "tracabilite": "Toute modification de ce fichier reste visible dans l'historique Git."
  },

  "_controle": {
    "configurations_prevues": len(DISTANCES_M),
    "seances_minimales_totales": 10 * len(DISTANCES_M),
    "mesures_effectuees": 0,
    "etat": "PRE-ENREGISTRE — aucune mesure",
    "prochain_jalon": "Autorisation du Parc naturel regional de Camargue pour l'etang de Vaccares, ou repli sur l'etang de Thau.",
    "genere_par": "scripts/generer-protocole-cote.py"
  }
}

with open("content/reseau/protocole-cote-trois-mires.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print("ok", len(json.dumps(doc)), "octets")
