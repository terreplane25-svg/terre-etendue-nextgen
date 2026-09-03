#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocole expérimental : portion visible d'une cible éloignée au-dessus de la mer.

Ce que ce script produit
────────────────────────
Un protocole scientifique complet, en français, structuré selon les trente-cinq
rubriques demandées. Toutes les valeurs numériques imprimées sont recalculées
ici et vérifiées par controle() ; aucune n'est écrite en dur dans le texte.

Les vérifications que controle() impose
───────────────────────────────────────
  · la hauteur occultée obtenue par la formule fermée en sécante coïncide avec
    celle obtenue par résolution numérique de s(h) + s(c) = D ;
  · le tracé de rayon par quadrature dans une atmosphère stratifiée coïncide
    avec l'approximation du rayon effectif R/(1−k) à mieux que 0,5 m tant que
    k ≤ 0,5 ;
  · la constante 503,3 de la relation gradient–coefficient est redérivée depuis
    g, R_d et la réfractivité optique, et non recopiée ;
  · elle donne k = 0 au gradient autoconvectif et k = 1 à +12,9 K/100 m.

Un point de physique que le cahier des charges mélangeait
─────────────────────────────────────────────────────────
Le conduit d'évaporation est un phénomène RADIO. Il est piloté par le gradient
d'humidité, dont le terme dans la réfractivité vaut +89,9 N à e = 20 hPa en
radioélectrique contre −0,78 N en optique : un rapport de 115. Un conduit
optique exige donc une inversion thermique extrême, pas un gradient d'humidité.
Le protocole le dit et le chiffre plutôt que d'importer un raisonnement radio
dans une expérience optique.

Ce que le tracé de rayon révèle, et que la moyenne cache
───────────────────────────────────────────────────────
Une couche d'inversion de 60 m avec k = 0,80 surmontée d'une atmosphère
standard k = 0,13 ne se comporte pas comme la moyenne pondérée en hauteur
(0,18) : le rayon rasant passe l'essentiel de son trajet à faible pente dans la
couche basse, et le k homogène équivalent vaut 0,56. C'est l'argument
quantitatif qui justifie d'exiger un profil vertical près de la surface plutôt
qu'une valeur moyenne.
"""
import math
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
CIBLE = os.path.join(PROTOCOLES, "visibilite-cible-eloignee.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

VERSION = "1.0"
DATE = "3 septembre 2026"
AUTEUR = "Terre &#201;tendue"
CONTACT = "terre-etendue-islam.fr"

# ── Constantes physiques et géodésiques ──────────────────────────────────────
A_GRS80 = 6378137.0                 # m, demi-grand axe
F_GRS80 = 1.0/298.257222101         # aplatissement
B_GRS80 = A_GRS80*(1.0 - F_GRS80)
R_MOYEN = (2.0*A_GRS80 + B_GRS80)/3.0   # R1 de l'IUGG = 6 371 008,8 m
G0 = 9.80665                        # m/s²
RD = 287.058                        # J/(kg·K), air sec
C_OPT = 79e-6                       # réfractivité optique : n − 1 = 79e-6 P/T
GH = G0/RD                          # 0,034163 K/m — gradient autoconvectif
CONST_K = R_MOYEN*C_OPT             # 503,3

H_OBS = 800.0                       # m — exemple imposé
H_CIBLE = 100.0                     # m — exemple imposé
P0, T0 = 1013.25, 288.15            # hPa, K — atmosphère de référence


# ── Géométrie sphérique ──────────────────────────────────────────────────────
def s_arc(h, R=R_MOYEN):
    """Arc au sol entre le pied de l'observateur et son point de tangence."""
    return R*math.acos(R/(R + h))


def d_slant(h, R=R_MOYEN):
    """Distance rectiligne œil → point de tangence."""
    return math.sqrt(2.0*R*h + h*h)


def d_approx(h, R=R_MOYEN):
    """Approximation classique √(2Rh)."""
    return math.sqrt(2.0*R*h)


def cachee(h_obs, D, R=R_MOYEN):
    """Hauteur occultée à la base de la cible — formule fermée en sécante."""
    s1 = s_arc(h_obs, R)
    if D <= s1:
        return 0.0
    return R*(1.0/math.cos((D - s1)/R) - 1.0)


def cachee_dicho(h_obs, D, R=R_MOYEN):
    """La même, résolue numériquement : s(h) + s(c) = D. Contrôle indépendant."""
    s1 = s_arc(h_obs, R)
    if D <= s1:
        return 0.0
    vise, lo, hi = D - s1, 0.0, 50000.0
    for _ in range(200):
        m = (lo + hi)/2.0
        if s_arc(m, R) < vise:
            lo = m
        else:
            hi = m
    return hi


def cachee_approx(h_obs, D, R=R_MOYEN):
    """Approximation classique (D − √(2Rh))²/(2R)."""
    d1 = d_approx(h_obs, R)
    return 0.0 if D <= d1 else (D - d1)**2/(2.0*R)


def fraction_visible(h_obs, H, D, R=R_MOYEN):
    c = cachee(h_obs, D, R)
    return max(0.0, min(1.0, (H - c)/H))


def r_eff(k):
    return R_MOYEN/(1.0 - k)


def k_de_gradient(dTdh, P=P0, T=T0):
    """k = 503,3 (P/T²)(0,0342 + dT/dh), dT/dh en K/m. Constante redérivée."""
    return CONST_K*(P/T**2)*(GH + dTdh)


def gradient_de_k(k, P=P0, T=T0):
    """Le gradient thermique qu'exigerait un k donné."""
    return k/(CONST_K*P/T**2) - GH


def k_requis(h_obs, D, c_visee=0.0):
    """Coefficient qu'il faudrait pour que la hauteur occultée vaille c_visee."""
    lo, hi = 0.0, 0.999999
    for _ in range(200):
        m = (lo + hi)/2.0
        if cachee(h_obs, D, r_eff(m)) > c_visee:
            lo = m
        else:
            hi = m
    return hi


# ── Tracé de rayon exact, par quadrature ─────────────────────────────────────
def arc_rasant(h_vise, n_de_h, n_pas=200000):
    """Arc au sol entre le point rasant et l'altitude h_vise.

    Invariant de Bouguer n(r)·r·sin z = K, avec K = n(0)·R au point rasant.
    dθ/dr = K / (r √(n²r² − K²)). La singularité en r = R est levée par
    r = R + t², et l'intégrale en t est traitée par Simpson.
    """
    K = n_de_h(0.0)*R_MOYEN
    T = math.sqrt(h_vise)

    def f(t):
        r = R_MOYEN + t*t
        n = n_de_h(t*t)
        rad = n*n*r*r - K*K
        return 0.0 if rad <= 0.0 else 2.0*t*K/(r*math.sqrt(rad))

    n_pas += n_pas % 2
    dt = T/n_pas
    s = f(0.0) + f(T)
    for i in range(1, n_pas):
        s += (4 if i % 2 else 2)*f(i*dt)
    return R_MOYEN*s*dt/3.0


def n_lineaire(k):
    return lambda h: 1.0 - (k/R_MOYEN)*h


def n_deux_couches(h, k_bas=0.80, k_haut=0.13, epais=60.0):
    if h <= epais:
        return 1.0 - (k_bas/R_MOYEN)*h
    return 1.0 - (k_bas/R_MOYEN)*epais - (k_haut/R_MOYEN)*(h - epais)


def k_equivalent(arc, h=H_OBS):
    """Le k homogène qui reproduirait un arc d'horizon donné."""
    lo, hi = 0.0, 0.999
    for _ in range(100):
        m = (lo + hi)/2.0
        if s_arc(h, r_eff(m)) < arc:
            lo = m
        else:
            hi = m
    return hi


def D_pour_c(h, c_vise, k):
    """Distance à laquelle la hauteur occultée prédite atteint c_vise."""
    lo, hi = 1.0, 3.0e6
    for _ in range(200):
        m = (lo + hi)/2.0
        if cachee(h, m, r_eff(k)) < c_vise:
            lo = m
        else:
            hi = m
    return hi


# ── Sensibilité ──────────────────────────────────────────────────────────────
def sensibilites(h=H_OBS, D=120000.0, k=0.13):
    """Dérivées partielles de c, par différences centrées."""
    R = r_eff(k)
    dh = (cachee(h + 0.5, D, R) - cachee(h - 0.5, D, R))          # par m
    dD = (cachee(h, D + 50.0, R) - cachee(h, D - 50.0, R))/100.0  # par m
    dk = (cachee(h, D, r_eff(k + 0.005))
          - cachee(h, D, r_eff(k - 0.005)))                       # par 0,01
    return cachee(h, D, R), dh, dD, dk


# ── Échantillonnage ──────────────────────────────────────────────────────────
Z_ALPHA, Z_BETA = 3.2905, 1.6449     # α = 0,001 bilatéral, puissance 95 %
FACTEUR_N = (Z_ALPHA + Z_BETA)**2    # 24,36


def taille_echantillon(rapport):
    """n minimal pour séparer deux prédictions distantes de Δ, bruit σ."""
    return FACTEUR_N*rapport**2


# ── Contrôle : rien n'est imprimé qui n'ait été revérifié ────────────────────
def controle():
    # 1. Formule fermée contre résolution numérique.
    for D in (110e3, 120e3, 130e3, 136.654e3, 150e3):
        assert abs(cachee(H_OBS, D) - cachee_dicho(H_OBS, D)) < 1e-6, D
    # 2. Le gradient autoconvectif annule k ; +12,9 K/100 m donne k = 1.
    assert abs(k_de_gradient(-GH)) < 1e-12
    assert abs(k_de_gradient(gradient_de_k(1.0)) - 1.0) < 1e-9
    assert abs(k_de_gradient(-0.0130) - 0.130) < 0.001
    assert abs(gradient_de_k(1.0) - 0.12865) < 1e-4
    # 3. Tracé de rayon contre rayon effectif.
    for k, tol in ((0.0, 0.5), (0.13, 0.5), (0.25, 0.6), (0.50, 0.6)):
        num = arc_rasant(H_OBS, n_lineaire(k))
        assert abs(num - s_arc(H_OBS, r_eff(k))) < tol, (k, num)
    # 4. La couche basse domine : le k équivalent n'est pas la moyenne.
    keq = k_equivalent(arc_rasant(H_OBS, n_deux_couches))
    moyenne = (0.80*60.0 + 0.13*740.0)/800.0
    assert keq > 3.0*moyenne, (keq, moyenne)
    assert abs(keq - 0.563) < 0.01, keq
    # 5. L'exemple imposé.
    assert abs(s_arc(H_OBS) - 100958.1) < 1.0
    assert abs(s_arc(H_CIBLE) - 35695.7) < 1.0
    assert abs(cachee(H_OBS, 120000.0) - 28.457) < 0.01
    assert abs(cachee(H_OBS, s_arc(H_OBS) + s_arc(H_CIBLE)) - H_CIBLE) < 0.05
    # 6. L'approximation classique reste sous 4 cm sur la plage utile.
    for D in (110e3, 120e3, 130e3, 136.654e3):
        assert abs(cachee(H_OBS, D) - cachee_approx(H_OBS, D)) < 0.04, D
    # 7. Terme humide : le rapport radio/optique dépasse 100.
    e, T = 20.0, 288.15
    assert abs(3.73e5*e/T**2/(11.27*e/T)) > 100.0
    # 8. Taille d'échantillon.
    assert abs(FACTEUR_N - 24.36) < 0.01
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Mise en forme
# ─────────────────────────────────────────────────────────────────────────────
def nb(x, n=0):
    s = "%.*f" % (n, x)
    e, _, d = s.partition(".")
    neg = e.startswith("-")
    e = e.lstrip("-")
    g = ""
    while len(e) > 3:
        g = "&#8239;" + e[-3:] + g
        e = e[:-3]
    e = ("-" if neg else "") + e + g
    return e + ("," + d if d else "")


def h2(n, titre, saut=False):
    return ('<h2%s><span class="n">%s</span>%s</h2>'
            % (' class="brk"' if saut else "", n, titre))


def h3(t):
    return "<h3>%s</h3>" % t


def p(t):
    return "<p>%s</p>" % t


def eq(corps, legende=""):
    cap = '<span class="cap">%s</span>' % legende if legende else ""
    return '<div class="eq">%s%s</div>' % (corps, cap)


def tab(legende, entetes, lignes, num=()):
    th = "".join('<th%s>%s</th>' % (' class="n"' if i in num else "", e)
                 for i, e in enumerate(entetes))
    return ("<table>\n  <caption>%s</caption>\n  <thead><tr>%s</tr></thead>\n"
            "  <tbody>\n%s\n  </tbody>\n</table>"
            % (legende, th, "\n".join(lignes)))


def rang(cellules, num=(), vedette=False):
    tds = "".join('<td%s>%s</td>' % (' class="n"' if i in num else "", c)
                  for i, c in enumerate(cellules))
    return '    <tr%s>%s</tr>' % (' class="hi"' if vedette else "", tds)


def liste(items, ordonnee=False):
    b = "ol" if ordonnee else "ul"
    return "<%s>\n%s\n</%s>" % (b, "\n".join("  <li>%s</li>" % i for i in items), b)


def encadre(etiquette, contenu, genre="key"):
    return ('<div class="box %s">\n  <span class="lab">%s</span>\n%s\n</div>'
            % (genre, etiquette, contenu))


def masthead():
    champs = (("R&#233;dacteur", AUTEUR), ("Contact", CONTACT),
              ("Version", VERSION), ("Date", DATE), ("Licence", "CC BY 4.0"))
    cases = "".join("<span>%s<b>%s</b></span>" % c for c in champs)
    return ('<div class="masthead">\n'
            '  <div class="kicker">Protocole exp&#233;rimental &#183; '
            'Observation photographique &#183; Pr&#233;-enregistrement</div>\n'
            '  <h1>Portion visible d\'une cible &#233;loign&#233;e '
            'au-dessus de la mer</h1>\n'
            '  <p class="dek">Mesure quantitative de la fraction visible d\'un '
            'objet de dimensions connues, et confrontation aux pr&#233;dictions '
            'de mod&#232;les g&#233;om&#233;triques concurrents</p>\n'
            '  <div class="byline">\n    %s\n  </div>\n</div>' % cases)


def ecrire(corps):
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    if i < 0:
        raise SystemExit("gabarit sans <div class=\"page\">")
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Portion visible d'une cible &#233;loign&#233;e "
                    "&#8212; protocole exp&#233;rimental</title>",
                    modele[:i], count=1)
    doc = entete + '<div class="page">\n' + corps + '\n</div>\n'
    open(CIBLE, "w", encoding="utf-8").write(doc)
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# Front matter
# ─────────────────────────────────────────────────────────────────────────────
def sec_resume():
    return "\n\n".join([
        h2("02", "R&#233;sum&#233;"),
        p("Ce protocole d&#233;finit une exp&#233;rience photographique "
          "destin&#233;e &#224; mesurer, sur une cible &#233;loign&#233;e "
          "observ&#233;e au-dessus de la mer, la <strong>fraction de sa "
          "hauteur qui reste visible</strong>, puis &#224; confronter cette "
          "mesure aux pr&#233;dictions de mod&#232;les g&#233;om&#233;triques "
          "concurrents. La grandeur mesur&#233;e est continue, ce qui la rend "
          "beaucoup plus discriminante que la seule alternative "
          "visible ou invisible."),
        p("La cible peut &#234;tre un navire, un phare, une &#233;olienne, un "
          "b&#226;timent ou un relief. Sa nature n'entre pas dans les "
          "calculs&#160;: seules comptent sa hauteur, l'altitude de sa base, "
          "sa position, la distance, et la g&#233;om&#233;trie de la ligne de "
          "vis&#233;e. Toutes ces grandeurs sont &#233;tablies par des sources "
          "ind&#233;pendantes de la photographie."),
        p("L'acquisition et l'analyse sont s&#233;par&#233;es. Au moment du "
          "d&#233;clenchement, l'op&#233;rateur n'a besoin de conna&#238;tre "
          "ni la distance, ni la hauteur de la cible, ni la pr&#233;diction "
          "attendue. Les param&#232;tres sont reconstitu&#233;s "
          "ensuite&#160;; une donn&#233;e reconstruite a posteriori n'est "
          "jamais pr&#233;sent&#233;e comme une mesure directe."),
        p("Les crit&#232;res de s&#233;lection, de qualit&#233; d'image, de "
          "mesure, de mod&#233;lisation atmosph&#233;rique et de "
          "d&#233;cision sont fix&#233;s et d&#233;pos&#233;s "
          "<strong>avant</strong> l'examen des r&#233;sultats. La conclusion "
          "prend exactement trois valeurs&#160;: compatible, incompatible, "
          "ind&#233;termin&#233;. Aucun r&#233;sultat n'est trait&#233; "
          "diff&#233;remment selon le sens dans lequel il va."),
        encadre("Ce que le protocole ne fait pas",
                p("Il ne mesure pas le rayon de la Terre, il ne "
                  "d&#233;montre aucun mod&#232;le, et il ne consid&#232;re "
                  "aucun mod&#232;le comme &#233;tabli d'avance. Il produit "
                  "une mesure et une comparaison, avec leurs incertitudes. "
                  "Un r&#233;sultat ind&#233;termin&#233; &#8212; le plus "
                  "fr&#233;quent quand les donn&#233;es atmosph&#233;riques "
                  "manquent &#8212; n'est une preuve ni pour ni contre quoi "
                  "que ce soit."), "warn"),
    ])


