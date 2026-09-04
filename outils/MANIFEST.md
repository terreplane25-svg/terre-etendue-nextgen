# Contenu de cette livraison

Trois paquets Python, testés (474 tests, tous passants), implémentant le
protocole « Portion visible d'une cible éloignée au-dessus de la mer » v1.0 :

- `outil-A-visee-optique/` — géométrie géodésique (Vincenty, rayon d'Euler),
  modèles concurrents (sphère à réfraction vs plan), condition de
  discrimination §28.2, verdict à trois valeurs §28.3.
- `outil-B-preuve-image/` — intégrité de fichier (SHA-256), lecture EXIF/GPS,
  chaîne de détention ISO/IEC 27037, mesure d'échelle.
- `outil-C-rapport-expertise/` — assemble A et B dans la fiche standard
  d'observation (§33) et l'arborescence d'archive figée (§34).

`outil-bonus-pre-ecran/profil_altimetrique.py` : script de pré-écran
altimétrique (interroge l'API IGN RGE ALTI pour vérifier qu'une ligne
d'observation reste en mer) — pas un des trois outils originaux, mais utile
pour une fonctionnalité « vérifier un site avant de le proposer ».

`exemples-cas-etudes/` : quatre cas réels bout-en-bout (`case_data.py` +
`run_case.py` chacun) montrant comment les trois outils s'assemblent en
pratique — y compris un cas invalidé (Chassiron↔Cordouan) et deux cas
validés (Sangatte↔South Foreland, Garoupe↔Monte Cinto).

Voir le texte de brief fourni séparément pour la demande d'intégration.
