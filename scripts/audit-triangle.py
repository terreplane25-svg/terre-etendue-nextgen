#!/usr/bin/env python3
"""
Audit d'un bloc de triangle d'archive — contrôles 2 à 5 de la grille
de content/reseau/mesures-brutes.json.

Le contrôle 1 (certification visuelle) et le 6 (absence de calcul joint) sont
humains : ils se font en regardant le bloc reçu, pas ici.

Usage :
    python3 scripts/audit-triangle.py bloc.json

Le bloc accepte deux formes, selon ce que publie la source.

Forme A — trois angles observés :
    {
      "id": "...",
      "angles": [[63, 11, 58.12], [58, 22, 14.10], [58, 25, 52.20]],
      "somme_imprimee": [180, 0, 4.42],
      "cotes_km": [22.108, 20.896, 20.911],        // OPPOSÉS aux angles, dans l'ordre
      "unite_cotes": "km",                          // km | toises | m
      "sigma_par_angle_secondes": 0.4,              // facultatif
      "sommets": ["Montjouy", "Sapeira", "N.-D."]   // facultatif
    }

Forme B — les deux colonnes des rapports de triangulation :
    {
      "id": "...",
      "spherical_excess_secondes": 5.50,
      "error_of_triangle_secondes": -0.42,
      "cotes_km": [50.1, 48.7, 52.3],
      "sigma_par_angle_secondes": 0.3
    }
    La somme observée est alors reconstituée :
        somme = 180° + spherical_excess + error_of_triangle

Sortie : un verdict par contrôle, et un verdict global.
"""

import json
import math
import sys

R = 6_371_008.8          # rayon moyen, m
ARCSEC = 206_264.806     # radians -> secondes d'arc
TOISE = 1.949036         # toise de Paris -> m


def dms(t):
    """[d, m, s] -> degrés décimaux."""
    d, m, s = t
    return d + m / 60 + s / 3600