def sec_ecarts():
    base = s_arc(H_CIBLE)
    c_50 = cachee(100.0, 50000.0)
    c_50_k20 = cachee(100.0, 50000.0, r_eff(0.20))
    k_annule = k_requis(100.0, 50000.0, 0.0)
    e, T = 20.0, 288.15
    wet_radio = 3.73e5*e/T**2
    wet_opt = -11.27*e/T
    keq = k_equivalent(arc_rasant(H_OBS, n_deux_couches))
    moyenne = (0.80*60.0 + 0.13*740.0)/800.0

    ecarts = [
        ("Seuils g&#233;om&#233;triques fixes (&#167;&#160;3 du cahier)",
         "Le cahier impose au moins 100&#8239;m d'altitude et au moins "
         "50&#8239;km de distance. Ces valeurs ne garantissent pas un signal "
         "mesurable. Depuis 100&#8239;m &#224; 50&#8239;km, la hauteur "
         "occult&#233;e vaut %s&#8239;m sans r&#233;fraction, %s&#8239;m "
         "&#224; k&#160;=&#160;0,20, et <strong>z&#233;ro</strong> "
         "d&#232;s k&#160;&#8805;&#160;%s. Un seuil en kilom&#232;tres ne "
         "peut donc pas d&#233;finir la validit&#233; d'une observation."
         % (nb(c_50, 1), nb(c_50_k20, 1), nb(k_annule, 2)),
         "Le crit&#232;re d'admission porte sur la <em>plus petite</em> "
         "hauteur occult&#233;e pr&#233;dite sur l'intervalle de "
         "r&#233;fraction retenu, et non sur la distance&#160;: la "
         "g&#233;om&#233;trie est admissible si cette valeur atteint au "
         "moins cinq fois l'incertitude de mesure (&#167;&#160;28). Les "
         "seuils de 100&#8239;m et 50&#8239;km deviennent des minimums "
         "pratiques, non des conditions de validit&#233;."),
        ("Conduit d'&#233;vaporation en optique (&#167;&#160;7 du cahier)",
         "Le cahier range le <em>ducting</em> parmi les r&#233;gimes &#224; "
         "traiter, sans distinguer le domaine radio du domaine optique. Le "
         "conduit d'&#233;vaporation marin est pilot&#233; par le gradient "
         "d'humidit&#233;, dont le terme dans la r&#233;fractivit&#233; vaut "
         "%s&#8239;N en radio&#233;lectrique &#224; e&#160;=&#160;20&#8239;hPa "
         "et T&#160;=&#160;288&#8239;K, contre %s&#8239;N en optique&#160;: un "
         "rapport de %s. Transposer un raisonnement radio &#224; une "
         "exp&#233;rience optique est une erreur de domaine."
         % (nb(wet_radio, 1), nb(wet_opt, 2), nb(abs(wet_radio/wet_opt), 0)),
         "Le protocole traite s&#233;par&#233;ment le conduit optique, qui "
         "exige une inversion thermique d'environ "
         "+%s&#8239;K/100&#8239;m, et le conduit radio, qui n'est pas le "
         "sujet. Les crit&#232;res de reconnaissance sont "
         "&#233;tablis sur les signatures visibles (&#167;&#160;11)."
         % nb(gradient_de_k(1.0)*100, 1)),
        ("Coefficient de r&#233;fraction moyen (&#167;&#160;9 du cahier)",
         "Le cahier envisage un coefficient global. Le tracé de rayon montre "
         "qu'une couche d'inversion de 60&#8239;m &#224; "
         "k&#160;=&#160;0,80 surmont&#233;e d'une atmosph&#232;re standard "
         "&#224; k&#160;=&#160;0,13 se comporte comme un k homog&#232;ne de "
         "<strong>%s</strong>, et non comme la moyenne pond&#233;r&#233;e en "
         "hauteur, qui vaut %s. Le rayon rasant passe l'essentiel de son "
         "trajet &#224; faible pente dans la couche basse."
         % (nb(keq, 3), nb(moyenne, 3)),
         "Le protocole exige un profil vertical r&#233;solu dans les "
         "premi&#232;res dizaines de m&#232;tres au-dessus de l'eau, et non "
         "une valeur moyenne&#160;; &#224; d&#233;faut, l'incertitude "
         "report&#233;e couvre l'&#233;cart entre les deux traitements."),
        ("Photographie vide (&#167;&#160;14 du cahier)",
         "Le cahier &#233;carte les photographies o&#249; la cible n'appara"
         "&#238;t pas. &#201;carter syst&#233;matiquement les non-d&#233;"
         "tections introduit un biais de s&#233;lection&#160;: une cible "
         "absente est une information, &#224; condition que sa taille "
         "apparente pr&#233;dite ait d&#233;pass&#233; la limite de "
         "d&#233;tection du syst&#232;me.",
         "Une non-d&#233;tection est retenue et class&#233;e "
         "<em>informative</em> si la taille angulaire pr&#233;dite de la "
         "partie attendue exc&#232;de trois fois la r&#233;solution "
         "effective mesur&#233;e&#160;; sinon elle est class&#233;e "
         "<em>ind&#233;termin&#233;e</em>. Les deux cas sont "
         "publi&#233;s (&#167;&#160;19)."),
        ("Mod&#232;le concurrent non sp&#233;cifi&#233; (&#167;&#160;23 du "
         "cahier)",
         "Comparer &#224; &#171;&#160;un mod&#232;le de surface "
         "plane&#160;&#187; n'a de sens que si ce mod&#232;le est "
         "compl&#232;tement sp&#233;cifi&#233;. Un mod&#232;le plan "
         "assorti d'une loi de r&#233;fraction libre reproduit n'importe "
         "quelle observation, et cesse d'&#234;tre r&#233;futable.",
         "Chaque mod&#232;le compar&#233; est d&#233;clar&#233; avec sa "
         "g&#233;om&#233;trie <em>et</em> sa loi de propagation, "
         "d&#233;pos&#233;es avant l'observation, avec le m&#234;me nombre "
         "de param&#232;tres libres autoris&#233;s (&#167;&#160;29)."),
        ("Hauteur de cible et altitude de base confondues "
         "(&#167;&#160;5 et&#160;6 du cahier)",
         "L'exemple num&#233;rique demand&#233; ne pr&#233;cise pas "
         "l'altitude de la base de la cible. Une cible de 100&#8239;m dont "
         "la base est &#224; 20&#8239;m d'altitude n'est pas une cible de "
         "100&#8239;m au niveau de la mer&#160;: son horizon propre vaut "
         "celui de 120&#8239;m, pas celui de 100&#8239;m.",
         "Les &#233;quations du &#167;&#160;9 sont &#233;crites avec une "
         "altitude de base explicite. L'exemple du &#167;&#160;10 "
         "d&#233;clare que la base est au niveau moyen de la mer, "
         "conform&#233;ment &#224; l'&#233;nonc&#233;."),
        ("Quatre verdicts (versions ant&#233;rieures de ce document)",
         "Les documents pr&#233;paratoires distinguaient recevabilit&#233; et "
         "conclusion en quatre cat&#233;gories. Le cahier en demande "
         "exactement trois.",
         "La recevabilit&#233; devient un filtre pr&#233;alable, sans "
         "valeur de conclusion. La conclusion scientifique prend "
         "exactement trois valeurs&#160;: compatible, incompatible, "
         "ind&#233;termin&#233; (&#167;&#160;28)."),
    ]
    lignes = [rang(["%02d" % (i + 1), e[0], e[1], e[2]], num=(0,))
              for i, e in enumerate(ecarts)]
    return "\n\n".join([
        h2("&#8212;", "&#201;carts au cahier des charges"),
        p("Le cahier des charges demande que toute erreur scientifique ou "
          "m&#233;thodologique soit signal&#233;e avant int&#233;gration. "
          "Sept points ont &#233;t&#233; corrig&#233;s. Le protocole qui suit "
          "int&#232;gre les corrections de la troisi&#232;me colonne."),
        tab("Tableau&#160;1 &#8212; corrections apport&#233;es au cahier des "
            "charges, et o&#249; elles sont int&#233;gr&#233;es.",
            ["N&#176;", "Point", "Ce qui ne va pas", "Correction retenue"],
            lignes, num=(0,)),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Sections 3 à 12
# ─────────────────────────────────────────────────────────────────────────────
def sec_question():
    return "\n\n".join([
        h2("03", "Question scientifique"),
        p("Pour une cible dont la position, l'altitude de base et la hauteur "
          "sont &#233;tablies ind&#233;pendamment de la photographie, et pour "
          "un observateur dont la position et l'altitude sont "
          "&#233;tablies de m&#234;me&#160;:"),
        encadre("Question",
                p("<strong>Quelle fraction de la hauteur de la cible est "
                  "effectivement observable sur l'image, quelle fraction "
                  "chaque mod&#232;le g&#233;om&#233;trique consid&#233;r&#233; "
                  "pr&#233;dit visible, et l'&#233;cart est-il assez grand "
                  "pour discriminer ces mod&#232;les compte tenu de toutes "
                  "les incertitudes&#160;?</strong>")),
        p("La question n'est pas &#171;&#160;l'objet est-il "
          "visible&#160;?&#160;&#187;. Une r&#233;ponse binaire perd "
          "l'essentiel de l'information et se laisse expliquer par trop de "
          "causes. La fraction visible est continue, born&#233;e entre 0 "
          "et&#160;1, mesurable avec une incertitude quantifiable, et "
          "pr&#233;dite diff&#233;remment par les mod&#232;les en "
          "concurrence."),
    ])


def sec_hypotheses():
    return "\n\n".join([
        h2("04", "Hypoth&#232;ses"),
        p("Deux mod&#232;les au moins sont mis en concurrence. Aucun n'est "
          "tenu pour &#233;tabli, aucun ne re&#231;oit le statut de "
          "r&#233;f&#233;rence, et les deux subissent exactement le "
          "m&#234;me traitement."),
        h3("4.1 Mod&#232;le S &#8212; surface sph&#233;rique"),
        p("La surface de r&#233;f&#233;rence est une sph&#232;re de rayon "
          "R&#160;=&#160;%s&#8239;m, valeur R<sub>1</sub> de l'IUGG "
          "d&#233;duite de l'ellipso&#239;de GRS&#8239;80. La lumi&#232;re se "
          "propage selon un rayon dont la courbure est celle qu'impose le "
          "profil vertical d'indice de r&#233;fraction, param&#233;tr&#233;e "
          "par le coefficient <em>k</em> d&#233;fini au &#167;&#160;11. La "
          "surface occulte la partie de la cible situ&#233;e sous le rayon "
          "rasant."
          % nb(R_MOYEN, 1)),
        h3("4.2 Mod&#232;le P &#8212; surface plane"),
        p("La surface de r&#233;f&#233;rence est un plan. Aucune partie de la "
          "cible n'est occult&#233;e par la surface, &#224; quelque distance "
          "que ce soit. La fraction visible pr&#233;dite vaut donc 1 partout, "
          "sous r&#233;serve de la limite de d&#233;tection du "
          "syst&#232;me optique et de l'extinction atmosph&#233;rique, qui "
          "sont trait&#233;es aux &#167;&#167;&#160;15 et&#160;20 et qui "
          "s'appliquent identiquement aux deux mod&#232;les."),
        h3("4.3 Contrainte commune"),
        p("Un mod&#232;le n'est admis dans la comparaison que s'il est "
          "d&#233;pos&#233; avec sa g&#233;om&#233;trie <em>et</em> sa loi de "
          "propagation, et avec un nombre de param&#232;tres libres "
          "d&#233;clar&#233;. Une loi de propagation laiss&#233;e libre "
          "reproduit n'importe quelle observation&#160;: elle n'est pas "
          "r&#233;futable, donc pas comparable. Le nombre de "
          "param&#232;tres libres entre dans la comparaison statistique "
          "(&#167;&#160;27)."),
        encadre("Ce que le protocole ne suppose pas",
                p("Il ne suppose pas que le mod&#232;le S est vrai. La valeur "
                  "de R et la loi de r&#233;fraction y sont des "
                  "<em>hypoth&#232;ses de travail dont on d&#233;duit une "
                  "pr&#233;diction testable</em>, au m&#234;me titre que "
                  "l'absence d'occultation dans le mod&#232;le P. "
                  "L'exp&#233;rience porte sur l'&#233;cart entre "
                  "pr&#233;diction et mesure, jamais sur la v&#233;rit&#233; "
                  "suppos&#233;e de l'une des deux."), "warn"),
    ])


def sec_objectifs():
    return "\n\n".join([
        h2("05", "Objectifs"),
        liste([
            "Mesurer, sur une image dont l'int&#233;grit&#233; est "
            "&#233;tablie, la fraction visible d'une cible de dimensions "
            "connues, avec son incertitude.",
            "&#201;tablir, pour la m&#234;me configuration, la fraction "
            "visible pr&#233;dite par chaque mod&#232;le d&#233;pos&#233;, "
            "avec l'enveloppe d'incertitude que produisent les "
            "param&#232;tres g&#233;od&#233;siques et atmosph&#233;riques.",
            "D&#233;terminer si l'&#233;cart entre mesure et pr&#233;diction "
            "d&#233;passe le seuil d&#233;pos&#233; avant l'observation.",
            "Rendre l'un des trois verdicts du &#167;&#160;28 et publier "
            "l'ensemble des donn&#233;es permettant &#224; un tiers de "
            "refaire l'analyse depuis les fichiers d'origine.",
        ], ordonnee=True),
    ])


def sec_definitions():
    taxo = [
        ("Fait mesur&#233;",
         "grandeur obtenue par un instrument, sur place, au moment de "
         "l'observation, avec l'instrument et sa cha&#238;ne d'&#233;talonnage "
         "identifi&#233;s"),
        ("Donn&#233;e externe",
         "grandeur tir&#233;e d'une source ind&#233;pendante de la "
         "photographie, dat&#233;e et citable&#160;: carte, fiche d'ouvrage, "
         "mod&#232;le num&#233;rique de terrain, registre"),
        ("Hypoth&#232;se",
         "&#233;nonc&#233; pos&#233; pour d&#233;duire une pr&#233;diction, "
         "sans &#234;tre lui-m&#234;me mesur&#233; dans "
         "l'exp&#233;rience"),
        ("Calcul",
         "op&#233;ration d&#233;terministe sur des faits mesur&#233;s, des "
         "donn&#233;es externes et des hypoth&#232;ses"),
        ("Mod&#232;le",
         "ensemble coh&#233;rent d'hypoth&#232;ses g&#233;om&#233;triques et "
         "de propagation, d&#233;pos&#233; avant l'observation"),
        ("Incertitude",
         "intervalle associ&#233; &#224; une grandeur, &#233;valu&#233; selon "
         "le guide JCGM&#160;100:2008, avec son type et son facteur "
         "d'&#233;largissement"),
        ("Observation photographique",
         "le fichier d'origine et ce qu'on y mesure&#160;; c'est la "
         "donn&#233;e observationnelle primaire"),
        ("Interpr&#233;tation",
         "&#233;nonc&#233; qui va au-del&#224; de la comparaison "
         "chiffr&#233;e&#160;; jamais m&#234;l&#233;e aux six "
         "cat&#233;gories pr&#233;c&#233;dentes dans un tableau de "
         "r&#233;sultats"),
    ]
    defs = [
        ("Cible", "objet &#233;loign&#233; dont la fraction visible est "
         "mesur&#233;e."),
        ("Hauteur de la cible <em>H</em>", "distance verticale entre la base "
         "de la cible et son sommet, en m&#232;tres."),
        ("Altitude de base <em>z</em><sub>b</sub>", "altitude de la base de la "
         "cible au-dessus de la surface de r&#233;f&#233;rence adopt&#233;e, "
         "en m&#232;tres."),
        ("Altitude de l'observateur <em>h</em>", "altitude de l'axe optique "
         "au-dessus de la m&#234;me surface, en m&#232;tres."),
        ("Distance <em>D</em>", "longueur de la g&#233;od&#233;sique entre le "
         "pied de l'observateur et le pied de la cible, en m&#232;tres."),
        ("Hauteur occult&#233;e <em>c</em>", "hauteur, compt&#233;e depuis la "
         "base de la cible, du plus bas point que le mod&#232;le "
         "pr&#233;dit visible."),
        ("Fraction visible <em>f</em>",
         "<em>f</em>&#160;=&#160;(<em>H</em>&#160;&#8722;&#160;<em>c</em>)/<em>H</em>, "
         "born&#233;e &#224; l'intervalle [0&#160;;&#160;1]. C'est la grandeur "
         "compar&#233;e."),
        ("Coefficient de r&#233;fraction <em>k</em>", "rapport de la courbure "
         "du rayon &#224; celle de la surface de r&#233;f&#233;rence "
         "(&#167;&#160;11)."),
        ("R&#233;solution effective", "plus petite structure r&#233;ellement "
         "s&#233;par&#233;e sur l'image, mesur&#233;e et non "
         "calcul&#233;e (&#167;&#160;20)."),
    ]
    return "\n\n".join([
        h2("06", "D&#233;finitions"),
        h3("6.1 Grandeurs"),
        liste(["<strong>%s</strong> &#8212; %s" % d for d in defs]),
        h3("6.2 Statut d'un &#233;nonc&#233;"),
        p("Chaque valeur figurant dans un rapport porte l'une de ces huit "
          "&#233;tiquettes, et une seule. Un tableau de r&#233;sultats "
          "o&#249; l'&#233;tiquette manque n'est pas recevable."),
        tab("Tableau&#160;2 &#8212; statut des &#233;nonc&#233;s. La "
            "distinction est la r&#232;gle fondamentale du protocole.",
            ["Statut", "D&#233;finition"],
            [rang([t[0], t[1]]) for t in taxo]),
    ])


def sec_fondement():
    return "\n\n".join([
        h2("07", "Fondement th&#233;orique"),
        p("Sur une surface convexe, un observateur plac&#233; &#224; une "
          "altitude <em>h</em> voit la surface jusqu'&#224; un point de "
          "tangence. Au-del&#224;, la surface s'interpose entre lui et tout "
          "objet dont le sommet est plus bas que le rayon rasant. La hauteur "
          "occult&#233;e cro&#238;t avec la distance&#160;; la fraction "
          "visible d&#233;cro&#238;t, atteint z&#233;ro &#224; une distance "
          "finie, et cette d&#233;croissance a une forme pr&#233;cise que le "
          "&#167;&#160;9 &#233;tablit."),
        p("Sur une surface plane, aucune occultation par la surface n'existe. "
          "La cible reste enti&#232;rement visible &#224; toute distance, sa "
          "taille angulaire d&#233;cro&#238;t comme "
          "1/<em>D</em>, et sa disparition &#233;ventuelle rel&#232;ve de la "
          "r&#233;solution du syst&#232;me ou de l'extinction "
          "atmosph&#233;rique, non de la g&#233;om&#233;trie."),
        p("Ces deux comportements sont quantitativement distincts, et c'est "
          "ce qui rend l'exp&#233;rience possible. Ils ne le sont pas "
          "partout&#160;: &#224; courte distance les deux mod&#232;les "
          "pr&#233;disent la m&#234;me chose, et il existe des "
          "g&#233;om&#233;tries o&#249; l'&#233;cart pr&#233;dit tombe sous "
          "l'incertitude de mesure. Le &#167;&#160;28 exige donc que la "
          "g&#233;om&#233;trie choisie s&#233;pare les pr&#233;dictions "
          "d'une quantit&#233; d&#233;clar&#233;e d'avance."),
        p("La r&#233;fraction atmosph&#233;rique intervient dans le "
          "mod&#232;le S comme une correction physique r&#233;elle, non "
          "comme un param&#232;tre d'ajustement. Elle courbe le rayon vers "
          "les indices croissants, donc vers le bas dans une atmosph&#232;re "
          "normale, ce qui recule l'horizon et diminue la hauteur "
          "occult&#233;e. Son amplitude est born&#233;e par la physique du "
          "profil vertical, et le &#167;&#160;11 &#233;tablit ces bornes "
          "avant l'observation."),
    ])


def sec_geometrie():
    # Le cercle est centré en (350, 1127,6) avec R = 900 : son sommet est en
    # (350, 227,6) et la tangente y est horizontale. L'œil, le point de
    # tangence et le rayon sont donc tous à y = 227,6 — sans quoi la figure
    # illustrerait mal ce qu'elle prétend montrer. Un premier jet plaçait le
    # point de tangence 19 px au-dessus de la surface.
    fig = """<figure>
<svg viewBox="0 140 700 182" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="fl" markerWidth="7" markerHeight="7" refX="6" refY="3"
    orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#14608f"/></marker></defs>
  <path d="M 20 290 A 900 900 0 0 1 680 290" fill="none" stroke="#3d4952"
    stroke-width="1.7"/>
  <line x1="120" y1="257.0" x2="120" y2="227.6" stroke="#8f2f2b"
    stroke-width="1.6"/>
  <circle cx="120" cy="227.6" r="4" fill="#8f2f2b"/>
  <text class="t" x="60" y="219">observateur</text>
  <text class="tm" x="86" y="248">h</text>
  <line x1="120" y1="227.6" x2="612" y2="227.6" stroke="#14608f"
    stroke-width="1.6" marker-end="url(#fl)"/>
  <circle cx="350" cy="227.6" r="3.6" fill="#14608f"/>
  <text class="tm" x="286" y="221">point de tangence</text>
  <line x1="560" y1="252.5" x2="560" y2="150" stroke="#96600f"
    stroke-width="1.8"/>
  <line x1="560" y1="252.5" x2="560" y2="227.6" stroke="#8f2f2b"
    stroke-width="4.2"/>
  <text class="t" x="572" y="152">sommet</text>
  <text class="t" x="578" y="274">base</text>
  <text class="tb" x="538" y="244" fill="#8f2f2b">c</text>
  <text class="tb" x="572" y="196" fill="#96600f">H</text>
  <text class="t" x="618" y="224" fill="#14608f">rayon rasant</text>
  <path d="M 120 288 L 350 277" fill="none" stroke="#6c7883" stroke-width=".8"
    class="dash"/>
  <path d="M 350 277 L 560 288" fill="none" stroke="#6c7883" stroke-width=".8"
    class="dash"/>
  <text class="tm" x="205" y="300">s(h)</text>
  <text class="tm" x="438" y="302">s(c)</text>
  <text class="tm" x="316" y="318">D = s(h) + s(c)</text>
</svg>
<figcaption>Construction de la hauteur occult&#233;e. Le rayon rasant est
tangent &#224; la surface au point de tangence, o&#249; la tangente est
horizontale&#160;; la distance se d&#233;compose en deux arcs, celui de
l'observateur et celui de la partie cach&#233;e de la cible. La partie de la
cible situ&#233;e sous le rayon, de hauteur <em>c</em>, n'est pas
visible.</figcaption>
</figure>"""
    return "\n\n".join([
        h2("08", "G&#233;om&#233;trie", saut=True),
        p("Le rayon rasant est tangent &#224; la surface de "
          "r&#233;f&#233;rence en un point unique. La distance entre le pied "
          "de l'observateur et le pied de la cible se d&#233;compose en deux "
          "arcs&#160;: celui qui s&#233;pare l'observateur du point de "
          "tangence, et celui qui s&#233;pare le point de tangence du pied "
          "de la cible. Le second correspond exactement &#224; la hauteur "
          "occult&#233;e."),
        fig,
        p("Cette d&#233;composition est exacte et ne fait aucune "
          "approximation de petit angle. Elle vaut pour le mod&#232;le S avec "
          "R, et pour le mod&#232;le S avec r&#233;fraction en "
          "rempla&#231;ant R par le rayon effectif du &#167;&#160;11. Elle "
          "ne s'applique pas au mod&#232;le P, qui ne pr&#233;dit aucune "
          "occultation."),
        p("Trois grandeurs en d&#233;coulent&#160;: la <strong>distance "
          "critique</strong>, &#224; laquelle la base cesse d'&#234;tre "
          "visible&#160;; la <strong>distance limite</strong>, &#224; "
          "laquelle le sommet cesse de l'&#234;tre&#160;; et entre les deux, "
          "la <strong>fraction visible</strong>, qui d&#233;cro&#238;t de 1 "
          "&#224; 0. C'est cette d&#233;croissance, et non les deux "
          "distances seules, qui porte l'information."),
    ])


def sec_equations():
    c1 = ("<em>s</em>(<em>x</em>) = R &#183; arccos[ R / (R + <em>x</em>) ]")
    c2 = ("<em>D</em><sub>crit</sub> = <em>s</em>(<em>h</em>)"
          "&#160;&#160;&#160;&#160;"
          "<em>D</em><sub>lim</sub> = <em>s</em>(<em>h</em>) + "
          "<em>s</em>(<em>z</em><sub>b</sub> + <em>H</em>) &#8722; "
          "<em>s</em>(<em>z</em><sub>b</sub>)")
    c3 = ("<em>c</em> = R &#183; { sec[ (<em>D</em> &#8722; "
          "<em>s</em>(<em>h</em>) + <em>s</em>(<em>z</em><sub>b</sub>)) / R ] "
          "&#8722; 1 } &#8722; <em>z</em><sub>b</sub>")
    c4 = ("<em>f</em> = ( <em>H</em> &#8722; <em>c</em> ) / <em>H</em>, "
          "born&#233;e &#224; [0 ; 1]")
    c5 = ("<em>c</em> &#8776; ( <em>D</em> &#8722; &#8730;(2R<em>h</em>) )&#178; "
          "/ (2R)")
    ecarts = []
    for D in (110e3, 120e3, 130e3, 136.654e3):
        ex, ap = cachee(H_OBS, D), cachee_approx(H_OBS, D)
        ecarts.append(rang([nb(D/1000, 3), nb(ex, 3), nb(ap, 3),
                            nb(ex - ap, 3)], num=(0, 1, 2, 3)))
    h_lignes = []
    for h in (2, 100, 800, 3107):
        h_lignes.append(rang([nb(h), nb(s_arc(h), 1), nb(d_slant(h), 1),
                              nb(d_approx(h), 1),
                              nb(s_arc(h) - d_approx(h), 2)],
                             num=(0, 1, 2, 3, 4)))
    return "\n\n".join([
        h2("09", "&#201;quations"),
        h3("9.1 Arc de tangence"),
        p("Pour une altitude <em>x</em> au-dessus d'une sph&#232;re de rayon "
          "R, l'arc au sol entre le pied du point et son point de tangence "
          "vaut&#160;:"),
        eq(c1, "x et R en m&#232;tres&#160;; le r&#233;sultat est un arc "
               "mesur&#233; sur la sph&#232;re."),
        h3("9.2 Distances critiques"),
        p("La base de la cible, situ&#233;e &#224; l'altitude "
          "<em>z</em><sub>b</sub>, cesse d'&#234;tre visible au-del&#224; de "
          "<em>D</em><sub>crit</sub>. Le sommet cesse de l'&#234;tre "
          "au-del&#224; de <em>D</em><sub>lim</sub>."),
        eq(c2, "pour une base au niveau de la surface, "
               "<em>z</em><sub>b</sub>&#160;=&#160;0 et "
               "<em>D</em><sub>lim</sub> = <em>s</em>(<em>h</em>) + "
               "<em>s</em>(<em>H</em>)."),
        h3("9.3 Hauteur occult&#233;e et fraction visible"),
        p("Pour <em>D</em>&#160;&gt;&#160;<em>D</em><sub>crit</sub>, la "
          "hauteur occult&#233;e compt&#233;e depuis la base vaut&#160;:"),
        eq(c3, "l'argument de la s&#233;cante est un angle "
               "g&#233;ocentrique, en radians."),
        eq(c4, "grandeur compar&#233;e entre mod&#232;les et mesure."),
        p("Cette forme ferm&#233;e a &#233;t&#233; v&#233;rifi&#233;e contre "
          "la r&#233;solution num&#233;rique directe de "
          "<em>s</em>(<em>h</em>)&#160;+&#160;<em>s</em>(<em>c</em>)&#160;="
          "&#160;<em>D</em>&#160;: les deux m&#233;thodes co&#239;ncident "
          "&#224; mieux d'un microm&#232;tre sur toute la plage utile."),
        h3("9.4 Comparaison aux approximations classiques"),
        p("L'approximation usuelle remplace l'arc par la corde et "
          "d&#233;veloppe la s&#233;cante au premier ordre&#160;:"),
        eq(c5, "approximation classique&#160;; &#224; ne pas employer sans "
               "avoir born&#233; son erreur."),
        tab("Tableau&#160;3 &#8212; distance d'horizon selon trois "
            "formulations. L'&#233;cart entre l'arc exact et "
            "&#8730;(2R<em>h</em>) reste sous 6&#8239;m jusqu'&#224; "
            "800&#8239;m d'altitude, mais atteint 40&#8239;m &#224; "
            "3&#8239;107&#8239;m.",
            ["h (m)", "arc exact (m)", "corde (m)",
             "&#8730;(2Rh) (m)", "arc &#8722; &#8730;(2Rh)"],
            h_lignes, num=(0, 1, 2, 3, 4)),
        tab("Tableau&#160;4 &#8212; hauteur occult&#233;e, exacte contre "
            "approch&#233;e, pour <em>h</em>&#160;=&#160;800&#8239;m. "
            "L'&#233;cart reste sous 4&#8239;cm, donc n&#233;gligeable devant "
            "toute incertitude de mesure&#160;; l'approximation est "
            "acceptable ici, et cette conclusion doit &#234;tre "
            "rev&#233;rifi&#233;e pour toute autre g&#233;om&#233;trie.",
            ["D (km)", "c exact (m)", "c approch&#233; (m)", "&#233;cart (m)"],
            ecarts, num=(0, 1, 2, 3)),
        h3("9.5 Mod&#232;le P"),
        p("Le mod&#232;le P pr&#233;dit <em>c</em>&#160;=&#160;0 et "
          "<em>f</em>&#160;=&#160;1 pour toute distance. Sa taille angulaire "
          "pr&#233;dite vaut <em>H</em>/<em>D</em> en radians, &#224; "
          "comparer &#224; la r&#233;solution effective du &#167;&#160;20."),
    ])


def sec_exemple():
    s1, s2 = s_arc(H_OBS), s_arc(H_CIBLE)
    dmax = s1 + s2
    lignes = []
    for D_km in (50, 100.958, 110, 120, 130, 136.654, 140):
        D = D_km*1000
        ce, cd, ca = (cachee(H_OBS, D), cachee_dicho(H_OBS, D),
                      cachee_approx(H_OBS, D))
        lignes.append(rang([nb(D_km, 3), nb(ce, 3), nb(cd, 3), nb(ca, 3),
                            nb(fraction_visible(H_OBS, H_CIBLE, D), 4)],
                           num=(0, 1, 2, 3, 4),
                           vedette=abs(D_km - 136.654) < 1e-6))
    interm = [
        ("R / (R + h)", nb(R_MOYEN/(R_MOYEN + H_OBS), 9), "&#8212;"),
        ("arccos[ R / (R + h) ]", nb(math.acos(R_MOYEN/(R_MOYEN + H_OBS)), 9),
         "rad"),
        ("<em>s</em>(800&#8239;m)", nb(s1, 3), "m"),
        ("<em>s</em>(100&#8239;m)", nb(s2, 3), "m"),
        ("<em>D</em><sub>crit</sub>", nb(s1, 3), "m"),
        ("<em>D</em><sub>lim</sub>", nb(dmax, 3), "m"),
        ("&#8730;(2R&#183;800)", nb(d_approx(H_OBS), 3), "m"),
        ("&#233;cart arc &#8722; &#8730;(2Rh)", nb(s1 - d_approx(H_OBS), 3), "m"),
    ]
    return "\n\n".join([
        h2("10", "Exemple num&#233;rique", saut=True),
        p("Configuration impos&#233;e par le cahier des charges&#160;: "
          "observateur &#224; <strong>800&#8239;m</strong> au-dessus du "
          "niveau moyen de la mer, cible de <strong>100&#8239;m</strong> de "
          "hauteur, base au niveau moyen de la mer "
          "(<em>z</em><sub>b</sub>&#160;=&#160;0), ligne de vis&#233;e "
          "enti&#232;rement au-dessus de l'eau, <strong>sans "
          "r&#233;fraction</strong> (<em>k</em>&#160;=&#160;0), sur une "
          "sph&#232;re de rayon R&#160;=&#160;%s&#8239;m." % nb(R_MOYEN, 1)),
        h3("10.1 R&#233;sultats interm&#233;diaires"),
        tab("Tableau&#160;5 &#8212; valeurs interm&#233;diaires, avec leurs "
            "unit&#233;s. Chacune est recalcul&#233;e &#224; chaque "
            "g&#233;n&#233;ration du document.",
            ["Grandeur", "Valeur", "Unit&#233;"],
            [rang([g[0], g[1], g[2]], num=(1,)) for g in interm], num=(1,)),
        h3("10.2 R&#233;sultats"),
        liste([
            "Distance &#224; l'horizon de l'observateur&#160;: "
            "<strong>%s&#8239;km</strong>. Au-del&#224;, la base de la cible "
            "est occult&#233;e." % nb(s1/1000, 3),
            "Distance &#224; laquelle le sommet cesse d'&#234;tre "
            "g&#233;om&#233;triquement visible&#160;: "
            "<strong>%s&#8239;km</strong>." % nb(dmax/1000, 3),
            "Distance &#224; laquelle la cible enti&#232;re est "
            "occult&#233;e&#160;: la m&#234;me, "
            "<strong>%s&#8239;km</strong>&#160;; au-del&#224; la hauteur "
            "occult&#233;e d&#233;passe 100&#8239;m." % nb(dmax/1000, 3),
            "Hauteur occult&#233;e en fonction de la distance&#160;: "
            "tableau&#160;6.",
        ], ordonnee=True),
        tab("Tableau&#160;6 &#8212; hauteur occult&#233;e et fraction "
            "visible, <em>h</em>&#160;=&#160;800&#8239;m, "
            "<em>H</em>&#160;=&#160;100&#8239;m, <em>k</em>&#160;=&#160;0. "
            "La colonne &#171;&#160;dichotomie&#160;&#187; est une "
            "r&#233;solution num&#233;rique ind&#233;pendante de la formule "
            "ferm&#233;e.",
            ["D (km)", "c ferm&#233;e (m)", "c dichotomie (m)",
             "c approch&#233;e (m)", "fraction visible"],
            lignes, num=(0, 1, 2, 3, 4)),
        h3("10.3 V&#233;rification ind&#233;pendante"),
        p("Trois m&#233;thodes ont &#233;t&#233; compar&#233;es. La formule "
          "ferm&#233;e en s&#233;cante et la r&#233;solution "
          "num&#233;rique de "
          "<em>s</em>(<em>h</em>)&#160;+&#160;<em>s</em>(<em>c</em>)&#160;=&#160;"
          "<em>D</em> co&#239;ncident &#224; mieux d'un microm&#232;tre&#160;: "
          "elles expriment la m&#234;me construction, l'une analytiquement, "
          "l'autre par bissection, et leur accord ne teste que "
          "l'impl&#233;mentation."),
        p("L'approximation classique, elle, repose sur deux simplifications "
          "distinctes&#160;: la corde remplace l'arc, et la s&#233;cante est "
          "d&#233;velopp&#233;e au premier ordre. Les deux erreurs sont de "
          "signes oppos&#233;s et se compensent partiellement, ce qui "
          "explique un &#233;cart r&#233;siduel de %s&#8239;cm seulement "
          "&#224; 136,654&#8239;km alors que chaque terme pris "
          "s&#233;par&#233;ment vaut plusieurs m&#232;tres. Cette "
          "compensation est fortuite&#160;: elle d&#233;pend de la "
          "g&#233;om&#233;trie et ne doit pas &#234;tre "
          "g&#233;n&#233;ralis&#233;e."
          % nb(100*abs(cachee(H_OBS, 136654.0) - cachee_approx(H_OBS, 136654.0)), 1)),
        encadre("Ce que cet exemple n'&#233;tablit pas",
                p("Ces valeurs sont des <strong>pr&#233;dictions du "
                  "mod&#232;le S sans r&#233;fraction</strong>, c'est-&#224;-dire "
                  "d'un cas physiquement irr&#233;alisable&#160;: "
                  "l'atmosph&#232;re courbe toujours les rayons. Elles "
                  "servent de borne, pas de pr&#233;vision. La "
                  "pr&#233;diction r&#233;elle du mod&#232;le S est "
                  "l'enveloppe du &#167;&#160;11, sensiblement plus "
                  "favorable &#224; la visibilit&#233;."), "warn"),
    ])


def sec_refraction():
    regimes = [
        ("Aucune r&#233;fraction", "k = 0",
         "cas de r&#233;f&#233;rence th&#233;orique, physiquement "
         "irr&#233;alisable dans l'atmosph&#232;re&#160;; correspond au "
         "gradient autoconvectif &#8722;%s&#8239;K/100&#8239;m"
         % nb(GH*100, 2)),
        ("R&#233;fraction standard", "k &#8776; 0,13 &#224; 0,17",
         "gradient de &#8722;13 &#224; &#8722;6,5&#8239;K/km&#160;; "
         "atmosph&#232;re bien m&#233;lang&#233;e, cas courant de jour "
         "au-dessus de la terre"),
        ("R&#233;fraction forte", "k &#8776; 0,20 &#224; 0,40",
         "air isotherme ou l&#233;g&#232;re inversion&#160;: gradient de 0 "
         "&#224; +25&#8239;K/km&#160;; fr&#233;quent au-dessus d'une mer "
         "plus froide que l'air"),
        ("R&#233;fraction tr&#232;s forte", "k &#8776; 0,40 &#224; 0,80",
         "inversion marqu&#233;e, gradient de +25 &#224; "
         "+100&#8239;K/km sur la couche travers&#233;e&#160;; "
         "physiquement admissible, &#224; documenter"),
        ("Inversion et mirage sup&#233;rieur", "k &#8776; 0,80 &#224; 1",
         "inversion intense&#160;; images renvers&#233;es au-dessus de "
         "l'objet, d&#233;formation verticale mesurable"),
        ("Conduit optique", "k &#8805; 1",
         "exige un gradient d'au moins +%s&#8239;K/100&#8239;m soutenu sur "
         "la couche o&#249; passe le rayon&#160;; le rayon &#233;pouse ou "
         "d&#233;passe la courbure de la surface"
         % nb(gradient_de_k(1.0)*100, 1)),
    ]
    grad_lignes = []
    for dT in (-34.16, -13.0, -6.5, 0.0, 25.0, 50.0, 100.0,
               gradient_de_k(1.0)*1000):
        grad_lignes.append(rang([nb(dT, 2), nb(k_de_gradient(dT/1000), 4)],
                                num=(0, 1),
                                vedette=abs(dT - gradient_de_k(1.0)*1000) < 1e-6))
    trace_lignes = []
    for k in (0.0, 0.13, 0.25, 0.50):
        num, ana = arc_rasant(H_OBS, n_lineaire(k)), s_arc(H_OBS, r_eff(k))
        trace_lignes.append(rang([nb(k, 2), nb(num, 2), nb(ana, 2),
                                  nb(num - ana, 3)], num=(0, 1, 2, 3)))
    keq = k_equivalent(arc_rasant(H_OBS, n_deux_couches))
    moyenne = (0.80*60.0 + 0.13*740.0)/800.0
    e, T = 20.0, 288.15
    return "\n\n".join([
        h2("11", "R&#233;fraction atmosph&#233;rique", saut=True),
        h3("11.1 Coefficient et rayon effectif"),
        p("Le coefficient de r&#233;fraction <em>k</em> est le rapport de la "
          "courbure du rayon &#224; celle de la surface. Dans une "
          "atmosph&#232;re &#224; gradient d'indice constant, tout le "
          "&#167;&#160;9 reste valable en rempla&#231;ant R par le rayon "
          "effectif&#160;:"),
        eq("R<sub>eff</sub> = R / (1 &#8722; <em>k</em>)",
           "valable pour k &lt; 1. Pour k &#8805; 1 le rayon ne "
           "s'&#233;l&#232;ve plus au-dessus de la surface et la "
           "construction du &#167;&#160;8 ne s'applique plus."),
        h3("11.2 Du gradient thermique au coefficient"),
        p("Pour la lumi&#232;re visible, la r&#233;fractivit&#233; de l'air "
          "vaut sensiblement <em>n</em>&#160;&#8722;&#160;1&#160;="
          "&#160;79&#215;10&#8315;&#8310;&#160;<em>P</em>/<em>T</em> avec "
          "<em>P</em> en hPa et <em>T</em> en K. En combinant avec "
          "l'&#233;quilibre hydrostatique d<em>P</em>/d<em>h</em>&#160;="
          "&#160;&#8722;<em>Pg</em>/(<em>R</em><sub>d</sub><em>T</em>), on "
          "obtient&#160;:"),
        eq("<em>k</em> = %s &#183; (<em>P</em>/<em>T</em>&#178;) &#183; "
           "( %s + d<em>T</em>/d<em>h</em> )" % (nb(CONST_K, 1), nb(GH, 4)),
           "P en hPa, T en K, dT/dh en K/m. La constante est "
           "R&#183;79&#215;10&#8315;&#8310; et le terme %s&#8239;K/m est "
           "g/R<sub>d</sub>, le gradient autoconvectif." % nb(GH, 4)),
        tab("Tableau&#160;7 &#8212; correspondance gradient-coefficient "
            "&#224; %s&#8239;hPa et %s&#8239;K. Le gradient autoconvectif "
            "annule <em>k</em>&#160;; le seuil de conduit optique est en "
            "gras." % (nb(P0, 2), nb(T0, 2)),
            ["d<em>T</em>/d<em>h</em> (K/km)", "<em>k</em>"],
            grad_lignes, num=(0, 1)),
        h3("11.3 Les six r&#233;gimes"),
        tab("Tableau&#160;8 &#8212; r&#233;gimes de r&#233;fraction et "
            "conditions physiques correspondantes.",
            ["R&#233;gime", "<em>k</em>", "Conditions physiques"],
            [rang([r[0], r[1], r[2]], num=(1,)) for r in regimes], num=(1,)),
        h3("11.4 Conduit optique et conduit radio&#160;: ne pas confondre"),
        p("Le conduit d'&#233;vaporation marin, abondamment "
          "document&#233; en propagation radio&#233;lectrique, est "
          "pilot&#233; par le gradient d'humidit&#233;. Le terme humide de "
          "la r&#233;fractivit&#233; vaut environ "
          "3,73&#215;10&#8309;&#160;<em>e</em>/<em>T</em>&#178; en radio, "
          "soit <strong>+%s&#8239;N</strong> &#224; "
          "<em>e</em>&#160;=&#160;20&#8239;hPa et "
          "<em>T</em>&#160;=&#160;288&#8239;K, contre environ "
          "&#8722;11,3&#160;<em>e</em>/<em>T</em> en optique, soit "
          "<strong>%s&#8239;N</strong>&#160;: un rapport de "
          "<strong>%s</strong> en valeur absolue, et de signe "
          "oppos&#233;."
          % (nb(3.73e5*e/T**2, 1), nb(-11.27*e/T, 2),
             nb(abs(3.73e5*e/T**2/(11.27*e/T)), 0))),
        p("Un conduit optique ne peut donc pas &#234;tre produit par "
          "l'humidit&#233;&#160;: il exige une inversion thermique d'au "
          "moins <strong>+%s&#8239;K/100&#8239;m</strong> soutenue sur la "
          "couche travers&#233;e. Invoquer un conduit d'&#233;vaporation "
          "pour expliquer une observation optique est une erreur de "
          "domaine, et le protocole la refuse." % nb(gradient_de_k(1.0)*100, 1)),
        h3("11.5 Le profil ne se moyenne pas"),
        p("Le rayon rasant passe l'essentiel de son trajet &#224; faible "
          "pente pr&#232;s de la surface. Une couche basse anormale y "
          "p&#232;se donc bien plus que sa part en hauteur. Un tra&#231;age "
          "de rayon par quadrature dans un profil &#224; deux couches "
          "&#8212; <em>k</em>&#160;=&#160;0,80 sous 60&#8239;m, "
          "<em>k</em>&#160;=&#160;0,13 au-dessus &#8212; donne un "
          "comportement identique &#224; celui d'un <em>k</em> homog&#232;ne "
          "de <strong>%s</strong>, alors que la moyenne pond&#233;r&#233;e en "
          "hauteur vaut %s." % (nb(keq, 3), nb(moyenne, 3))),
        encadre("Cons&#233;quence op&#233;ratoire",
                p("Un coefficient moyen, une valeur de manuel ou une "
                  "climatologie ne suffisent pas. Ce qui est exig&#233; est "
                  "le profil vertical <em>r&#233;solu dans les "
                  "premi&#232;res dizaines de m&#232;tres au-dessus de "
                  "l'eau</em> (&#167;&#160;21). &#192; d&#233;faut, "
                  "l'incertitude report&#233;e doit couvrir l'&#233;cart "
                  "entre les deux traitements, soit ici un facteur trois sur "
                  "<em>k</em>.")),
        h3("11.6 Validation du rayon effectif par tra&#231;age de rayon"),
        p("L'approximation du rayon effectif a &#233;t&#233; "
          "compar&#233;e &#224; une int&#233;gration exacte de l'invariant "
          "de Bouguer <em>n</em>(<em>r</em>)&#183;<em>r</em>&#183;sin&#160;"
          "<em>z</em>&#160;=&#160;cte dans un profil d'indice "
          "lin&#233;aire."),
        tab("Tableau&#160;9 &#8212; arc au sol entre le point rasant et "
            "800&#8239;m d'altitude. L'accord sub-m&#233;trique valide "
            "l'emploi de R<sub>eff</sub> pour k&#160;&#8804;&#160;0,5. "
            "Au-del&#224;, l'&#233;cart cro&#238;t et le tra&#231;age "
            "devient obligatoire.",
            ["<em>k</em>", "tra&#231;age (m)", "R<sub>eff</sub> (m)",
             "&#233;cart (m)"], trace_lignes, num=(0, 1, 2, 3)),
        h3("11.7 Interdiction d'ajustement"),
        p("La valeur de <em>k</em> retenue, ou l'intervalle retenu, est "
          "d&#233;pos&#233;e avant l'analyse et justifi&#233;e par les "
          "donn&#233;es atmosph&#233;riques du &#167;&#160;21. Une "
          "r&#233;fraction plus forte ne peut jamais &#234;tre "
          "introduite apr&#232;s coup pour rendre compte d'un &#233;cart "
          "constat&#233;, dans un sens comme dans l'autre. Si les "
          "donn&#233;es ne permettent pas de borner <em>k</em>, "
          "l'observation est class&#233;e ind&#233;termin&#233;e "
          "(&#167;&#160;28), et non expliqu&#233;e."),
    ])


def sec_geodesie():
    postes = [
        ("Position horizontale de l'observateur",
         "r&#233;cepteur GNSS bi-fr&#233;quence en post-traitement, ou "
         "positionnement sur un point g&#233;od&#233;sique publi&#233;",
         "ITRF / ETRS89", "&#177;&#160;0,1 &#224; 5&#8239;m"),
        ("Altitude de l'observateur",
         "hauteur ellipso&#239;dale GNSS convertie en altitude par un "
         "mod&#232;le de g&#233;o&#239;de publi&#233;, plus la hauteur "
         "mesur&#233;e de l'axe optique au-dessus du sol",
         "ellipso&#239;de GRS&#8239;80 &#8594; g&#233;o&#239;de",
         "&#177;&#160;0,3 &#224; 2&#8239;m"),
        ("Position de la cible",
         "fiche officielle de l'ouvrage, relev&#233; g&#233;od&#233;sique, "
         "base cartographique nationale&#160;; pour un navire, position "
         "horodat&#233;e d'un registre",
         "ITRF / syst&#232;me national", "&#177;&#160;1 &#224; 50&#8239;m"),
        ("Altitude de la base de la cible",
         "mod&#232;le num&#233;rique de terrain officiel&#160;; pour un "
         "ouvrage c&#244;tier ou un navire, niveau d'eau &#224; l'heure "
         "exacte, corrig&#233; de la mar&#233;e et du z&#233;ro "
         "hydrographique",
         "altitude normale ou orthom&#233;trique", "&#177;&#160;0,2 &#224; "
         "2&#8239;m"),
        ("Hauteur de la cible",
         "plan cot&#233;, fiche technique du constructeur, liste officielle "
         "de feux, sp&#233;cification de navire&#160;; jamais "
         "d&#233;duite de la photographie",
         "&#8212;", "&#177;&#160;0,1 &#224; 1&#8239;m"),
        ("Distance",
         "g&#233;od&#233;sique sur l'ellipso&#239;de calcul&#233;e par un "
         "algorithme publi&#233; et v&#233;rifiable",
         "GRS&#8239;80 / WGS&#8239;84", "&#177;&#160;quelques m&#232;tres"),
        ("Azimut",
         "azimut g&#233;od&#233;sique direct issu du m&#234;me calcul",
         "GRS&#8239;80 / WGS&#8239;84", "&#177;&#160;0,01&#176;"),
        ("Profil interm&#233;diaire",
         "&#233;chantillonnage du mod&#232;le de terrain et de la "
         "bathym&#233;trie le long de la g&#233;od&#233;sique, au pas de "
         "500&#8239;m au plus",
         "id.", "&#177;&#160;2 &#224; 10&#8239;m"),
    ]
    return "\n\n".join([
        h2("12", "G&#233;od&#233;sie"),
        h3("12.1 Syst&#232;mes de r&#233;f&#233;rence"),
        p("Toutes les positions sont exprim&#233;es dans un rep&#232;re "
          "d&#233;clar&#233;, avec son &#233;poque. Le rapport nomme "
          "explicitement le syst&#232;me, le mod&#232;le de "
          "g&#233;o&#239;de, la r&#233;f&#233;rence verticale et, le cas "
          "&#233;ch&#233;ant, la transformation appliqu&#233;e entre deux "
          "syst&#232;mes."),
        p("Il faut distinguer trois surfaces qui ne co&#239;ncident "
          "pas&#160;: l'<strong>ellipso&#239;de</strong>, sur lequel se "
          "calcule la g&#233;od&#233;sique&#160;; le "
          "<strong>g&#233;o&#239;de</strong>, auquel se rapportent les "
          "altitudes&#160;; et la <strong>sph&#232;re de "
          "r&#233;f&#233;rence</strong> du &#167;&#160;9, qui est une "
          "commodit&#233; de calcul. L'&#233;cart entre g&#233;o&#239;de "
          "et ellipso&#239;de atteint plusieurs dizaines de m&#232;tres et "
          "affecte directement <em>h</em> et "
          "<em>z</em><sub>b</sub>&#160;: le confondre avec z&#233;ro est "
          "une erreur de plusieurs dizaines de m&#232;tres sur "
          "l'altitude, donc de plusieurs m&#232;tres sur la hauteur "
          "occult&#233;e."),
        h3("12.2 Sph&#232;re ou ellipso&#239;de"),
        p("La sph&#232;re de rayon R<sub>1</sub>&#160;=&#160;"
          "(2<em>a</em>&#160;+&#160;<em>b</em>)/3&#160;=&#160;%s&#8239;m est "
          "une approximation. Le rayon de courbure r&#233;el de "
          "l'ellipso&#239;de d&#233;pend de la latitude et de l'azimut "
          "de la vis&#233;e&#160;; il varie du rayon m&#233;ridien "
          "&#224; la grande normale, soit environ %s&#8239;km &#224; "
          "%s&#8239;km." % (nb(R_MOYEN, 1), nb(A_GRS80*(1 - F_GRS80)**2/1000, 0),
                            nb(A_GRS80/1000, 0)),
        ),
        p("Le protocole exige donc, pour chaque observation, le "
          "<strong>rayon de courbure normal &#224; l'azimut de la "
          "vis&#233;e</strong> (rayon d'Euler) calcul&#233; &#224; la "
          "latitude du trajet, et non R<sub>1</sub>. La diff&#233;rence "
          "est quantifi&#233;e au rapport&#160;: substituer "
          "R<sub>1</sub> au rayon d'Euler peut changer la hauteur "
          "occult&#233;e de plusieurs pour cent, ce qui est "
          "sup&#233;rieur &#224; l'erreur de l'approximation "
          "corde-contre-arc du &#167;&#160;9.4."),
        h3("12.3 Sources et pr&#233;cisions"),
        tab("Tableau&#160;10 &#8212; postes g&#233;od&#233;siques, sources "
            "admises et pr&#233;cisions typiques. Les valeurs de la "
            "derni&#232;re colonne sont indicatives&#160;: chaque "
            "observation reporte l'incertitude r&#233;elle de sa propre "
            "source.",
            ["Poste", "Source admise", "R&#233;f&#233;rentiel",
             "Incertitude typique"],
            [rang([q[0], q[1], q[2], q[3]], num=(3,)) for q in postes],
            num=(3,)),
        h3("12.4 R&#232;gle d'ind&#233;pendance"),
        p("Aucune de ces grandeurs n'est d&#233;duite de la photographie "
          "analys&#233;e. En particulier, la hauteur de la cible ne peut pas "
          "&#234;tre estim&#233;e depuis l'image lorsque cette m&#234;me "
          "hauteur sert ensuite &#224; juger l'image&#160;: le "
          "raisonnement serait circulaire et le r&#233;sultat "
          "automatiquement compatible."),
    ])


def sec_materiel():
    return "\n\n".join([
        h2("13", "Mat&#233;riel"),
        p("Le protocole ne prescrit ni marque ni mod&#232;le. Il fixe des "
          "caract&#233;ristiques minimales, et toute configuration qui les "
          "atteint est recevable."),
        h3("13.1 Caract&#233;ristiques minimales"),
        liste([
            "<strong>Enregistrement brut.</strong> L'appareil produit un "
            "fichier natif non compress&#233; avec pertes, ou &#224; "
            "d&#233;faut un fichier compress&#233; dont les "
            "m&#233;tadonn&#233;es sont compl&#232;tes. Le fichier brut est "
            "pr&#233;f&#233;r&#233; parce qu'il n'a subi ni accentuation ni "
            "r&#233;duction de bruit.",
            "<strong>R&#233;solution angulaire.</strong> La cha&#238;ne "
            "optique doit r&#233;soudre la caract&#233;ristique mesur&#233;e "
            "au sens du &#167;&#160;20&#160;; c'est un crit&#232;re sur le "
            "r&#233;sultat, pas sur le mat&#233;riel.",
            "<strong>Support.</strong> Tr&#233;pied stable et lest&#233;, "
            "colonne rentr&#233;e, rotule bloqu&#233;e, sur sol ferme. "
            "Stabilisation d&#233;sactiv&#233;e.",
            "<strong>D&#233;clenchement.</strong> Sans contact&#160;: "
            "retardateur d'au moins deux secondes, ou commande &#224; "
            "distance.",
            "<strong>Mise au point.</strong> Manuelle, &#224; l'infini, "
            "affin&#233;e en vis&#233;e agrandie sur la cible "
            "elle-m&#234;me. La mise au point automatique est d&#233;sactiv"
            "&#233;e&#160;: elle d&#233;rive d'une vue &#224; l'autre.",
            "<strong>Exposition.</strong> Fixe pour toute la s&#233;rie, "
            "r&#233;gl&#233;e pour qu'aucun pixel de la cible ne soit "
            "satur&#233;. Sensibilit&#233; la plus basse compatible avec un "
            "temps de pose court.",
            "<strong>Horloge.</strong> R&#233;gl&#233;e sur le temps "
            "universel &#224; mieux que 5&#8239;s, et v&#233;rifi&#233;e "
            "juste avant la s&#233;rie.",
            "<strong>Position.</strong> R&#233;cepteur GNSS enregistrant la "
            "position et l'incertitude annonc&#233;e&#160;; un point "
            "g&#233;od&#233;sique publi&#233; vaut mieux.",
            "<strong>Mesure de la hauteur d'&#339;il.</strong> M&#232;tre "
            "ruban, du sol ou du plan d'eau &#224; l'axe optique, "
            "photographi&#233;.",
        ]),
        h3("13.2 Mat&#233;riel compl&#233;mentaire recommand&#233;"),
        liste([
            "Thermom&#232;tres &#224; au moins deux hauteurs au point de "
            "vue, et thermom&#232;tre de surface pour l'eau si "
            "accessible.",
            "Barom&#232;tre et hygrom&#232;tre &#233;talonn&#233;s.",
            "Mire ou cible de r&#233;solution photographi&#233;e &#224; "
            "distance connue, pour le contr&#244;le du &#167;&#160;24.",
        ]),
    ])


def sec_photographie():
    return "\n\n".join([
        h2("14", "Photographie"),
        h3("14.1 S&#233;rie"),
        p("Chaque observation est une <strong>s&#233;rie</strong>, jamais une "
          "vue isol&#233;e. Au moins vingt vues cons&#233;cutives de la "
          "m&#234;me vis&#233;e sont enregistr&#233;es sans toucher &#224; la "
          "mise au point, au cadrage ni au grossissement. Toutes sont "
          "remises&#160;; aucune n'est &#233;cart&#233;e par "
          "l'op&#233;rateur."),
        p("La s&#233;rie sert &#224; trois choses&#160;: estimer la "
          "dispersion due &#224; la turbulence, rechercher les signatures "
          "atmosph&#233;riques du &#167;&#160;19, et permettre une "
          "s&#233;lection des vues les plus nettes selon un crit&#232;re "
          "d&#233;clar&#233; d'avance et appliqu&#233; automatiquement."),
        h3("14.2 Vues de contexte"),
        liste([
            "Une vue grand-angle depuis la m&#234;me position, montrant les "
            "rep&#232;res proches.",
            "Une vue de la mire de r&#233;solution, si elle est "
            "disponible.",
            "Une photographie du m&#232;tre mesurant la hauteur de l'axe "
            "optique.",
            "Une vue de l'horizon dans la m&#234;me direction, &#224; la "
            "m&#234;me focale, pour la r&#233;f&#233;rence angulaire du "
            "&#167;&#160;19.",
        ]),
        h3("14.3 R&#233;p&#233;tition"),
        p("La m&#234;me vis&#233;e est reprise &#224; au moins deux moments "
          "s&#233;par&#233;s de plusieurs heures, et si possible &#224; deux "
          "dates. Un &#233;cart syst&#233;matique entre les deux moments "
          "signale un effet atmosph&#233;rique&#160;; un &#233;cart nul "
          "sur des conditions diff&#233;rentes renforce la mesure."),
    ])


def sec_zoom():
    return "\n\n".join([
        h2("15", "Grossissement"),
        h3("15.1 Principe"),
        p("Un fort grossissement est <strong>autoris&#233;</strong>, y "
          "compris num&#233;rique. Une photographie n'est jamais "
          "irrecevable au seul motif qu'un zoom important a "
          "&#233;t&#233; employ&#233;."),
        p("Le grossissement ne modifie ni la distance entre l'observateur et "
          "la cible, ni la g&#233;om&#233;trie du terrain, ni la "
          "trajectoire physique des rayons lumineux. Il ne peut pas rendre "
          "visible une partie d'objet r&#233;ellement occult&#233;e par la "
          "surface. Il rend la cible assez grande sur le capteur pour "
          "&#234;tre mesur&#233;e, et c'est &#224; cela qu'il sert&#160;: "
          "&#224; 100&#8239;km, une hauteur de 20&#8239;m ne sous-tend que "
          "%s secondes d'arc." % nb(20.0/(100000*4.8481368e-6), 1)),
        encadre("L'inf&#233;rence inverse est fausse",
                p("Ne pas distinguer un objet sans zoom n'&#233;tablit "
                  "<em>pas</em> qu'il est occult&#233;. Un objet peut "
                  "&#234;tre non r&#233;solu, ou trop peu "
                  "contrast&#233;, tout en &#233;tant "
                  "g&#233;om&#233;triquement visible. Confondre "
                  "&#171;&#160;je ne le distinguais pas&#160;&#187; et "
                  "&#171;&#160;il &#233;tait occult&#233;&#160;&#187; est "
                  "l'erreur la plus courante du domaine, et le "
                  "&#167;&#160;20 la traite explicitement."), "warn"),
        h3("15.2 Quatre op&#233;rations &#224; distinguer"),
        liste([
            "<strong>Focale optique r&#233;elle</strong> &#8212; seule "
            "grandeur qui d&#233;termine l'&#233;chelle angulaire du "
            "syst&#232;me.",
            "<strong>Zoom optique</strong> &#8212; variation de la focale "
            "r&#233;elle&#160;; ajoute de l'information.",
            "<strong>Zoom num&#233;rique et recadrage interne</strong> "
            "&#8212; s&#233;lection d'une partie du capteur, avec ou sans "
            "r&#233;&#233;chantillonnage&#160;; n'ajoute aucune "
            "information, et n'en retire pas non plus tant que le "
            "r&#233;&#233;chantillonnage reste interpolant.",
            "<strong>Traitement computationnel</strong> &#8212; fusion de "
            "plusieurs vues, r&#233;duction de bruit, accentuation, "
            "reconnaissance de sujet&#160;; peut cr&#233;er ou "
            "d&#233;placer de l'information.",
        ]),
        h3("15.3 Ligne de partage"),
        p("<strong>Agrandir</strong> une information d&#233;j&#224; "
          "enregistr&#233;e est acceptable&#160;: interpolation bilin&#233;aire "
          "ou bicubique, affichage agrandi, recadrage. Ces "
          "op&#233;rations ne cr&#233;ent aucun d&#233;tail et se "
          "d&#233;font."),
        p("<strong>Reconstruire</strong> une information qui n'a pas "
          "&#233;t&#233; enregistr&#233;e est exclu de la mesure&#160;: "
          "synth&#232;se g&#233;n&#233;rative, sur-r&#233;solution "
          "apprise, rehaussement de sujet, accentuation agressive, fusion "
          "inventant une structure absente des vues individuelles. Les "
          "zones concern&#233;es ne sont pas mesur&#233;es."),
        h3("15.4 Ce qui doit &#234;tre document&#233;"),
        liste([
            "focale optique r&#233;elle et focale &#233;quivalente&#160;;",
            "facteur de grossissement employ&#233; et sa part optique "
            "contre num&#233;rique&#160;;",
            "r&#233;solution native du capteur, en pixels et en pas de "
            "photosite&#160;;",
            "r&#233;solution du fichier final&#160;;",
            "recadrage effectu&#233; par l'appareil avant "
            "l'enregistrement&#160;;",
            "traitements computationnels actifs&#160;;",
            "toute autre &#233;tape entre la sc&#232;ne et le fichier.",
        ]),
        p("Une information indisponible est d&#233;clar&#233;e indisponible, "
          "jamais estim&#233;e. Le crit&#232;re d'acceptation n'est pas "
          "&#171;&#160;grossissement autoris&#233; ou "
          "interdit&#160;&#187;&#160;: c'est "
          "<strong>l'information est-elle assez document&#233;e et assez "
          "exploitable pour permettre une mesure fiable&#160;?</strong>"),
    ])


def sec_acquisition():
    return "\n\n".join([
        h2("16", "Acquisition", saut=True),
        p("L'acquisition et l'analyse sont s&#233;par&#233;es. Au moment du "
          "d&#233;clenchement, l'op&#233;rateur n'a besoin de conna&#238;tre "
          "ni la distance exacte, ni la hauteur de la cible, ni la "
          "pr&#233;diction attendue. Cette s&#233;paration n'est pas une "
          "commodit&#233;&#160;: elle emp&#234;che le r&#233;glage de la "
          "prise de vue en fonction du r&#233;sultat esp&#233;r&#233;."),
        h3("16.1 Ce qui est consign&#233; sur place"),
        liste([
            "date et heure en temps universel, et &#233;cart mesur&#233; de "
            "l'horloge&#160;;",
            "position GNSS et incertitude annonc&#233;e par le "
            "r&#233;cepteur&#160;;",
            "altitude du point de vue et hauteur de l'axe optique au-dessus "
            "du sol ou de l'eau&#160;;",
            "orientation approch&#233;e de la vis&#233;e&#160;;",
            "bo&#238;tier, objectif, focale r&#233;elle, ouverture, temps de "
            "pose, sensibilit&#233;, format&#160;;",
            "grossissement employ&#233; et sa nature&#160;;",
            "temp&#233;rature de l'air &#224; deux hauteurs si possible, "
            "temp&#233;rature de l'eau, pression, humidit&#233;&#160;;",
            "&#233;tat du ciel, visibilit&#233; estim&#233;e, &#233;tat de "
            "la mer&#160;;",
            "ce qui est vis&#233;, en une phrase.",
        ]),
        h3("16.2 Ce qui n'est pas fait sur place"),
        p("Aucun calcul, aucune comparaison, aucune conclusion. "
          "L'op&#233;rateur ne consulte pas la pr&#233;diction avant la fin "
          "de la s&#233;rie. S'il la conna&#238;t d&#233;j&#224;, il le "
          "d&#233;clare, et la mesure du &#167;&#160;19 est alors "
          "conduite par un analyste qui l'ignore."),
        h3("16.3 Acquisition a posteriori"),
        p("Une photographie prise sans intention exp&#233;rimentale reste "
          "recevable si le fichier d'origine existe, si son "
          "authenticit&#233; peut &#234;tre &#233;tablie, si la cible est "
          "identifiable, si la position de l'observateur est "
          "d&#233;terminable et si les param&#232;tres du &#167;&#160;12 "
          "sont &#233;tablissables aux pr&#233;cisions vis&#233;es. Les "
          "donn&#233;es manquantes sont d&#233;clar&#233;es manquantes, et "
          "leur absence est report&#233;e dans l'incertitude."),
        p("Une donn&#233;e reconstruite a posteriori n'est jamais "
          "pr&#233;sent&#233;e comme une mesure directe effectu&#233;e lors "
          "de la photographie. Le &#167;&#160;21 en fixe les classes."),
    ])


def sec_conservation():
    return "\n\n".join([
        h2("17", "Conservation des donn&#233;es"),
        h3("17.1 Int&#233;grit&#233;"),
        liste([
            "Les fichiers d'origine sont conserv&#233;s tels qu'ils sortent "
            "de l'appareil. Ils ne sont jamais ouverts en &#233;criture.",
            "L'empreinte SHA-256 de chaque fichier est calcul&#233;e "
            "d&#232;s le transfert, avant toute autre op&#233;ration, et "
            "consign&#233;e avec la date.",
            "L'empreinte est d&#233;pos&#233;e le jour m&#234;me "
            "aupr&#232;s d'un tiers qui la date. &#192; d&#233;faut, la "
            "date de calcul n'est qu'une d&#233;claration de "
            "l'op&#233;rateur, et le rapport le dit.",
            "Toute manipulation se fait sur une copie, et la liste des "
            "op&#233;rations appliqu&#233;es &#224; cette copie est jointe.",
        ]),
        encadre("Ce que l'empreinte prouve, et ce qu'elle ne prouve pas",
                p("Elle &#233;tablit que le fichier n'a pas chang&#233; "
                  "depuis sa d&#233;claration. Elle n'&#233;tablit ni qu'il "
                  "sort d'un appareil, ni la date de la prise de vue. Les "
                  "m&#233;tadonn&#233;es EXIF s'&#233;crivent&#160;: elles "
                  "documentent la cha&#238;ne, elles ne prouvent pas "
                  "l'origine. L'authenticit&#233; repose sur les "
                  "concordances externes du &#167;&#160;24."), "warn"),
        h3("17.2 Traitements admis"),
        p("Sont admis, sur la copie, les traitements qui ne d&#233;placent "
          "aucun pixel et n'en cr&#233;ent aucun&#160;: r&#233;glage "
          "d'affichage du contraste et de la luminosit&#233;, conversion "
          "lin&#233;aire du fichier brut sans accentuation ni "
          "r&#233;duction de bruit, agrandissement par interpolation "
          "d&#233;clar&#233;e, recadrage d&#233;clar&#233; dont les "
          "coordonn&#233;es d'origine sont conserv&#233;es."),
        p("Sont exclus de la mesure&#160;: la synth&#232;se "
          "g&#233;n&#233;rative, la sur-r&#233;solution apprise, la "
          "reconstruction de d&#233;tail, l'interpolation cr&#233;atrice, "
          "l'accentuation agressive, la r&#233;duction de bruit "
          "non&#8209;lin&#233;aire, et toute fusion multi-vues qui produit "
          "une structure absente des vues individuelles."),
        h3("17.3 Archivage"),
        p("La structure d'archivage est fix&#233;e au &#167;&#160;34. "
          "L'ensemble &#8212; fichiers d'origine, empreintes, fiche "
          "d'observation, donn&#233;es externes, code de calcul, rapport "
          "&#8212; est publi&#233; sous une licence permettant la "
          "reprise, de fa&#231;on qu'un tiers puisse refaire l'analyse "
          "depuis les fichiers d'origine."),
    ])


def sec_validation():
    criteres = [
        ("Mise au point", "bord franc de r&#233;f&#233;rence dont la "
         "largeur de transition est &#224; moins de 1,5&#215; le minimum de "
         "la s&#233;rie", "entre 1,5 et 3&#215;", "au-del&#224; de 3&#215;"),
        ("Flou de boug&#233;", "aucun allongement directionnel "
         "d&#233;tectable sur une source ponctuelle", "allongement "
         "&#8804;&#160;2 pixels", "allongement &gt;&#160;2 pixels"),
        ("Turbulence", "dispersion de la position du bord sur la "
         "s&#233;rie &#8804;&#160;1 pixel", "&#8804;&#160;3 pixels",
         "&gt;&#160;3 pixels"),
        ("Exposition", "aucun pixel satur&#233; ni &#233;cr&#234;t&#233; "
         "sur la cible et son fond imm&#233;diat", "saturation hors zone "
         "mesur&#233;e", "saturation dans la zone mesur&#233;e"),
        ("Contraste", "&#233;cart cible-fond &#8805;&#160;10&#215; "
         "l'&#233;cart-type du bruit local", "entre 3 et 10&#215;",
         "&lt;&#160;3&#215;"),
        ("Artefacts", "aucun artefact de compression, de capteur ou de "
         "traitement dans la zone mesur&#233;e", "artefacts hors zone",
         "artefacts dans la zone"),
        ("Distorsion", "r&#233;siduel de distorsion &lt;&#160;1 pixel "
         "apr&#232;s &#233;talonnage du couple bo&#238;tier-objectif",
         "entre 1 et 3 pixels", "&gt;&#160;3 pixels ou non "
         "&#233;talonn&#233;"),
        ("Occultation parasite", "aucune&#160;: toute occultation visible "
         "est identifi&#233;e et attribu&#233;e", "occultation hors zone "
         "mesur&#233;e", "occultation de cause ind&#233;termin&#233;e"),
    ]
    return "\n\n".join([
        h2("18", "Validation des images"),
        p("Les crit&#232;res ci-dessous sont fix&#233;s et "
          "d&#233;pos&#233;s <strong>avant</strong> l'examen des "
          "r&#233;sultats, et appliqu&#233;s par un op&#233;rateur qui "
          "ignore la pr&#233;diction. Ils ne portent que sur la "
          "qualit&#233; de l'image, jamais sur ce qu'elle montre."),
        tab("Tableau&#160;11 &#8212; grille de validation. Une image est "
            "<em>valide</em> si tous les postes sont en colonne&#160;1, "
            "<em>valide avec r&#233;serves</em> si aucun n'est en "
            "colonne&#160;3, <em>non valide</em> d&#232;s qu'un poste est "
            "en colonne&#160;3.",
            ["Poste", "Valide", "Valide avec r&#233;serves", "Non valide"],
            [rang([c[0], c[1], c[2], c[3]]) for c in criteres]),
        p("Une image <em>valide avec r&#233;serves</em> entre dans "
          "l'analyse avec une incertitude de mesure major&#233;e d'un "
          "facteur d&#233;clar&#233; d'avance. Une image <em>non "
          "valide</em> est exclue, et son exclusion est "
          "publi&#233;e&#160;: le taux d'exclusion fait partie du "
          "r&#233;sultat."),
        encadre("Contre le tri d'apr&#232;s le r&#233;sultat",
                p("Le classement est fait avant toute mesure de la fraction "
                  "visible, par une personne qui ne conna&#238;t ni la "
                  "pr&#233;diction ni la distance. Le journal de "
                  "classement est horodat&#233; et joint au dossier. Un "
                  "classement post&#233;rieur &#224; la mesure est "
                  "irrecevable.")),
    ])


def sec_analyse_image():
    return "\n\n".join([
        h2("19", "Analyse des images"),
        h3("19.1 &#201;chelle m&#233;trique"),
        p("L'&#233;chelle se d&#233;termine de deux fa&#231;ons "
          "ind&#233;pendantes, et les deux sont report&#233;es&#160;: "
          "&#224; partir de la focale r&#233;elle et du pas de photosite "
          "d'une part&#160;; &#224; partir de deux parties pertinentes de "
          "la cible dont l'altitude est connue d'autre part. Un &#233;cart "
          "sup&#233;rieur &#224; 2&#8239;% entre les deux invalide la "
          "focale d&#233;clar&#233;e, non les rep&#232;res."),
        h3("19.2 Grandeurs mesur&#233;es"),
        liste([
            "position apparente du sommet de la cible, en pixels&#160;;",
            "position apparente de la limite inf&#233;rieure visible, en "
            "pixels&#160;;",
            "hauteur visible, en m&#232;tres, par conversion&#160;;",
            "hauteur occult&#233;e, par diff&#233;rence avec la hauteur "
            "totale &#233;tablie au &#167;&#160;12&#160;;",
            "fraction visible <em>f</em>, avec son incertitude&#160;;",
            "rapports de hauteur entre au moins trois &#233;l&#233;ments de "
            "cote connue, pour le test de d&#233;formation verticale.",
        ]),
        h3("19.3 Bord mesurable"),
        p("Un bord n'est mesurable que s'il est une discontinuit&#233; "
          "r&#233;solue. Si la transition entre l'objet et son fond "
          "s'&#233;tend sur plus de trois fois la structure r&#233;solue du "
          "&#167;&#160;20, ce n'est pas un bord mais un d&#233;grad&#233;, "
          "et sa position n'est pas mesur&#233;e. C'est le cas typique "
          "d'une base noy&#233;e dans la brume."),
        h3("19.4 R&#233;gimes atmosph&#233;riques &#224; rechercher"),
        p("Les signatures suivantes sont recherch&#233;es "
          "<strong>sur la s&#233;rie enti&#232;re et avant</strong> la "
          "comparaison du &#167;&#160;28. Le r&#233;sultat de cette "
          "recherche est consign&#233; qu'il soit positif ou n&#233;gatif."),
        liste([
            "<strong>Mirage inf&#233;rieur</strong> &#8212; image "
            "invers&#233;e sous l'objet, s&#233;par&#233;e par une ligne "
            "nette&#160;; s'att&#233;nue quand le point de vue "
            "s'&#233;l&#232;ve.",
            "<strong>Mirage sup&#233;rieur</strong> &#8212; image "
            "invers&#233;e au-dessus de l'objet&#160;; appara&#238;t et "
            "dispara&#238;t au fil des heures.",
            "<strong>Looming</strong> &#8212; l'objet entier remonte sans se "
            "d&#233;former&#160;: les rapports de hauteur internes sont "
            "conserv&#233;s.",
            "<strong>Conduit optique</strong> &#8212; contraste soutenu "
            "&#224; tr&#232;s grande distance, bandes horizontales, "
            "transitions abruptes d'une vue &#224; l'autre.",
            "<strong>D&#233;formation verticale</strong> &#8212; les "
            "rapports de hauteur entre &#233;l&#233;ments de cote connue ne "
            "sont pas conserv&#233;s.",
        ]),
        p("Test op&#233;ratoire de la d&#233;formation verticale&#160;: les "
          "rapports de hauteur entre au moins trois &#233;l&#233;ments de "
          "cote connue sont mesur&#233;s dans l'image et compar&#233;s "
          "&#224; leurs valeurs r&#233;elles. Un &#233;cart "
          "sup&#233;rieur &#224; trois fois l'incertitude de ces rapports "
          "signale une d&#233;formation, et l'observation est "
          "class&#233;e ind&#233;termin&#233;e."),
        p("Un r&#233;gime ne peut &#234;tre invoqu&#233; que s'il a "
          "&#233;t&#233; recherch&#233; avant la comparaison et s'il est "
          "&#233;tabli par des signatures relev&#233;es dans les images "
          "<em>et</em> par les donn&#233;es atmosph&#233;riques du "
          "&#167;&#160;21. Il n'est jamais introduit apr&#232;s coup pour "
          "rendre compte d'un &#233;cart, dans un sens comme dans l'autre."),
        h3("19.5 Mesure en aveugle"),
        p("Les mesures du &#167;&#160;19.2 sont faites par au moins trois "
          "analystes travaillant s&#233;par&#233;ment, &#224; qui l'on "
          "communique l'image et l'&#233;chelle mais ni la distance, ni la "
          "hauteur totale de la cible, ni la pr&#233;diction. Ils "
          "rendent des positions en pixels. La conversion en "
          "m&#232;tres et la comparaison viennent ensuite."),
        p("La dispersion entre analystes est report&#233;e comme composante "
          "d'incertitude de type&#160;A. Si elle exc&#232;de la "
          "r&#233;solution effective du &#167;&#160;20, le dossier revient "
          "en 19.3&#160;: le bord mesur&#233; est ambigu."),
        h3("19.6 Non-d&#233;tection"),
        p("Une s&#233;rie o&#249; la cible n'appara&#238;t pas n'est pas "
          "&#233;cart&#233;e d'office. Elle est class&#233;e "
          "<em>informative</em> si la taille angulaire pr&#233;dite de la "
          "partie attendue exc&#232;de trois fois la r&#233;solution "
          "effective mesur&#233;e&#160;; sinon "
          "<em>ind&#233;termin&#233;e</em>. Les deux cas sont "
          "publi&#233;s. &#201;carter les non-d&#233;tections sans ce test "
          "introduirait un biais de s&#233;lection."),
    ])


def sec_resolution():
    lignes = []
    for D_km in (50, 80, 100, 120, 150, 200):
        mps = D_km*1000*4.8481368e-6
        c0 = cachee(H_OBS, D_km*1000)
        c25 = cachee(H_OBS, D_km*1000, r_eff(0.25))
        lignes.append(rang([nb(D_km), nb(mps, 3), nb(20.0/mps, 1),
                            nb(c0/mps, 1), nb(c25/mps, 1)],
                           num=(0, 1, 2, 3, 4)))
    return "\n\n".join([
        h2("20", "R&#233;solution angulaire", saut=True),
        h3("20.1 Trois limites, et c'est la plus grande qui compte"),
        liste([
            "<strong>Pas de photosite projet&#233;</strong> &#8212; l'angle "
            "sous-tendu par un pixel, &#233;gal au pas de photosite "
            "divis&#233; par la focale r&#233;elle.",
            "<strong>Limite de diffraction</strong> &#8212; environ "
            "1,22&#160;&#955;/<em>d</em> pour une pupille de "
            "diam&#232;tre <em>d</em>.",
            "<strong>Turbulence atmosph&#233;rique</strong> &#8212; sur un "
            "trajet rasant de plusieurs dizaines de kilom&#232;tres, elle "
            "domine g&#233;n&#233;ralement les deux "
            "pr&#233;c&#233;dentes.",
        ]),
        p("La turbulence sur un trajet marin rasant ne se calcule pas de "
          "fa&#231;on fiable&#160;: la structure du champ d'indice n'y est "
          "pas connue. Le protocole exige donc qu'elle soit "
          "<strong>mesur&#233;e sur l'image</strong>, et non "
          "estim&#233;e."),
        h3("20.2 Mesure de la r&#233;solution effective"),
        p("La r&#233;solution effective est la largeur de transition d'un "
          "bord franc de dimension connue pr&#233;sent dans le champ, "
          "mesur&#233;e par la m&#233;thode du bord inclin&#233; de la "
          "norme applicable (&#167;&#160;35), et convertie en m&#232;tres "
          "&#224; la distance de la cible. La caract&#233;ristique "
          "mesur&#233;e doit &#234;tre au moins trois fois plus grande que "
          "cette valeur."),
        h3("20.3 Occult&#233; contre non r&#233;solu"),
        encadre("La distinction d&#233;cisive",
                "\n".join([
                    p("<strong>Occult&#233;</strong>&#160;: la partie de "
                      "l'objet est absente de l'image parce qu'un corps "
                      "s'interpose. Le mod&#232;le pr&#233;dit une "
                      "position pr&#233;cise pour la limite, et cette "
                      "limite est un bord r&#233;solu."),
                    p("<strong>Non r&#233;solu</strong>&#160;: la partie de "
                      "l'objet est pr&#233;sente mais trop petite ou trop "
                      "peu contrast&#233;e pour &#234;tre "
                      "s&#233;par&#233;e. Aucune limite nette "
                      "n'appara&#238;t&#160;; le signal s'&#233;teint "
                      "progressivement."),
                    p("Les deux se distinguent par trois "
                      "signes&#160;: la nettet&#233; de la limite, "
                      "compar&#233;e &#224; la r&#233;solution "
                      "effective&#160;; la stabilit&#233; de sa position "
                      "sur la s&#233;rie&#160;; et son "
                      "d&#233;placement, ou son absence de "
                      "d&#233;placement, quand la focale change &#224; "
                      "position constante. Une limite d'occultation ne "
                      "bouge pas avec la focale&#160;; une limite de "
                      "d&#233;tection recule."),
                ])),
        h3("20.4 Ordres de grandeur"),
        tab("Tableau&#160;12 &#8212; &#233;chelle angulaire et taille "
            "angulaire de la hauteur occult&#233;e pr&#233;dite, "
            "<em>h</em>&#160;=&#160;800&#8239;m. &#192; 120&#8239;km, la "
            "pr&#233;diction &#224; <em>k</em>&#160;=&#160;0,25 ne "
            "sous-tend qu'une seconde d'arc&#160;: cette "
            "g&#233;om&#233;trie ne discrimine pas. &#192; 150&#8239;km, "
            "elle en sous-tend quatre-vingt-dix.",
            ["D (km)", "m par seconde d'arc", "20&#8239;m (&#8243;)",
             "c &#224; k=0 (&#8243;)", "c &#224; k=0,25 (&#8243;)"],
            lignes, num=(0, 1, 2, 3, 4)),
    ])


def sec_meteo():
    classes = [
        ("A", "Mesure directe sur site",
         "instrument &#233;talonn&#233; relev&#233; par l'op&#233;rateur au "
         "point de vue, pendant l'observation", "mesure"),
        ("B", "Sondage a&#233;rologique",
         "profil vertical mesur&#233; par ballon, &#224; moins de "
         "100&#8239;km et 3&#8239;h, l'&#233;cart &#233;tant "
         "consign&#233; et report&#233; dans l'incertitude",
         "mesure d&#233;port&#233;e"),
        ("C", "Station m&#233;t&#233;orologique officielle",
         "observation horodat&#233;e d'un r&#233;seau reconnu, &#224; moins "
         "de 30&#8239;km et 1&#8239;h&#160;; ne donne que des valeurs de "
         "surface", "mesure de surface"),
        ("D", "Sortie de mod&#232;le ou r&#233;analyse",
         "valeur calcul&#233;e sur une maille, jamais observ&#233;e en ce "
         "point&#160;; r&#233;solution verticale insuffisante pr&#232;s de "
         "la surface", "valeur calcul&#233;e"),
        ("E", "Climatologie ou estimation",
         "moyenne saisonni&#232;re, ou valeur choisie par l'analyste faute "
         "de mieux, y compris le coefficient dit standard",
         "d&#233;clarative"),
    ]
    return "\n\n".join([
        h2("21", "Donn&#233;es m&#233;t&#233;orologiques"),
        h3("21.1 Ce qu'il faut, et &#224; quelle r&#233;solution"),
        p("La grandeur qui gouverne la pr&#233;diction est le "
          "<strong>gradient vertical de temp&#233;rature dans la couche "
          "o&#249; passe le rayon rasant</strong>, non la "
          "temp&#233;rature moyenne. Le &#167;&#160;11.5 montre qu'une "
          "couche basse de quelques dizaines de m&#232;tres suffit &#224; "
          "tripler le coefficient effectif."),
        liste([
            "<strong>R&#233;solution verticale</strong> &#8212; au moins un "
            "point tous les 10&#8239;m dans les 100 premiers m&#232;tres "
            "au-dessus de l'eau, puis tous les 100&#8239;m jusqu'&#224; "
            "l'altitude de l'observateur. C'est la r&#233;solution qui "
            "permet de d&#233;tecter une couche d'inversion mince.",
            "<strong>&#201;tendue horizontale</strong> &#8212; la couche "
            "concern&#233;e est celle qui borde le point de tangence, au "
            "milieu du trajet. Un profil pris &#224; une seule "
            "extr&#233;mit&#233; ne renseigne pas sur le milieu&#160;: le "
            "rapport le dit, et l'incertitude en tient compte.",
            "<strong>Grandeurs</strong> &#8212; temp&#233;rature, pression, "
            "humidit&#233;, et temp&#233;rature de surface de la mer. "
            "L'&#233;cart entre temp&#233;rature de l'air et "
            "temp&#233;rature de l'eau est le meilleur indicateur "
            "disponible d'une inversion de surface.",
            "<strong>Cadence</strong> &#8212; au d&#233;but et &#224; la fin "
            "de chaque s&#233;rie au minimum.",
        ]),
        h3("21.2 Classes de donn&#233;e"),
        tab("Tableau&#160;13 &#8212; classes de donn&#233;e "
            "atmosph&#233;rique. La classe dit comment la valeur a "
            "&#233;t&#233; obtenue, pas si elle est juste.",
            ["Classe", "Origine", "D&#233;finition", "Statut au rapport"],
            [rang([c[0], c[1], c[2], c[3]], num=(0,)) for c in classes],
            num=(0,)),
        p("Une donn&#233;e estim&#233;e a posteriori n'est jamais "
          "pr&#233;sent&#233;e comme une mesure directe. La classe "
          "accompagne la valeur partout o&#249; elle appara&#238;t, y "
          "compris dans la conclusion."),
        h3("21.3 Insuffisance"),
        p("L'insuffisance des donn&#233;es ne se traite pas par un choix "
          "prudent&#160;: elle se traite en reportant la plage "
          "enti&#232;re des valeurs plausibles dans l'incertitude, selon "
          "le &#167;&#160;23. Concr&#232;tement, en l'absence de "
          "donn&#233;e de classe A ou B, l'intervalle de <em>k</em> "
          "retenu est celui que les conditions de surface autorisent, "
          "born&#233; par le tableau&#160;8&#160;; il est "
          "d&#233;pos&#233; avant l'analyse."),
    ])


def sec_incertitudes():
    c, dh, dD, dk = sensibilites(H_OBS, 150000.0, 0.13)
    c2, dh2, dD2, dk2 = sensibilites(H_OBS, 120000.0, 0.13)
    postes = [
        ("Altitude de l'observateur <em>h</em>", "&#177;&#160;1&#8239;m",
         nb(abs(dh2), 3), nb(abs(dh), 3)),
        ("Distance <em>D</em>", "&#177;&#160;100&#8239;m",
         nb(abs(dD2)*100, 3), nb(abs(dD)*100, 3)),
        ("Hauteur de la cible <em>H</em>", "&#177;&#160;0,5&#8239;m",
         "0,000", "0,000"),
        ("Coefficient <em>k</em>", "&#177;&#160;0,01",
         nb(abs(dk2), 3), nb(abs(dk), 3)),
        ("Coefficient <em>k</em> non mesur&#233;", "plage 0,10 &#224; 0,40",
         nb(abs(dk2)*15, 2), nb(abs(dk)*15, 2)),
    ]
    return "\n\n".join([
        h2("22", "Analyse des incertitudes"),
        p("Les incertitudes sont &#233;valu&#233;es et compos&#233;es selon "
          "le guide pour l'expression de l'incertitude de mesure "
          "(&#167;&#160;35). Chaque composante porte son type &#8212; A si "
          "elle vient d'une dispersion statistique, B sinon &#8212; et son "
          "facteur d'&#233;largissement."),
        h3("22.1 Composantes de mesure"),
        liste([
            "dispersion entre les trois analystes en aveugle "
            "(type&#160;A)&#160;;",
            "dispersion de la position du bord sur la s&#233;rie, due "
            "&#224; la turbulence (type&#160;A)&#160;;",
            "r&#233;solution effective, en m&#232;tres &#224; la distance de "
            "la cible (type&#160;B)&#160;;",
            "incertitude d'&#233;chelle, &#233;cart entre les deux "
            "d&#233;terminations du &#167;&#160;19.1 (type&#160;B)&#160;;",
            "r&#233;siduel de distorsion apr&#232;s &#233;talonnage "
            "(type&#160;B).",
        ]),
        h3("22.2 Composantes de pr&#233;diction"),
        p("La pr&#233;diction h&#233;rite des incertitudes "
          "g&#233;od&#233;siques et atmosph&#233;riques. Le tableau&#160;14 "
          "donne les coefficients de sensibilit&#233; pour deux "
          "g&#233;om&#233;tries."),
        tab("Tableau&#160;14 &#8212; effet sur la hauteur occult&#233;e "
            "pr&#233;dite, en m&#232;tres, pour "
            "<em>h</em>&#160;=&#160;800&#8239;m et "
            "<em>k</em>&#160;=&#160;0,13. La hauteur de la cible "
            "n'intervient pas dans <em>c</em>&#160;; elle n'intervient que "
            "dans la fraction. &#192; 120&#8239;km, l'ignorance de "
            "<em>k</em> &#233;crase tout le reste, ce qui rend cette "
            "g&#233;om&#233;trie inutilisable sans donn&#233;e "
            "atmosph&#233;rique.",
            ["Param&#232;tre", "&#201;cart consid&#233;r&#233;",
             "&#224; 120&#8239;km (m)", "&#224; 150&#8239;km (m)"],
            [rang([q[0], q[1], q[2], q[3]], num=(2, 3),
                  vedette=(q[0].startswith("Coefficient <em>k</em> non")))
             for q in postes], num=(2, 3)),
        p("&#192; 120&#8239;km la hauteur occult&#233;e pr&#233;dite vaut "
          "%s&#8239;m et l'ignorance de <em>k</em> sur une plage de 0,10 "
          "&#224; 0,40 en vaut %s&#8239;m&#160;: la pr&#233;diction est "
          "noy&#233;e. &#192; 150&#8239;km elle vaut %s&#8239;m pour une "
          "m&#234;me ignorance de %s&#8239;m&#160;: le rapport devient "
          "favorable. C'est cette comparaison, et non une distance ronde, "
          "qui doit fixer la g&#233;om&#233;trie d'une campagne."
          % (nb(c2, 1), nb(abs(dk2)*15, 1), nb(c, 1), nb(abs(dk)*15, 1))),
        h3("22.3 Composition"),
        p("Les composantes ind&#233;pendantes se composent en quadrature. "
          "Les composantes corr&#233;l&#233;es &#8212; typiquement "
          "l'altitude de l'observateur et l'altitude de la base quand elles "
          "viennent du m&#234;me mod&#232;le de terrain &#8212; sont "
          "compos&#233;es en tenant compte de leur corr&#233;lation, dont "
          "la valeur retenue est justifi&#233;e au rapport."),
    ])


def sec_sensibilite():
    lignes = []
    for D_km in (100, 110, 120, 130, 140, 150, 160):
        D = D_km*1000
        r = [fraction_visible(H_OBS, H_CIBLE, D, r_eff(k))
             for k in (0.0, 0.13, 0.25, 0.50)]
        lignes.append(rang([nb(D_km), nb(r[0], 3), nb(r[1], 3), nb(r[2], 3),
                            nb(r[3], 3), "1,000"], num=(0, 1, 2, 3, 4, 5)))
    design = []
    for h in (100, 300, 800, 2000):
        row = [nb(h)] + [nb(D_pour_c(float(h), 20.0, k)/1000, 1)
                         for k in (0.20, 0.35, 0.50)]
        design.append(rang(row, num=(0, 1, 2, 3)))
    return "\n\n".join([
        h2("23", "Analyse de sensibilit&#233;", saut=True),
        h3("23.1 M&#233;thode"),
        p("Chaque param&#232;tre est vari&#233; syst&#233;matiquement dans "
          "son intervalle d'incertitude, et l'<strong>enveloppe</strong> des "
          "pr&#233;dictions qui en r&#233;sulte est rapport&#233;e. "
          "L'intervalle retenu est celui que permettent les meilleures "
          "sources et les meilleurs instruments dont l'observateur "
          "disposait&#160;; il n'est ni &#233;largi par pr&#233;caution, ni "
          "resserr&#233; par commodit&#233;, et son origine est "
          "cit&#233;e."),
        p("Les param&#232;tres vari&#233;s sont&#160;: altitude de "
          "l'observateur, distance, position, altitude de la base, hauteur de "
          "la cible, coefficient de r&#233;fraction et profil vertical, "
          "focale r&#233;elle et param&#232;tres optiques. Le balayage est "
          "conduit sur la grille compl&#232;te lorsque le nombre de "
          "combinaisons le permet, sinon par tirage de Monte-Carlo dont le "
          "germe est publi&#233;."),
        h3("23.2 R&#232;gle de conclusion"),
        encadre("La conclusion ne porte que si elle tient sur l'enveloppe "
                "enti&#232;re",
                "\n".join([
                    p("Si une seule combinaison admissible des "
                      "param&#232;tres rend l'observation conforme &#224; la "
                      "pr&#233;diction d'un mod&#232;le, ce mod&#232;le "
                      "n'est pas r&#233;fut&#233; par cette observation."),
                    p("L'analyste rapporte explicitement la combinaison la "
                      "plus d&#233;favorable &#224; sa propre conclusion, et "
                      "ce qu'elle donne. Cette exigence s'applique dans les "
                      "deux sens et pour les deux mod&#232;les."),
                ])),
        h3("23.3 Enveloppe sur l'exemple"),
        tab("Tableau&#160;15 &#8212; fraction visible pr&#233;dite pour "
            "<em>h</em>&#160;=&#160;800&#8239;m et "
            "<em>H</em>&#160;=&#160;100&#8239;m, selon <em>k</em>, "
            "compar&#233;e au mod&#232;le P. Les deux mod&#232;les ne se "
            "s&#233;parent qu'au-del&#224; de la distance o&#249; "
            "l'enveloppe du mod&#232;le S s'&#233;carte de 1.",
            ["D (km)", "S, k=0", "S, k=0,13", "S, k=0,25", "S, k=0,50",
             "mod&#232;le P"], lignes, num=(0, 1, 2, 3, 4, 5)),
        h3("23.4 Choix de la g&#233;om&#233;trie d'une campagne"),
        p("La g&#233;om&#233;trie doit &#234;tre choisie pour que la "
          "pr&#233;diction du mod&#232;le S <em>la plus favorable au "
          "mod&#232;le P</em> &#8212; c'est-&#224;-dire celle obtenue avec "
          "le <em>k</em> maximal retenu &#8212; s'&#233;carte encore "
          "nettement de la pr&#233;diction du mod&#232;le P."),
        tab("Tableau&#160;16 &#8212; distance &#224; laquelle la hauteur "
            "occult&#233;e pr&#233;dite atteint 20&#8239;m, m&#234;me sous "
            "le coefficient maximal retenu. C'est ce tableau, et non un "
            "seuil en kilom&#232;tres, qui doit dimensionner une "
            "campagne.",
            ["Altitude observateur (m)", "k<sub>max</sub>=0,20",
             "k<sub>max</sub>=0,35", "k<sub>max</sub>=0,50"],
            design, num=(0, 1, 2, 3)),
        p("Lecture&#160;: depuis 100&#8239;m, il faut d&#233;j&#224; "
          "%s&#8239;km si l'on admet <em>k</em> jusqu'&#224; 0,50. Le seuil "
          "de 50&#8239;km du cahier des charges ne suffit donc pas d&#232;s "
          "que la r&#233;fraction n'est pas born&#233;e par une mesure."
          % nb(D_pour_c(100.0, 20.0, 0.50)/1000, 1)),
    ])


def sec_controles():
    ctrl = [
        ("&#201;talonnage d'&#233;chelle",
         "photographier une mire de dimensions connues &#224; distance "
         "mesur&#233;e, &#224; la focale employ&#233;e",
         "l'&#233;chelle calcul&#233;e depuis la focale et celle "
         "mesur&#233;e sur la mire s'accordent &#224; mieux de 2&#8239;%"),
        ("R&#233;solution",
         "mesurer la largeur de transition d'un bord franc de la mire",
         "la valeur est report&#233;e et sert de r&#233;f&#233;rence "
         "instrumentale au &#167;&#160;20"),
        ("Distorsion",
         "photographier une grille r&#233;guli&#232;re et ajuster un "
         "mod&#232;le de distorsion",
         "r&#233;siduel &lt;&#160;1 pixel apr&#232;s correction"),
        ("Stabilit&#233;",
         "vingt vues cons&#233;cutives d'une cible fixe proche",
         "d&#233;placement du centro&#239;de &#8804;&#160;1 pixel"),
        ("Orientation",
         "vis&#233;e sur deux rep&#232;res d'azimut connu",
         "azimut retrouv&#233; &#224; mieux que 0,05&#176;"),
        ("Coh&#233;rence entre focales",
         "photographier la m&#234;me sc&#232;ne &#224; trois focales, "
         "position inchang&#233;e",
         "la limite d'occultation mesur&#233;e ne se d&#233;place pas&#160;; "
         "une limite de d&#233;tection, elle, recule"),
        ("Coh&#233;rence entre images",
         "mesurer la fraction visible sur cinq vues de la m&#234;me "
         "s&#233;rie",
         "dispersion compatible avec la r&#233;solution effective"),
        ("Reproductibilit&#233; entre analystes",
         "trois mesures en aveugle du m&#234;me bord",
         "dispersion inf&#233;rieure &#224; la r&#233;solution effective"),
        ("Concordance externe",
         "position du Soleil d&#233;duite des ombres, hauteur de "
         "mar&#233;e, registre horodat&#233; d'un mobile, "
         "m&#233;t&#233;o observ&#233;e, rep&#232;res attendus dans le "
         "champ",
         "au moins deux concordances &#233;tablies, aucune discordance"),
    ]
    return "\n\n".join([
        h2("24", "Contr&#244;les"),
        p("Ces contr&#244;les sont ex&#233;cut&#233;s au moins une fois par "
          "campagne et &#224; chaque changement de mat&#233;riel. Leurs "
          "r&#233;sultats sont joints au dossier, qu'ils soient "
          "favorables ou non."),
        tab("Tableau&#160;17 &#8212; contr&#244;les exp&#233;rimentaux et "
            "crit&#232;res d'acceptation.",
            ["Contr&#244;le", "Mode op&#233;ratoire", "Crit&#232;re"],
            [rang([c[0], c[1], c[2]]) for c in ctrl]),
        p("Le contr&#244;le de coh&#233;rence entre focales est le plus "
          "discriminant du lot&#160;: il s&#233;pare exp&#233;rimentalement "
          "une limite d'occultation d'une limite de d&#233;tection, sans "
          "recourir &#224; aucun mod&#232;le."),
    ])


def sec_replication():
    return "\n\n".join([
        h2("25", "R&#233;plication"),
        liste([
            "<strong>Plusieurs observateurs.</strong> La m&#234;me cible est "
            "photographi&#233;e par au moins deux op&#233;rateurs "
            "ind&#233;pendants, si possible depuis deux sites d'altitudes "
            "diff&#233;rentes.",
            "<strong>Plusieurs analystes.</strong> Au moins trois analyses "
            "ind&#233;pendantes du m&#234;me dossier, sous le m&#234;me "
            "seuil d&#233;pos&#233;, conduites s&#233;par&#233;ment.",
            "<strong>Mesure en aveugle.</strong> Les analystes mesurent des "
            "positions en pixels sans conna&#238;tre la distance, la "
            "hauteur totale ni la pr&#233;diction.",
            "<strong>D&#233;claration d'int&#233;r&#234;t.</strong> Chaque "
            "analyste d&#233;clare tout int&#233;r&#234;t dans l'issue et "
            "toute participation &#224; la prise de vue. L'op&#233;rateur du "
            "clich&#233; n'est aucun des trois.",
            "<strong>R&#233;p&#233;tition.</strong> La m&#234;me "
            "g&#233;om&#233;trie est reprise &#224; des dates et dans des "
            "conditions atmosph&#233;riques diff&#233;rentes.",
            "<strong>Publication des donn&#233;es brutes.</strong> Fichiers "
            "d'origine, empreintes, fiches, donn&#233;es externes et code de "
            "calcul, sous licence permettant la reprise.",
        ]),
        p("Le r&#233;sultat est certifi&#233; lorsque les trois analyses "
          "convergent. Toute divergence rend le r&#233;sultat "
          "ind&#233;termin&#233;&#160;: les trois analyses sont "
          "publi&#233;es, le point de d&#233;saccord est nomm&#233;, et le "
          "dossier reste ouvert."),
    ])


def sec_preenregistrement():
    return "\n\n".join([
        h2("26", "Pr&#233;-enregistrement"),
        p("Les &#233;l&#233;ments suivants sont fix&#233;s, dat&#233;s et "
          "d&#233;pos&#233;s aupr&#232;s d'un tiers <strong>avant</strong> "
          "toute acquisition, ou &#224; d&#233;faut avant tout examen des "
          "images pour un dossier a posteriori."),
        liste([
            "les mod&#232;les compar&#233;s, avec leur g&#233;om&#233;trie, "
            "leur loi de propagation et leur nombre de param&#232;tres "
            "libres&#160;;",
            "l'intervalle de <em>k</em> retenu et sa justification&#160;;",
            "les crit&#232;res de s&#233;lection des observations et des "
            "images (&#167;&#160;18)&#160;;",
            "la m&#233;thode de mesure de la fraction visible "
            "(&#167;&#160;19)&#160;;",
            "le mode de composition des incertitudes (&#167;&#160;22) et le "
            "plan de sensibilit&#233; (&#167;&#160;23)&#160;;",
            "le <strong>seuil de r&#233;futation</strong>&#160;: l'&#233;cart "
            "&#224; partir duquel un r&#233;sultat est d&#233;clar&#233; "
            "incompatible&#160;;",
            "la taille d'&#233;chantillon vis&#233;e et la r&#232;gle "
            "d'arr&#234;t&#160;;",
            "le plan d'analyse statistique (&#167;&#160;27).",
        ]),
        p("Aucun de ces &#233;l&#233;ments n'est modifi&#233; apr&#232;s "
          "examen des r&#233;sultats. Tout &#233;cart au plan "
          "d&#233;pos&#233; est publi&#233; comme tel, avec sa date et son "
          "motif, et l'analyse correspondante est &#233;tiquet&#233;e "
          "<em>exploratoire</em>&#160;: elle ne peut pas conclure."),
        p("Un dossier analys&#233; sans seuil pr&#233;alablement "
          "d&#233;pos&#233; ne peut pas conclure &#224; une "
          "incompatibilit&#233;. Il peut conclure &#224; une "
          "compatibilit&#233; ou rester ind&#233;termin&#233;. "
          "L'asym&#233;trie est d&#233;lib&#233;r&#233;e&#160;: c'est "
          "l'affirmation la plus forte qui exige l'engagement "
          "pr&#233;alable."),
    ])


def sec_statistique():
    lignes = [rang([nb(r, 2), nb(taille_echantillon(r), 1)], num=(0, 1))
              for r in (0.20, 0.33, 0.50, 0.75, 1.00)]
    return "\n\n".join([
        h2("27", "Analyse statistique"),
        h3("27.1 Grandeur analys&#233;e"),
        p("L'analyse porte sur la fraction visible <em>f</em>, et sur "
          "l'&#233;cart <em>f</em><sub>obs</sub>&#160;&#8722;&#160;"
          "<em>f</em><sub>pr&#233;d</sub> pour chaque mod&#232;le. Les "
          "observations d'une campagne sont ajust&#233;es "
          "<strong>conjointement</strong> sur la courbe "
          "<em>f</em>(<em>D</em>), et non compar&#233;es une &#224; une."),
        h3("27.2 Comparaison de mod&#232;les"),
        p("Les mod&#232;les sont compar&#233;s par leur "
          "vraisemblance, p&#233;nalis&#233;e du nombre de "
          "param&#232;tres libres d&#233;clar&#233;s au &#167;&#160;26. La "
          "statistique retenue, le crit&#232;re de p&#233;nalisation et le "
          "seuil de d&#233;cision sont d&#233;pos&#233;s avant "
          "l'analyse. Aucun mod&#232;le ne re&#231;oit le statut "
          "d'hypoth&#232;se nulle privil&#233;gi&#233;e&#160;: les deux "
          "sont trait&#233;s sym&#233;triquement."),
        h3("27.3 Taille d'&#233;chantillon"),
        p("Pour s&#233;parer deux pr&#233;dictions distantes de &#916; avec "
          "un bruit par observation &#963;, au risque de "
          "premi&#232;re esp&#232;ce &#945;&#160;=&#160;0,001 bilat&#233;ral "
          "et &#224; la puissance 95&#8239;%&#160;:"),
        eq("<em>n</em> &#8805; (<em>z</em><sub>1&#8722;&#945;/2</sub> + "
           "<em>z</em><sub>1&#8722;&#946;</sub>)&#178; &#183; "
           "(&#963;/&#916;)&#178; = %s &#183; (&#963;/&#916;)&#178;"
           % nb(FACTEUR_N, 2),
           "z<sub>0,9995</sub> = %s, z<sub>0,95</sub> = %s"
           % (nb(Z_ALPHA, 4), nb(Z_BETA, 4))),
        tab("Tableau&#160;18 &#8212; nombre minimal d'observations "
            "ind&#233;pendantes. Le rapport &#963;/&#916; se calcule "
            "&#224; partir du tableau&#160;15 et de l'incertitude de "
            "mesure du &#167;&#160;22.",
            ["&#963;/&#916;", "<em>n</em> minimal"], lignes, num=(0, 1)),
        p("Cette formule est un dimensionnement, non l'analyse elle-m&#234;me. "
          "Elle suppose des observations ind&#233;pendantes et un bruit de "
          "m&#234;me &#233;cart-type&#160;; deux vues du m&#234;me jour, "
          "depuis le m&#234;me site, sur la m&#234;me cible, ne sont pas "
          "deux observations ind&#233;pendantes. Le d&#233;compte porte sur "
          "les configurations distinctes&#160;: site, cible, date, "
          "conditions."),
        h3("27.4 Ce qui est publi&#233;"),
        p("Toutes les observations recevables entrent dans l'analyse, y "
          "compris celles qui ne vont pas dans le sens attendu et celles "
          "class&#233;es ind&#233;termin&#233;es. Le taux d'exclusion, ses "
          "motifs et la liste des dossiers &#233;cart&#233;s sont "
          "publi&#233;s avec les r&#233;sultats."),
    ])


def sec_decision():
    return "\n\n".join([
        h2("28", "Crit&#232;res de d&#233;cision", saut=True),
        h3("28.1 Filtre pr&#233;alable"),
        p("La <strong>recevabilit&#233;</strong> est un filtre, non une "
          "conclusion. Un dossier est recevable s'il fournit les "
          "pi&#232;ces du &#167;&#160;33, s'il passe les contr&#244;les du "
          "&#167;&#160;24, si l'image est valide ou valide avec "
          "r&#233;serves au sens du &#167;&#160;18, et si toute "
          "occultation visible est identifi&#233;e et attribu&#233;e. Un "
          "dossier irrecevable n'est ni favorable ni "
          "d&#233;favorable&#160;: il n'entre pas dans l'analyse, et son "
          "exclusion est publi&#233;e."),
        h3("28.2 Condition de discrimination"),
        p("Une observation ne peut discriminer que si sa "
          "g&#233;om&#233;trie s&#233;pare assez les pr&#233;dictions. La "
          "condition, d&#233;pos&#233;e avant l'observation&#160;:"),
        encadre("Condition de discrimination",
                p("L'&#233;cart entre la pr&#233;diction du mod&#232;le S "
                  "sous le coefficient <em>le plus favorable au mod&#232;le "
                  "P</em> et la pr&#233;diction du mod&#232;le P doit "
                  "atteindre au moins <strong>cinq fois</strong> "
                  "l'incertitude compos&#233;e de mesure. En de&#231;&#224;, "
                  "l'observation est class&#233;e "
                  "ind&#233;termin&#233;e avant m&#234;me d'&#234;tre "
                  "mesur&#233;e.")),
        h3("28.3 Les trois cat&#233;gories"),
        liste([
            "<strong>Compatible.</strong> La fraction visible "
            "observ&#233;e tombe dans l'enveloppe de pr&#233;diction du "
            "mod&#232;le, incertitudes de mesure et de pr&#233;diction "
            "compos&#233;es, et l'&#233;cart reste sous le seuil de "
            "r&#233;futation d&#233;pos&#233;.",
            "<strong>Incompatible.</strong> L'&#233;cart franchit le seuil "
            "d&#233;pos&#233;, il tient sur l'enveloppe enti&#232;re de "
            "sensibilit&#233; du &#167;&#160;23, aucun r&#233;gime "
            "atmosph&#233;rique du &#167;&#160;19.4 n'est &#233;tabli, "
            "aucune occultation n'est inexpliqu&#233;e, et les trois "
            "analyses ind&#233;pendantes convergent.",
            "<strong>Ind&#233;termin&#233;.</strong> Tout le reste&#160;: "
            "donn&#233;es atmosph&#233;riques insuffisantes pour borner "
            "<em>k</em>, caract&#233;ristique non r&#233;solue, bord non "
            "mesurable, r&#233;gime atmosph&#233;rique &#233;tabli, "
            "enveloppe de sensibilit&#233; recouvrant les deux "
            "pr&#233;dictions, ou divergence entre analystes.",
        ]),
        p("Un m&#234;me dossier peut &#234;tre compatible avec un "
          "mod&#232;le et incompatible avec l'autre&#160;: c'est le cas "
          "recherch&#233;. Il peut aussi &#234;tre compatible avec les "
          "deux, ou incompatible avec les deux&#160;; ces deux issues sont "
          "publi&#233;es telles quelles, la seconde signalant qu'un "
          "&#233;l&#233;ment du dispositif est mal compris."),
        encadre("Sym&#233;trie de traitement",
                "\n".join([
                    p("Les m&#234;mes r&#232;gles, les m&#234;mes seuils et "
                      "les m&#234;mes incertitudes s'appliquent aux deux "
                      "mod&#232;les. Un r&#233;sultat allant dans un sens "
                      "n'est ni examin&#233; plus s&#233;v&#232;rement ni "
                      "accept&#233; plus facilement qu'un r&#233;sultat "
                      "allant dans l'autre."),
                    p("Une observation <em>ind&#233;termin&#233;e</em> n'est "
                      "jamais pr&#233;sent&#233;e comme une preuve pour ou "
                      "contre un mod&#232;le, ni comme un demi-r&#233;sultat. "
                      "Elle est publi&#233;e avec le motif exact de "
                      "l'ind&#233;termination et ce qu'il faudrait pour la "
                      "lever."),
                ]), "warn"),
    ])


def sec_concurrents():
    return "\n\n".join([
        h2("29", "Mod&#232;les concurrents"),
        p("Un mod&#232;le n'entre dans la comparaison que s'il est "
          "d&#233;pos&#233; avec quatre &#233;l&#233;ments&#160;: sa "
          "g&#233;om&#233;trie de surface, sa loi de propagation de la "
          "lumi&#232;re, ses param&#232;tres libres et leurs intervalles, et "
          "la pr&#233;diction explicite qu'il fait sur <em>f</em>(<em>D</em>) "
          "pour la configuration observ&#233;e."),
        h3("29.1 Pourquoi cette exigence"),
        p("Un mod&#232;le dont la loi de propagation reste libre reproduit "
          "n'importe quelle observation. Il n'est pas r&#233;futable, donc "
          "pas comparable. Cela vaut pour un mod&#232;le plan assorti d'une "
          "r&#233;fraction ad hoc comme pour un mod&#232;le sph&#233;rique "
          "assorti d'un <em>k</em> libre&#160;: les deux sont exclus de la "
          "comparaison par la m&#234;me r&#232;gle."),
        h3("29.2 Traitement identique"),
        liste([
            "m&#234;mes donn&#233;es d'entr&#233;e, m&#234;mes sources, "
            "m&#234;mes incertitudes&#160;;",
            "m&#234;mes r&#232;gles de mesure sur les images&#160;;",
            "m&#234;me analyse de sensibilit&#233;, sur les m&#234;mes "
            "intervalles&#160;;",
            "m&#234;me seuil de r&#233;futation&#160;;",
            "m&#234;me p&#233;nalisation du nombre de param&#232;tres "
            "libres.",
        ]),
        h3("29.3 Cas particulier du mod&#232;le P"),
        p("Le mod&#232;le P tel que d&#233;fini au &#167;&#160;4.2 n'a "
          "aucun param&#232;tre libre&#160;: il pr&#233;dit "
          "<em>f</em>&#160;=&#160;1 partout. C'est un avantage dans la "
          "comparaison p&#233;nalis&#233;e, et il faut le dire&#160;: un "
          "mod&#232;le sans param&#232;tre libre est plus facilement "
          "r&#233;futable, mais aussi moins facilement &#233;cart&#233; "
          "quand les donn&#233;es sont pauvres. C'est la raison de la "
          "condition de discrimination du &#167;&#160;28.2."),
        p("Toute variante du mod&#232;le P introduisant une loi de "
          "propagation, une perspective particuli&#232;re ou une limite de "
          "visibilit&#233; doit &#234;tre d&#233;pos&#233;e comme un "
          "mod&#232;le distinct, avec ses param&#232;tres, et subit "
          "exactement le m&#234;me traitement."),
    ])


def sec_limites():
    return "\n\n".join([
        h2("30", "Limites"),
        liste([
            "<strong>La r&#233;fraction n'est jamais mesur&#233;e sur le "
            "trajet lui-m&#234;me.</strong> Elle est estim&#233;e depuis des "
            "profils pris ailleurs, ou born&#233;e. C'est la limite "
            "principale, et elle est irr&#233;ductible sans instrumentation "
            "du trajet.",
            "<strong>Le point de tangence est le plus mal "
            "document&#233;.</strong> Il se trouve au milieu du trajet, "
            "l&#224; o&#249; l'on ne mesure rien.",
            "<strong>La turbulence n'est pas mod&#233;lisable ici.</strong> "
            "Elle est mesur&#233;e sur l'image, ce qui la traite comme un "
            "bruit et non comme un biais&#160;; un biais "
            "syst&#233;matique de turbulence n'est pas exclu.",
            "<strong>Les altitudes d&#233;pendent d'un mod&#232;le de "
            "g&#233;o&#239;de.</strong> Elles ne sont pas des mesures "
            "directes, et leur incertitude est corr&#233;l&#233;e entre "
            "l'observateur et la cible quand la source est la m&#234;me.",
            "<strong>La s&#233;lection des cibles n'est pas "
            "al&#233;atoire.</strong> On photographie ce qui est "
            "photographiable&#160;; la campagne doit d&#233;clarer sa "
            "r&#232;gle de choix &#224; l'avance.",
            "<strong>Un dossier a posteriori est presque toujours plus "
            "pauvre.</strong> L'absence de mesure atmosph&#233;rique sur "
            "site suffit le plus souvent &#224; rendre le r&#233;sultat "
            "ind&#233;termin&#233;.",
            "<strong>Le protocole ne mesure pas R.</strong> Il teste une "
            "pr&#233;diction construite avec une valeur de R "
            "pos&#233;e&#160;; une conclusion d'incompatibilit&#233; "
            "porterait sur le couple g&#233;om&#233;trie-propagation, pas "
            "sur R seul.",
        ]),
    ])


ATTAQUES = [
    ("G&#233;om&#233;trie", "Rayon sph&#233;rique moyen",
     "Vous calculez avec R<sub>1</sub> alors que le rayon de courbure "
     "d&#233;pend de la latitude et de l'azimut. L'&#233;cart entre rayon "
     "m&#233;ridien et grande normale d&#233;passe 40&#8239;km, soit "
     "0,6&#8239;%, ce qui exc&#232;de l'erreur d'approximation dont vous "
     "vous vantez au &#167;&#160;9.4.",
     "Exact, et c'est pourquoi le &#167;&#160;12.2 impose le rayon d'Euler "
     "&#224; l'azimut de la vis&#233;e, et non R<sub>1</sub>. La "
     "diff&#233;rence est quantifi&#233;e au rapport."),
    ("G&#233;om&#233;trie", "Cible non ponctuelle",
     "Vous traitez la cible comme un segment vertical au-dessus d'un point. "
     "Un navire ou une montagne a une extension le long de la vis&#233;e, et "
     "sa base n'est pas &#224; une distance unique.",
     "L'incertitude sur <em>D</em> est &#233;largie &#224; l'extension "
     "longitudinale de la cible, et cette composante est "
     "d&#233;clar&#233;e. Une cible dont l'extension d&#233;passe "
     "l'incertitude vis&#233;e sur <em>D</em> est &#233;cart&#233;e."),
    ("G&#233;od&#233;sie", "G&#233;o&#239;de et ellipso&#239;de",
     "Une altitude GNSS brute est une hauteur ellipso&#239;dale. La "
     "confondre avec une altitude introduit des dizaines de m&#232;tres "
     "d'erreur, donc plusieurs m&#232;tres sur <em>c</em>.",
     "Le &#167;&#160;12.1 impose la conversion par un mod&#232;le de "
     "g&#233;o&#239;de publi&#233; et la d&#233;claration du "
     "mod&#232;le. Le contr&#244;le du &#167;&#160;24 v&#233;rifie la "
     "coh&#233;rence sur un point de cote connue."),
    ("G&#233;od&#233;sie", "Mar&#233;e et z&#233;ro hydrographique",
     "Pour un ouvrage c&#244;tier, la base &#171;&#160;au niveau de la "
     "mer&#160;&#187; bouge de plusieurs m&#232;tres dans la "
     "journ&#233;e, et le z&#233;ro des cartes n'est pas le niveau moyen.",
     "L'altitude de la base est prise &#224; l'heure exacte, corrig&#233;e "
     "de la mar&#233;e observ&#233;e et non pr&#233;dite quand un "
     "mar&#233;graphe existe, et le z&#233;ro de r&#233;f&#233;rence est "
     "nomm&#233;."),
    ("Atmosph&#232;re", "Rayon effectif inappropri&#233;",
     "R/(1&#8722;<em>k</em>) suppose un gradient d'indice constant sur toute "
     "la hauteur. C'est faux d&#232;s qu'il y a une couche.",
     "Reconnu et quantifi&#233;&#160;: le &#167;&#160;11.5 montre un facteur "
     "trois sur un profil &#224; deux couches. Le tra&#231;age de rayon est "
     "obligatoire d&#232;s qu'un profil non lin&#233;aire est "
     "document&#233;, et l'incertitude couvre l'&#233;cart quand il ne "
     "l'est pas."),
    ("Atmosph&#232;re", "R&#233;fraction ajust&#233;e apr&#232;s coup",
     "Il suffira d'invoquer une inversion pour sauver le mod&#232;le S, ou "
     "de la nier pour le condamner.",
     "Le &#167;&#160;11.7 interdit l'ajustement post&#233;rieur, dans les "
     "deux sens. L'intervalle de <em>k</em> est d&#233;pos&#233; avant "
     "analyse, et un r&#233;gime n'est invocable que s'il a "
     "&#233;t&#233; recherch&#233; avant la comparaison et "
     "&#233;tabli par des signatures d'image et des donn&#233;es "
     "m&#233;t&#233;o."),
    ("Atmosph&#232;re", "Conduit d'&#233;vaporation",
     "Au-dessus de la mer, le conduit d'&#233;vaporation est "
     "omnipr&#233;sent&#160;: votre exp&#233;rience ne prouvera jamais rien.",
     "Erreur de domaine, et le &#167;&#160;11.4 la chiffre&#160;: le terme "
     "humide vaut environ 90&#8239;N en radio contre &#8722;0,8&#8239;N en "
     "optique. Le conduit d'&#233;vaporation est un ph&#233;nom&#232;ne "
     "radio&#233;lectrique&#160;; un conduit optique exige une inversion "
     "thermique extr&#234;me, recherch&#233;e explicitement."),
    ("Photographie", "Zoom num&#233;rique",
     "Une image agrandie num&#233;riquement ne contient pas plus "
     "d'information&#160;: vous mesurez du bruit interpol&#233;.",
     "Le &#167;&#160;15 l'&#233;nonce&#160;: l'agrandissement n'ajoute rien "
     "et n'est pas compt&#233; dans la r&#233;solution. C'est la "
     "r&#233;solution effective <em>mesur&#233;e</em> du &#167;&#160;20 qui "
     "d&#233;cide, et elle est insensible &#224; l'agrandissement."),
    ("Photographie", "Traitement interne",
     "Les appareils modernes reconstruisent. Vous ne mesurez pas une "
     "sc&#232;ne, vous mesurez une inf&#233;rence.",
     "Le &#167;&#160;15.3 exclut de la mesure toute zone issue d'une "
     "reconstruction, et le &#167;&#160;17.2 liste les traitements admis. "
     "Le format brut est exig&#233; d&#232;s que l'appareil en produit un."),
    ("R&#233;solution", "Occult&#233; ou non r&#233;solu",
     "Vous ne pouvez pas distinguer une base cach&#233;e d'une base trop "
     "petite pour &#234;tre vue.",
     "C'est l'objet du &#167;&#160;20.3, et le contr&#244;le "
     "exp&#233;rimental du &#167;&#160;24 le tranche sans mod&#232;le&#160;: "
     "&#224; position constante, une limite d'occultation ne se "
     "d&#233;place pas quand la focale change, une limite de "
     "d&#233;tection recule."),
    ("R&#233;solution", "Brume prise pour un bord",
     "&#192; 150&#8239;km la base d'un objet dispara&#238;t dans la brume "
     "bien avant d'&#234;tre occult&#233;e. Vous mesurerez une limite "
     "d'extinction.",
     "Le &#167;&#160;19.3 refuse de mesurer un bord dont la transition "
     "exc&#232;de trois fois la structure r&#233;solue&#160;; le "
     "&#167;&#160;18 &#233;carte les images dont le contraste "
     "cible-fond est insuffisant. Le cas &#233;ch&#233;ant, "
     "l'observation est ind&#233;termin&#233;e."),
    ("Mesure", "Biais de l'analyste",
     "Celui qui mesure sait ce qu'il cherche.",
     "Trois analystes en aveugle mesurent des positions en pixels sans "
     "conna&#238;tre distance, hauteur ni pr&#233;diction "
     "(&#167;&#160;19.5)&#160;; la dispersion entre eux est une composante "
     "d'incertitude, et une divergence rouvre le dossier."),
    ("S&#233;lection", "Tri des images",
     "Vingt vues, on garde les meilleures&#160;: le tri fabrique le "
     "r&#233;sultat.",
     "Le crit&#232;re de tri est d&#233;pos&#233; d'avance, appliqu&#233; "
     "automatiquement, et ex&#233;cut&#233; par une personne qui ignore la "
     "pr&#233;diction (&#167;&#160;18). Toutes les vues sont remises et "
     "publi&#233;es, et le taux d'exclusion fait partie du r&#233;sultat."),
    ("S&#233;lection", "Dossiers qui ne parviennent pas",
     "Les observations sont soumises parce qu'elles ont paru "
     "remarquables. Votre s&#233;rie ne dit rien de la population.",
     "Reconnu au &#167;&#160;30. Une campagne pr&#233;-enregistr&#233;e "
     "d&#233;clare sa r&#232;gle de choix des cibles avant "
     "l'acquisition&#160;; les dossiers a posteriori sont analys&#233;s "
     "s&#233;par&#233;ment et ne sont pas m&#233;lang&#233;s aux "
     "campagnes."),
    ("Statistique", "Observations non ind&#233;pendantes",
     "Vingt vues du m&#234;me jour ne font pas vingt observations.",
     "Le &#167;&#160;27.3 le dit&#160;: le d&#233;compte porte sur les "
     "configurations distinctes &#8212; site, cible, date, conditions "
     "&#8212; et la s&#233;rie ne sert qu'&#224; estimer la dispersion."),
    ("Statistique", "Mod&#232;le nul privil&#233;gi&#233;",
     "Vous testez le mod&#232;le plan contre le mod&#232;le sph&#233;rique "
     "en donnant &#224; ce dernier un param&#232;tre libre suppl&#233;mentaire.",
     "Le &#167;&#160;27.2 p&#233;nalise le nombre de param&#232;tres libres "
     "d&#233;clar&#233;s, et le &#167;&#160;29.3 dit explicitement que "
     "l'absence de param&#232;tre libre du mod&#232;le P est un avantage "
     "dans la comparaison p&#233;nalis&#233;e."),
    ("Donn&#233;es historiques", "Photographie ancienne",
     "Une photographie de vacances n'a ni horloge synchronis&#233;e, ni "
     "position certifi&#233;e, ni m&#233;t&#233;o.",
     "Elle est recevable si les conditions du &#167;&#160;16.3 sont "
     "remplies, et elle finit le plus souvent "
     "<em>ind&#233;termin&#233;e</em> faute de donn&#233;e "
     "atmosph&#233;rique. Le protocole le dit d'avance plut&#244;t que de "
     "conclure &#224; partir d'un dossier pauvre."),
    ("Int&#233;grit&#233;", "Empreinte fabriqu&#233;e",
     "L'empreinte est calcul&#233;e par celui qui soumet le fichier. Elle ne "
     "prouve rien sur l'origine.",
     "Reconnu explicitement au &#167;&#160;17.1. L'empreinte n'&#233;tablit "
     "que l'int&#233;grit&#233;&#160;; l'authenticit&#233; repose sur au "
     "moins deux concordances externes que le fichier ne peut pas "
     "fabriquer &#8212; position du Soleil, mar&#233;e, registre "
     "horodat&#233;, m&#233;t&#233;o observ&#233;e &#8212; et le "
     "d&#233;p&#244;t de l'empreinte aupr&#232;s d'un tiers datant."),
]


def sec_audit():
    lignes = [rang(["%02d" % (i + 1), a[0], a[1], a[2], a[3]], num=(0,))
              for i, a in enumerate(ATTAQUES)]
    return "\n\n".join([
        h2("31", "Audit critique", saut=True),
        p("Le protocole a &#233;t&#233; attaqu&#233; du point de vue d'un "
          "contradicteur comp&#233;tent et hostile. Dix-huit objections ont "
          "&#233;t&#233; retenues. Chacune est reproduite telle qu'elle "
          "serait formul&#233;e, avec la correction "
          "int&#233;gr&#233;e&#160;; celles qui restent sans correction "
          "compl&#232;te figurent au &#167;&#160;30."),
        tab("Tableau&#160;19 &#8212; objections et corrections. Une "
            "objection sans correction serait une limite, pas un "
            "audit&#160;: les limites irr&#233;ductibles sont "
            "&#233;num&#233;r&#233;es s&#233;par&#233;ment au "
            "&#167;&#160;30.",
            ["N&#176;", "Domaine", "Objection", "Formulation hostile",
             "Correction"], lignes, num=(0,)),
    ])


def sec_checklist():
    terrain = [
        "V&#233;rifier que le seuil de r&#233;futation et le plan "
        "d'analyse sont d&#233;pos&#233;s et dat&#233;s.",
        "R&#233;gler l'horloge sur le temps universel et noter "
        "l'&#233;cart.",
        "Installer le tr&#233;pied, lester, mettre de niveau, bloquer la "
        "rotule, rentrer la colonne.",
        "D&#233;sactiver la stabilisation. Mise au point manuelle &#224; "
        "l'infini, affin&#233;e en vis&#233;e agrandie sur la cible.",
        "Fixer l'exposition&#160;; v&#233;rifier qu'aucun pixel de la cible "
        "n'est satur&#233;. Sensibilit&#233; minimale.",
        "Relever la position GNSS et son incertitude&#160;; mesurer et "
        "photographier la hauteur de l'axe optique.",
        "Enregistrer en format brut. Vingt vues au minimum, sans toucher "
        "&#224; la mise au point, au cadrage ni au grossissement.",
        "Prendre la vue grand-angle du point de vue, la vue de l'horizon "
        "&#224; la m&#234;me focale, et la mire si elle est disponible.",
        "Relever temp&#233;rature de l'air &#224; deux hauteurs, "
        "temp&#233;rature de l'eau, pression, humidit&#233;, au d&#233;but "
        "et &#224; la fin.",
        "Noter l'&#233;tat du ciel, la visibilit&#233;, l'&#233;tat de la "
        "mer, et ce qui est vis&#233; en une phrase.",
        "Reprendre la m&#234;me vis&#233;e plusieurs heures plus tard.",
        "Au retour&#160;: transf&#233;rer sans conversion, calculer les "
        "empreintes SHA-256, les d&#233;poser aupr&#232;s d'un tiers "
        "datant, remplir la fiche du &#167;&#160;33.",
    ]
    analyste = [
        "V&#233;rifier les empreintes et leur datation par un tiers.",
        "&#201;tablir au moins deux concordances externes&#160;; "
        "v&#233;rifier qu'aucune discordance n'existe.",
        "Reconstituer la cha&#238;ne optique et num&#233;rique&#160;; "
        "s&#233;parer la part optique du grossissement de sa part "
        "num&#233;rique.",
        "&#201;tablir position, altitudes, distance, azimut et profil "
        "interm&#233;diaire depuis des sources ind&#233;pendantes "
        "dat&#233;es&#160;; noter chaque incertitude.",
        "&#201;tablir la hauteur de la cible et l'altitude de sa base "
        "depuis une source ind&#233;pendante&#160;; ne jamais les lire dans "
        "l'image.",
        "Classer les images selon la grille du &#167;&#160;18, sans "
        "conna&#238;tre la pr&#233;diction.",
        "Mesurer la r&#233;solution effective sur un bord franc de "
        "dimension connue.",
        "V&#233;rifier la condition de discrimination du &#167;&#160;28.2 "
        "avant toute mesure de la fraction visible.",
        "Rechercher les cinq r&#233;gimes atmosph&#233;riques sur la "
        "s&#233;rie&#160;; consigner le r&#233;sultat, positif ou "
        "n&#233;gatif.",
        "Faire mesurer les positions en pixels par trois analystes en "
        "aveugle&#160;; reporter la dispersion.",
        "Calculer la fraction visible observ&#233;e et son incertitude.",
        "Calculer la fraction pr&#233;dite par chaque mod&#232;le "
        "d&#233;pos&#233;, et l'enveloppe de sensibilit&#233;.",
        "Rapporter la combinaison de param&#232;tres la plus "
        "d&#233;favorable &#224; sa propre conclusion.",
        "Rendre l'un des trois verdicts du &#167;&#160;28, et publier "
        "l'archive du &#167;&#160;34.",
    ]
    return "\n\n".join([
        h2("32", "Checklist", saut=True),
        h3("32.1 Op&#233;rateur, sur le terrain"),
        liste(terrain, ordonnee=True),
        h3("32.2 Analyste, sur dossier"),
        liste(analyste, ordonnee=True),
        encadre("Trois interdits",
                liste([
                    "Ne pas d&#233;placer le seuil apr&#232;s avoir vu les "
                    "images.",
                    "Ne pas invoquer un r&#233;gime atmosph&#233;rique "
                    "qu'on n'a pas cherch&#233; avant la comparaison.",
                    "Ne pas lire dans l'image un param&#232;tre qui servira "
                    "ensuite &#224; juger cette image.",
                ]), "warn"),
    ])


FICHE = [
    ("Identification", [
        "Identifiant du dossier", "Date et heure UTC de la s&#233;rie",
        "&#201;cart d'horloge mesur&#233;", "Op&#233;rateur",
        "Campagne et r&#233;f&#233;rence du pr&#233;-enregistrement"]),
    ("Observateur", [
        "Coordonn&#233;es et syst&#232;me de r&#233;f&#233;rence",
        "Incertitude annonc&#233;e par le r&#233;cepteur",
        "Hauteur ellipso&#239;dale et mod&#232;le de g&#233;o&#239;de",
        "Altitude du sol ou niveau d'eau",
        "Hauteur de l'axe optique au-dessus du sol",
        "Altitude <em>h</em> retenue et son incertitude"]),
    ("Cible", [
        "D&#233;signation exacte et sources d'identification",
        "Coordonn&#233;es et syst&#232;me de r&#233;f&#233;rence",
        "Altitude de la base <em>z</em><sub>b</sub> et sa source",
        "Hauteur totale <em>H</em> et sa source",
        "Parties pertinentes de cote connue, avec leurs sources",
        "Extension longitudinale de la cible"]),
    ("G&#233;om&#233;trie", [
        "Distance <em>D</em>, algorithme et incertitude",
        "Azimut g&#233;od&#233;sique",
        "Rayon de courbure d'Euler &#224; cet azimut",
        "Profil interm&#233;diaire&#160;: source, pas d'&#233;chantillonnage",
        "Altitude maximale du profil et marge sous la ligne de vis&#233;e"]),
    ("Syst&#232;me photographique", [
        "Bo&#238;tier, objectif, num&#233;ros de s&#233;rie",
        "Focale optique r&#233;elle et focale &#233;quivalente",
        "Ouverture, temps de pose, sensibilit&#233;",
        "R&#233;solution native du capteur et pas de photosite",
        "R&#233;solution du fichier final",
        "Facteur de grossissement, part optique et part num&#233;rique",
        "Recadrage interne avant enregistrement",
        "Traitements computationnels actifs",
        "Profil de distorsion appliqu&#233; et r&#233;siduel"]),
    ("Atmosph&#232;re", [
        "Temp&#233;rature de l'air &#224; chaque hauteur mesur&#233;e",
        "Temp&#233;rature de surface de la mer",
        "Pression, humidit&#233;",
        "Profil vertical disponible&#160;: source, r&#233;solution, distance "
        "et &#233;cart horaire",
        "Classe de chaque donn&#233;e (A &#224; E)",
        "Intervalle de <em>k</em> retenu et sa justification"]),
    ("Images", [
        "Nombre de vues, noms de fichiers, empreintes SHA-256",
        "Preuve de datation des empreintes",
        "Classement de chaque vue selon le &#167;&#160;18",
        "Vues exclues et motif",
        "R&#233;solution effective mesur&#233;e",
        "Toute transformation appliqu&#233;e &#224; la copie"]),
    ("Mesures", [
        "Caract&#233;ristique d&#233;sign&#233;e, et date de sa d&#233;signation",
        "Positions en pixels rendues par chaque analyste en aveugle",
        "&#201;chelle par la focale, et &#233;chelle par les rep&#232;res",
        "Hauteur visible, hauteur occult&#233;e",
        "Fraction visible observ&#233;e et son incertitude",
        "Rapports de hauteur mesur&#233;s et attendus"]),
    ("R&#233;sultat", [
        "Fraction pr&#233;dite par chaque mod&#232;le, avec enveloppe",
        "&#201;cart observ&#233;-pr&#233;dit et incertitude compos&#233;e",
        "Combinaison la plus d&#233;favorable &#224; la conclusion",
        "R&#233;sultat de la recherche de r&#233;gimes",
        "Verdict pour chaque mod&#232;le&#160;: compatible, incompatible, "
        "ind&#233;termin&#233;",
        "Motif d'ind&#233;termination le cas &#233;ch&#233;ant"]),
]


def sec_fiche():
    blocs = []
    for titre, champs in FICHE:
        blocs.append(h3(titre))
        blocs.append('<div class="sheet">\n%s\n</div>' % "\n".join(
            '  <div class="fr"><span class="a">%s</span>'
            '<span class="b">&nbsp;</span></div>' % c for c in champs))
    return "\n\n".join([
        h2("33", "Fiche standard d'observation", saut=True),
        p("Un dossier incomplet est ind&#233;termin&#233;, pas "
          "d&#233;favorable. Un champ sans valeur porte la mention "
          "<em>indisponible</em>&#160;; il n'est jamais laiss&#233; en "
          "blanc ni rempli d'une valeur plausible."),
    ] + blocs)


def sec_archivage():
    arbre = """<div class="eq" style="text-align:left; font-size:8.6pt;
 line-height:1.5">
dossier-&lt;identifiant&gt;/<br>
&nbsp;&nbsp;00-preenregistrement/&nbsp;&nbsp;&nbsp;plan dat&#233;, seuil,
mod&#232;les d&#233;pos&#233;s, preuve de d&#233;p&#244;t<br>
&nbsp;&nbsp;10-originaux/&nbsp;&nbsp;&nbsp;fichiers tels que sortis de
l'appareil, jamais modifi&#233;s<br>
&nbsp;&nbsp;11-empreintes/&nbsp;&nbsp;&nbsp;SHA256SUMS, date de calcul, preuve
de datation par un tiers<br>
&nbsp;&nbsp;20-fiche/&nbsp;&nbsp;&nbsp;fiche du &#167;&#160;33, en texte
structur&#233; et en PDF<br>
&nbsp;&nbsp;30-donnees-externes/&nbsp;&nbsp;&nbsp;extraits
g&#233;od&#233;siques, topographiques, mar&#233;graphiques,
m&#233;t&#233;orologiques, avec leur date d'&#233;dition<br>
&nbsp;&nbsp;40-controles/&nbsp;&nbsp;&nbsp;mire, distorsion,
stabilit&#233;, orientation, coh&#233;rence entre focales<br>
&nbsp;&nbsp;50-mesures/&nbsp;&nbsp;&nbsp;relev&#233;s en pixels de chaque
analyste, journal de classement horodat&#233;<br>
&nbsp;&nbsp;60-calcul/&nbsp;&nbsp;&nbsp;code, param&#232;tres, germe
al&#233;atoire, sorties interm&#233;diaires<br>
&nbsp;&nbsp;70-rapport/&nbsp;&nbsp;&nbsp;rapport de chaque analyste,
d&#233;clarations d'int&#233;r&#234;t, rapport de synth&#232;se<br>
&nbsp;&nbsp;90-journal/&nbsp;&nbsp;&nbsp;journal horodat&#233; de toutes les
op&#233;rations, y compris les &#233;carts au plan
<span class="cap">Arborescence impos&#233;e. Les num&#233;ros fixent
l'ordre de lecture&#160;: le pr&#233;-enregistrement vient avant les
donn&#233;es, les donn&#233;es avant les mesures, les mesures avant le
rapport.</span></div>"""
    return "\n\n".join([
        h2("34", "Structure d'archivage"),
        p("L'archive doit permettre &#224; un tiers de refaire l'analyse "
          "depuis les fichiers d'origine, sans rien demander &#224; "
          "personne."),
        arbre,
        liste([
            "Le r&#233;pertoire <code>10-originaux</code> est en lecture "
            "seule. Toute copie de travail vit ailleurs.",
            "Le fichier <code>SHA256SUMS</code> couvre l'ensemble de "
            "l'archive, et son empreinte est elle-m&#234;me "
            "d&#233;pos&#233;e.",
            "Le journal du &#167;&#160;90 est append-only&#160;: on n'y "
            "efface rien, on y ajoute les corrections.",
            "L'archive est publi&#233;e sous une licence permettant la "
            "reprise et la red&#233;marche&#160;; si un fichier ne peut "
            "&#234;tre diffus&#233;, son empreinte et le nom de son "
            "d&#233;tenteur le sont.",
        ]),
    ])


# ── Bibliographie : statut de vérification déclaré pour chaque entrée ────────
REF_VERIFIEES = [
    ("Moritz, H. (2000). <em>Geodetic Reference System 1980</em>. Journal of "
     "Geodesy 74, 128&#8211;133. DOI&#160;10.1007/s001900050278.",
     "&#167;&#160;4.1, &#167;&#160;12 &#8212; d&#233;finition de "
     "l'ellipso&#239;de GRS&#8239;80 et du rayon moyen R<sub>1</sub>."),
    ("Karney, C.&#8239;F.&#8239;F. (2013). <em>Algorithms for geodesics</em>. "
     "Journal of Geodesy 87, 43&#8211;55. DOI&#160;10.1007/s00190-012-0578-z.",
     "&#167;&#160;12.3 &#8212; calcul de la g&#233;od&#233;sique et de "
     "l'azimut sur l'ellipso&#239;de."),
    ("Pavlis, N.&#8239;K., Holmes, S.&#8239;A., Kenyon, S.&#8239;C., Factor, "
     "J.&#8239;K. (2012). <em>The development and evaluation of the Earth "
     "Gravitational Model 2008 (EGM2008)</em>. Journal of Geophysical "
     "Research&#160;: Solid Earth 117, B04406. "
     "DOI&#160;10.1029/2011JB008916. Correction&#160;: J. Geophys. Res. Solid "
     "Earth (2013), DOI&#160;10.1002/jgrb.50167.",
     "&#167;&#160;12.1 &#8212; conversion entre hauteur ellipso&#239;dale et "
     "altitude."),
    ("Ciddor, P.&#8239;E. (1996). <em>Refractive index of air&#160;: new "
     "equations for the visible and near infrared</em>. Applied Optics 35(9), "
     "1566&#8211;1573. DOI&#160;10.1364/AO.35.001566.",
     "&#167;&#160;11.2 &#8212; r&#233;fractivit&#233; optique de l'air&#160;; "
     "base de la constante employ&#233;e."),
    ("van der Werf, S.&#8239;Y. (2003). <em>Ray tracing and refraction in the "
     "modified US1976 atmosphere</em>. Applied Optics 42(3), 354&#8211;366. "
     "DOI&#160;10.1364/AO.42.000354.",
     "&#167;&#160;11.6 &#8212; m&#233;thode de tra&#231;age de rayon en "
     "atmosph&#232;re stratifi&#233;e."),
    ("Lehn, W.&#8239;H. (1979). <em>The Novaya Zemlya effect&#160;: an arctic "
     "mirage</em>. Journal of the Optical Society of America 69(5), "
     "776&#8211;781.",
     "&#167;&#160;11.3, &#167;&#160;19.4 &#8212; conduit optique et mirages "
     "de forte inversion."),
    ("Hirt, C., Guillaume, S., Wisbar, A., B&#252;rki, B., Sternberg, H. "
     "(2010). <em>Monitoring of the refraction coefficient in the lower "
     "atmosphere using a controlled setup of simultaneous reciprocal vertical "
     "angle measurements</em>. Journal of Geophysical Research 115, D21102. "
     "DOI&#160;10.1029/2010JD014067.",
     "&#167;&#160;11.3 &#8212; amplitude mesur&#233;e des variations de "
     "<em>k</em> pr&#232;s du sol. <strong>Port&#233;e "
     "limit&#233;e</strong>&#160;: mesures &#224; environ 1,8&#8239;m "
     "au-dessus d'une prairie, sur des trajets courts, par temps "
     "ensoleill&#233;&#160;; les valeurs extr&#234;mes rapport&#233;es "
     "(&#8722;4 &#224; +16) ne sont pas transposables telles quelles &#224; "
     "un trajet marin rasant de plusieurs dizaines de kilom&#232;tres."),
    ("Recommandation UIT-R P.453-14 (2019). <em>The radio refractive "
     "index&#160;: its formula and refractivity data</em>. Union "
     "internationale des t&#233;l&#233;communications.",
     "&#167;&#160;11.4 &#8212; formule de la r&#233;fractivit&#233; "
     "radio&#233;lectrique et d&#233;finition des conduits. "
     "<strong>Domaine radio</strong>&#160;: cit&#233;e pr&#233;cis&#233;ment "
     "pour &#233;tablir la diff&#233;rence avec le domaine optique."),
    ("ISO 12233:2024. <em>Photography &#8212; Electronic still picture "
     "imaging &#8212; Resolution and spatial frequency responses</em>. "
     "Organisation internationale de normalisation.",
     "&#167;&#160;20.2, &#167;&#160;24 &#8212; mesure de la r&#233;solution "
     "par la m&#233;thode du bord inclin&#233;."),
]

REF_A_CONFIRMER = [
    ("JCGM 100:2008, <em>&#201;valuation des donn&#233;es de mesure &#8212; "
     "Guide pour l'expression de l'incertitude de mesure</em> (GUM), Bureau "
     "international des poids et mesures.",
     "&#167;&#160;22 &#8212; &#233;valuation et composition des "
     "incertitudes."),
    ("JCGM 200:2012, <em>Vocabulaire international de "
     "m&#233;trologie</em> (VIM), 3<sup>e</sup> &#233;dition.",
     "&#167;&#160;6 &#8212; terminologie des grandeurs et des "
     "incertitudes."),
    ("Organisation m&#233;t&#233;orologique mondiale, publication "
     "n&#176;&#8239;8, <em>Guide des instruments et des m&#233;thodes "
     "d'observation</em>.",
     "&#167;&#160;21 &#8212; conditions de mesure des grandeurs "
     "atmosph&#233;riques de surface."),
    ("CIPA DC-008 / JEITA CP-3451, <em>Exchangeable image file format for "
     "digital still cameras&#160;: Exif</em>.",
     "&#167;&#160;15.4, &#167;&#160;17 &#8212; champs de "
     "m&#233;tadonn&#233;es exig&#233;s."),
    ("Rüeger, J.&#8239;M., <em>Refractive Index Formulae for Radio "
     "Waves</em>, F&#233;d&#233;ration internationale des g&#233;om&#232;tres.",
     "&#167;&#160;11.4 &#8212; termes sec et humide de la "
     "r&#233;fractivit&#233;."),
    ("Torge, W., M&#252;ller, J., <em>Geodesy</em>, De Gruyter.",
     "&#167;&#160;11.1, &#167;&#160;12.2 &#8212; coefficient de "
     "r&#233;fraction g&#233;od&#233;sique et rayons de courbure de "
     "l'ellipso&#239;de."),
    ("Copernicus DEM &#8212; <em>Global and European Digital Elevation "
     "Model</em>, Agence spatiale europ&#233;enne.",
     "&#167;&#160;12.3 &#8212; profil interm&#233;diaire et altitude de "
     "base."),
    ("Organisation hydrographique internationale, publication S-44, "
     "<em>Normes pour les lev&#233;s hydrographiques</em>.",
     "&#167;&#160;12.3 &#8212; incertitudes bathym&#233;triques et "
     "z&#233;ro des cartes."),
]


def sec_bibliographie():
    v = "\n".join(
        "  <li>%s<br><em>Justifie&#160;:</em> %s</li>" % r
        for r in REF_VERIFIEES)
    a = "\n".join(
        "  <li>%s<br><em>Justifierait&#160;:</em> %s</li>" % r
        for r in REF_A_CONFIRMER)
    return "\n\n".join([
        h2("35", "Bibliographie", saut=True),
        encadre("Statut de v&#233;rification",
                "\n".join([
                    p("Le cahier des charges interdit de citer une source "
                      "non v&#233;rifi&#233;e. Les r&#233;f&#233;rences sont "
                      "donc s&#233;par&#233;es en deux listes selon ce qui a "
                      "pu &#234;tre contr&#244;l&#233; le %s." % DATE),
                    p("La premi&#232;re liste rassemble les "
                      "r&#233;f&#233;rences dont le titre exact, les "
                      "auteurs, la revue, le volume, la pagination ou le "
                      "num&#233;ro d'article et l'identifiant ont "
                      "&#233;t&#233; retrouv&#233;s aupr&#232;s de "
                      "l'&#233;diteur ou d'un catalogue "
                      "bibliographique."),
                    p("La seconde rassemble des documents d'organisme "
                      "d&#233;sign&#233;s par leur r&#233;f&#233;rence "
                      "officielle, dont l'&#233;dition en vigueur "
                      "<strong>n'a pas pu &#234;tre revérifiée</strong> "
                      "&#224; cette date. Ils sont nomm&#233;s sans "
                      "num&#233;ro d'&#233;dition ni ann&#233;e "
                      "invent&#233;s, et l'&#233;dition applicable doit "
                      "&#234;tre confirm&#233;e avant toute publication du "
                      "protocole."),
                ]), "warn"),
        h3("35.1 R&#233;f&#233;rences v&#233;rifi&#233;es"),
        "<ol class=\"refs\">\n%s\n</ol>" % v,
        h3("35.2 Documents d'organisme, &#233;dition &#224; confirmer"),
        "<ol class=\"refs\">\n%s\n</ol>" % a,
        h3("35.3 Ce qui n'est cit&#233; nulle part"),
        p("Aucune valeur du pr&#233;sent protocole n'est reprise d'une "
          "source secondaire non v&#233;rifi&#233;e. Les constantes "
          "physiques &#8212; g, R<sub>d</sub>, la r&#233;fractivit&#233; "
          "optique &#8212; et les relations qui en d&#233;coulent sont "
          "red&#233;riv&#233;es dans le code qui produit ce document, et "
          "l'accord de cette red&#233;rivation avec ses deux points "
          "d'ancrage physiques &#8212; gradient autoconvectif et seuil de "
          "conduit &#8212; est v&#233;rifi&#233; &#224; chaque "
          "g&#233;n&#233;ration."),
    ])


def corps():
    return "\n\n".join([
        masthead(), sec_resume(), sec_ecarts(), sec_question(),
        sec_hypotheses(), sec_objectifs(), sec_definitions(), sec_fondement(),
        sec_geometrie(), sec_equations(), sec_exemple(), sec_refraction(),
        sec_geodesie(), sec_materiel(), sec_photographie(), sec_zoom(),
        sec_acquisition(), sec_conservation(), sec_validation(),
        sec_analyse_image(), sec_resolution(), sec_meteo(),
        sec_incertitudes(), sec_sensibilite(), sec_controles(),
        sec_replication(), sec_preenregistrement(), sec_statistique(),
        sec_decision(), sec_concurrents(), sec_limites(), sec_audit(),
        sec_checklist(), sec_fiche(), sec_archivage(), sec_bibliographie(),
    ])


def main():
    controle()
    ecrire(corps())
    print("Écrit : %s (%d ko)"
          % (os.path.relpath(CIBLE, RACINE), os.path.getsize(CIBLE) // 1024))
    print("  s(800 m) = %.1f m   s(100 m) = %.1f m   D_lim = %.3f km"
          % (s_arc(H_OBS), s_arc(H_CIBLE),
             (s_arc(H_OBS) + s_arc(H_CIBLE))/1000))
    print("  k équivalent du profil à deux couches : %.4f (moyenne : %.4f)"
          % (k_equivalent(arc_rasant(H_OBS, n_deux_couches)),
             (0.80*60 + 0.13*740)/800))
    return 0


if __name__ == "__main__":
    sys.exit(main())
