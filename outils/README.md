# Outils de visée optique — paquets Python de référence

Trois paquets qui implémentent le protocole « Portion visible d'une cible
éloignée au-dessus de la mer » v1.0, plus un pré-écran altimétrique et quatre
cas d'étude.

## Ce que ces paquets sont pour le site

**La référence.** Le calculateur du Lab tourne dans le navigateur, donc en
TypeScript (`src/lib/visee-optique/noyau.ts`), mais ce port n'est pas
autoritaire : il est épinglé à ce Python par 61 vecteurs d'or et 263 contrôles.

    python3 scripts/generer-vecteurs-or-visee.py    # outil A — regénère les vecteurs
    python3 scripts/generer-vecteurs-or-preuve.py  # outil B — idem
    python3 scripts/generer-vecteurs-or-rapport.py # outil C — idem
    npm run verifier:ports                         # vérifie que les trois ports n'ont pas dérivé

Les trois ports sont épinglés :

| Port | Référence | Vecteurs | Contrôles |
|---|---|---|---|
| `src/lib/visee-optique/noyau.ts` | outil A, 321 tests | 61 | 263 |
| `src/lib/preuve-image/noyau.ts` | outil B, 137 tests | 26 | 152 |
| `src/lib/rapport-expertise/noyau.ts` | outil C, 42 tests | 22 | 117 |

Les trois harnais ont été éprouvés en cassant volontairement le port : un tag
EXIF décalé d'un cran, le signe de l'hémisphère sud oublié, l'arc de tangence
biaisé de 10⁻⁷, un champ retiré d'un bloc de la fiche, deux répertoires de
l'arborescence intervertis — chacun est détecté et nommé.

Toute correction de formule se fait **dans le Python d'abord**, puis se
répercute dans le port, puis les vecteurs sont régénérés. Jamais l'inverse.

## Installation

    python3 -m venv outils/.venv
    outils/.venv/bin/pip install pytest numpy scipy Pillow PyWavelets
    outils/.venv/bin/pip install -e outils/outil-A-visee-optique \
                                 -e outils/outil-B-preuve-image \
                                 -e outils/outil-C-rapport-expertise

## Tests

    cd outils/outil-A-visee-optique   && ../.venv/bin/python -m pytest -q   # 321
    cd outils/outil-B-preuve-image    && ../.venv/bin/python -m pytest -q   # 137
    cd outils/outil-C-rapport-expertise && ../.venv/bin/python -m pytest -q #  42

## Ce qui a changé depuis la livraison

**Vincenty a été promue dans `visee_optique.geodesy`.** Elle vivait en cinq
copies hors du paquet — le pré-écran et les quatre `case_data.py` — donc hors
de toute couverture, alors que c'est elle qui produit le D et l'azimut dont
dépend tout le reste. Les cinq copies étaient numériquement identiques : le
risque était latent, pas réalisé.

Deux différences ont été introduites à dessein :

- **La non-convergence n'est plus silencieuse.** Les copies sortaient de la
  boucle après `max_iter` sans le signaler, et retournaient le dernier itéré
  comme si c'était une distance. Un couple quasi-antipodal lève maintenant.
- **`azimut_2_vers_1` est renommé `azimut_arrivee_deg`.** La formule retourne
  α₂, l'azimut *au point d'arrivée dans le même sens de parcours*, pas le
  gisement de retour. Sur l'équateur vers l'est, les copies retournaient 90°
  sous un nom qui promet 270° : qui s'en servait comme d'un azimut de retour
  se trompait d'un demi-tour. Le test l'a attrapé.

Vingt-six tests couvrent désormais ces deux fonctions, dont deux qui les
confrontent à des résultats obtenus **sans** Vincenty : sur l'équateur la
distance vaut exactement a·Δλ, et sur un méridien elle vaut l'intégrale du
rayon méridien, calculée ici par quadrature.

## Ce que le port de l'outil B fait en plus

Le vérificateur d'intégrité tourne **entièrement dans le navigateur** : le
fichier de l'utilisateur n'est jamais transmis, ni stocké, ni journalisé. Ce
n'est pas qu'une commodité d'hébergement, c'est ce qu'un tiers de confiance
doit pouvoir dire de son propre outil — et c'est vérifié plutôt qu'affirmé :
zéro requête réseau relevée pendant l'analyse d'un fichier.

Le SHA-256 passe par WebCrypto, la même primitive dans le navigateur et dans
Node. Il a été confronté à `sha256sum` du système, une troisième
implémentation indépendante du Python comme du navigateur : identique.

## L'archive produite par le navigateur, validée par le Python

Le générateur de fiche écrit un ZIP sans compression, à la main
(`src/lib/rapport-expertise/zip.ts`, aucune dépendance). Sans compression
délibérément : l'empreinte d'un fichier est alors la même dans l'archive et
hors d'elle, donc le manifeste se contrôle sans décompresseur.

Trois contre-épreuves indépendantes plutôt qu'une affirmation :

- `unzip -t` ne détecte aucune erreur, et le CRC-32 rend la valeur normalisée
  `cbf43926` sur la chaîne d'épreuve `123456789` ;
- `sha256sum -c SHA256SUMS` valide le manifeste produit dans le navigateur,
  avec les vrais fichiers ;
- `rapport_expertise.archive.verifier_arborescence` — la fonction Python
  elle-même — déclare l'arborescence conforme au §34, aucun répertoire
  manquant.

Et `originaux_proteges` retourne False, comme attendu : le verrouillage Unix de
`10-originaux/` est la seule chose que le navigateur ne peut pas faire. Le
LISEZ-MOI de l'archive donne la commande plutôt que de la simuler.

## Ce qui reste à faire

- Le pré-écran et les quatre `case_data.py` portent encore leur copie de
  Vincenty. Ils devraient importer le paquet.
- Les cas d'étude ne tournent pas tels que livrés : ils importent un
  `build_demo_image` absent de l'archive et codent en dur `/home/claude/...`
  dans `sys.path`. Comme documentation de l'API ils restent excellents.
- Le pré-écran altimétrique exige un accès réseau serveur vers l'API IGN, non
  disponible côté navigateur (CORS) ni depuis l'environnement de développement
  actuel. Il n'est pas intégré au site.