def fmt_dms(deg):
    d = int(deg)
    reste = (deg - d) * 3600
    m = int(reste // 60)
    return f"{d}° {m:02d}′ {reste - m * 60:.2f}″"


def heron(a, b, c):
    s = (a + b + c) / 2
    p = s * (s - a) * (s - b) * (s - c)
    return math.sqrt(p) if p > 0 else 0.0


def ligne(ok, texte):
    return f"  [{'OK ' if ok else 'ÉCHEC'}] {texte}"


def main(chemin):
    bloc = json.load(open(chemin, encoding="utf-8"))
    verdicts = []
    print(f"\nAUDIT — {bloc.get('id', '(sans id)')}")
    if bloc.get("sommets"):
        print(f"  sommets : {' / '.join(bloc['sommets'])}")
    print()

    # ---- reconstitution de la somme observée --------------------------------
    angles = bloc.get("angles")
    if angles:
        somme = sum(dms(a) for a in angles)
        exces_obs = (somme - 180) * 3600
        print(f"  forme A — trois angles observés")
        for i, a in enumerate(angles, 1):
            print(f"    angle {i} : {fmt_dms(dms(a))}")
        print(f"    somme recalculée : {fmt_dms(somme)}")

        # CONTRÔLE 2 — la somme recalculée reproduit la somme imprimée
        if bloc.get("somme_imprimee"):
            imp = dms(bloc["somme_imprimee"])
            ecart = (somme - imp) * 3600
            ok = abs(ecart) < 0.01
            verdicts.append(ok)
            print(f"    somme imprimée   : {fmt_dms(imp)}")
            print(ligne(ok, f"contrôle 2 — somme : écart {ecart:+.3f}″ (tolérance 0,01″)"))
        else:
            print("  [n/a  ] contrôle 2 — somme imprimée non fournie")
    else:
        se = bloc.get("spherical_excess_secondes")
        et = bloc.get("error_of_triangle_secondes")
        if se is None or et is None:
            sys.exit("Bloc invalide : ni 'angles', ni le couple "
                     "'spherical_excess_secondes' + 'error_of_triangle_secondes'.")
        exces_obs = se + et
        somme = 180 + exces_obs / 3600
        print(f"  forme B — colonnes du rapport")
        print(f"    spherical excess   : {se:+.3f}″  (calculé par l'auteur)")
        print(f"    error of triangle  : {et:+.3f}″  (résidu de mesure)")
        print(f"    somme observée reconstituée : {fmt_dms(somme)}")
        print("  [n/a  ] contrôle 2 — sans objet en forme B")

    print(f"\n  EXCÈS OBSERVÉ : {exces_obs:+.3f}″\n")

    # ---- côtés --------------------------------------------------------------
    cotes = bloc.get("cotes_km")
    unite = bloc.get("unite_cotes", "km")
    if cotes:
        if unite == "toises":
            cotes_m = [c * TOISE for c in cotes]
        elif unite == "m":
            cotes_m = list(cotes)
        else:
            cotes_m = [c * 1000 for c in cotes]
    else:
        cotes_m = None

    # CONTRÔLE 3 — loi des sinus
    if angles and cotes_m:
        A = [dms(a) for a in angles]
        # L'ordre est IMPOSÉ : cotes_km[i] est le côté opposé à angles[i].
        # Ne jamais chercher la meilleure permutation — le nommage des sommets
        # fixe l'appariement, et permuter librement fabrique un accord qui
        # n'existe pas. C'est ce contrôle qui a rejeté le bloc 5.
        r = [cotes_m[i] / math.sin(math.radians(A[i])) for i in range(3)]
        disp = (max(r) - min(r)) / (sum(r) / 3) * 100
        perm = (0, 1, 2)
        # tolérance = dispersion induite par l'arrondi des côtés imprimés
        pas = 10 ** -max((len(str(c).split(".")[1]) if "." in str(c) else 0) for c in cotes)
        pas_m = pas * (TOISE if unite == "toises" else 1 if unite == "m" else 1000)
        tol = max(pas_m / min(cotes_m) * 100 * 2, 0.05)
        ok = disp <= tol
        verdicts.append(ok)
        print(f"  loi des sinus — c/sin(A) : {' / '.join(f'{x/1000:.3f}' for x in r)}")
        print(ligne(ok, f"contrôle 3 — dispersion {disp:.2f} % (tolérance {tol:.2f} %)"))
        imax = max(range(3), key=lambda i: A[i])
        cmax = max(range(3), key=lambda i: cotes_m[perm[i]])
        if imax != cmax:
            print("         >>> le plus grand angle ne fait PAS face au plus grand côté")
    else:
        print("  [n/a  ] contrôle 3 — loi des sinus : angles ou côtés manquants")

    # CONTRÔLE 4 — vraisemblance de la fermeture
    if cotes_m:
        aire = heron(*cotes_m)
        pred = aire / R**2 * ARCSEC
        residu = exces_obs - pred
        sig = bloc.get("sigma_par_angle_secondes")
        print(f"\n  aire (Heron)        : {aire/1e6:.1f} km²")
        print(f"  excès prédit A/R²   : {pred:+.3f}″")
        print(f"  résidu observé−prédit : {residu:+.3f}″")
        if sig:
            ss = math.sqrt(3) * sig
            n = abs(residu) / ss if ss else float("inf")
            ok = n <= 4
            verdicts.append(ok)
            print(ligne(ok, f"contrôle 4 — résidu à {n:.2f} σ (σ somme = {ss:.3f}″, seuil 4 σ)"))
        else:
            print("  [n/a  ] contrôle 4 — σ instrumental non fourni")
        if exces_obs > 0:
            Rd = math.sqrt(aire / (exces_obs / ARCSEC))
            print(f"\n  RAYON DÉDUIT  R = √(A/ε) : {Rd/1000:.1f} km", end="")
            if sig:
                # dR/R = (1/2)·(σ_somme / ε)
                rel = 0.5 * (math.sqrt(3) * sig) / exces_obs
                print(f"  ± {Rd*rel/1000:.0f} km  ({rel*100:.1f} %)")
                if rel > 0.15:
                    print("         >>> incertitude sur R supérieure à 15 % : cet indicateur")
                    print("             n'est PAS un critère de rejet sur ce triangle. Le résidu")
                    print("             de mesure y domine l'excès. Voir contrôle 4.")
            else:
                print()
        else:
            print("\n  excès observé négatif ou nul — rayon non calculable")
    else:
        print("  [n/a  ] contrôle 4 — côtés non fournis")

    print()
    if not verdicts:
        print("  VERDICT : indéterminé — pas assez de champs pour un contrôle automatique.")
    elif all(verdicts):
        print(f"  VERDICT : PASSE les {len(verdicts)} contrôles automatiques.")
        print("            Reste à vérifier à la main : contrôle 1 (image) et 6 (aucun calcul joint).")
    else:
        print(f"  VERDICT : ÉCHEC — {verdicts.count(False)} contrôle(s) sur {len(verdicts)}.")
        print("            Ne pas verser dans mesures-brutes.json.")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
