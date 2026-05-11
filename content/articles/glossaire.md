---
title: "Glossaire"
description: ".nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999} .nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;ju..."
date: "2026-04-17"
author: "Terre Etendue"
category: "headquarters"
tags: []
---

.nx-nav{width:100%;background:#F7F2E8;border-bottom:1px solid #DDD5C5;padding:0 2rem;position:sticky;top:0;z-index:999}
.nx-nav__inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;gap:1.5rem}
/* Logo */
.nx-nav__logo{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.1rem;font-weight:700;color:#B8860B;text-decoration:none;letter-spacing:-.01em;white-space:nowrap;flex-shrink:0}
.nx-nav__logo:hover{color:#D4A017}
/* Liens */
.nx-nav__links{display:flex;align-items:center;gap:1.8rem;list-style:none;margin:0;padding:0}
.nx-nav__links a{font-family:'Outfit',sans-serif;font-size:.73rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#5C4A3A;text-decoration:none;padding:.5em 0;position:relative;transition:color .3s ease;white-space:nowrap}
.nx-nav__links a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:#B8860B;transition:width .3s ease}
.nx-nav__links a:hover{color:#2C1810}
.nx-nav__links a:hover::after{width:100%}
/* Recherche */
.nx-nav__search{position:relative;flex-shrink:0}
.nx-nav__search-btn{background:none;border:none;cursor:pointer;color:#8A7A6A;font-size:1rem;padding:6px;transition:color .3s ease;display:flex;align-items:center}
.nx-nav__search-btn:hover{color:#B8860B}
.nx-nav__search-box{position:absolute;top:calc(100% + 12px);right:0;width:0;opacity:0;overflow:hidden;transition:all .35s cubic-bezier(.16,1,.3,1);background:#EDE5D5;border:1px solid #DDD5C5;border-radius:8px;padding:0;z-index:1000}
.nx-nav__search-box.open{width:300px;opacity:1;padding:.6rem}
.nx-nav__search-input{width:100%;background:transparent;border:none;outline:none;font-family:'Outfit',sans-serif;font-size:.82rem;color:#2C1810;padding:.4em .6em;caret-color:#B8860B}
.nx-nav__search-input::placeholder{color:#8A7A6A}
/* Hamburger */
.nx-nav__toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-shrink:0}
.nx-nav__toggle span{display:block;width:22px;height:2px;background:#5C4A3A;margin:5px 0;transition:all .3s ease}
/* Mobile */
@media(max-width:900px){
 .nx-nav__toggle{display:block}
 .nx-nav__links{display:none;position:absolute;top:64px;left:0;right:0;background:#EDE5D5;border-bottom:1px solid #DDD5C5;flex-direction:column;padding:1rem 2rem;gap:0}
 .nx-nav__links.open{display:flex}
 .nx-nav__links li{width:100%}
 .nx-nav__links a{display:block;padding:.8em 0;border-bottom:1px solid #141414}
 .nx-nav__links li:last-child a{border-bottom:none}
 .nx-nav__search-box.open{width:calc(100vw - 4rem);right:-1rem}
}


 [Terre Étendue Islam](/)
 
 
 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 - @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');
.sp{background:#F7F2E8;color:#2C1810;min-height:80vh;padding:6rem 2rem 5rem}
.sp__inner{max-width:800px;margin:0 auto}
.sp__tag{display:inline-block;font-family:'Outfit',sans-serif;font-size:.62rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#B8860B;background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.2);padding:.3em 1em;border-radius:4px;margin-bottom:1.5rem}
.sp__title{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(1.8rem,4.5vw,2.6rem);font-weight:700;color:#B8860B;line-height:1.15;margin:0 0 1.5rem}
.sp__body{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.05rem;line-height:1.8;color:#5C4A3A}
.sp__body p{margin-bottom:1.4em}
.sp__body h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.3rem;font-weight:700;color:#2C1810;margin:2.5em 0 .8em;padding-bottom:.4em;border-bottom:1px solid #DDD5C5}
.sp__body h3{font-family:'Outfit',sans-serif;font-size:.95rem;font-weight:600;color:#B8860B;margin:1.8em 0 .5em}
.sp__body a{color:#B8860B;text-decoration:underline;text-underline-offset:3px}
.sp__body ul{padding-left:1.5em;margin-bottom:1.4em}
.sp__body li{margin-bottom:.6em}
.sp__body strong{color:#2C1810}
.sp__social{display:flex;gap:1rem;flex-wrap:wrap;margin:2em 0}
.sp__social a{display:inline-flex;align-items:center;gap:.5em;padding:.6em 1.2em;background:#EDE5D5;border:1px solid #DDD5C5;border-radius:6px;font-family:'Outfit',sans-serif;font-size:.8rem;font-weight:500;color:#5C4A3A;text-decoration:none;transition:all .3s ease}
.sp__social a:hover{border-color:rgba(212,175,55,.3);color:#2C1810;transform:translateY(-2px)}


 Ressources
 
# Glossaire

Les termes clés utilisés sur ce site, classés par domaine. Ce glossaire est mis à jour au fil des publications.

## Termes coraniques et arabes


 **Daḥā (دَحَا)** — Verbe arabe signifiant « étendre, aplanir ». Utilisé dans le Coran (79:30) pour décrire l'action divine sur la Terre. Voir [B1](/la-terre-dans-le-coran/).

 - **Suṭiḥat (سُطِحَتْ)** — « Elle a été aplanie » (88:20). Racine s-ṭ-ḥ, antonyme de kurawī (sphérique).

 - **Al-udḥiyy (الأُدْحِيّ)** — Le nid aplani de l'autruche dans le sable. Souvent confondu à tort avec l'œuf d'autruche.

 - **Falak (فَلَك)** — Traduit par « orbite » dans les éditions concordistes. Signifie en réalité « vague suspendue » (Mawj al-Makfūf) selon le jumhūr des mufassirīn.

 - **Basaṭa (بَسَطَ)** — Étendre, aplanir. Terme utilisé unanimement par les 8 dictionnaires classiques pour gloser daḥā.

 - **ʿUlamāʾ al-Sharʿ** — Les savants de la Loi islamique (Coran, Sunna). Partisans de la planéité.

 - **Ahl al-Hayʾa** — Les astronomes/philosophes. Partisans de la sphéricité (influence grecque).

 - **Mufassir (pl. mufassirūn)** — Exégète du Coran.

 - **Ṣaḥāba** — Compagnons du Prophète ﷺ.

 - **Tābiʿūn** — Successeurs — ceux qui ont rencontré les Compagnons.

 - **Concordisme** — Tentative de faire coïncider le texte coranique avec les théories scientifiques modernes.

 - **Ijmāʿ** — Consensus des savants. Ses critères : imams identifiés, chaîne documentée, absence de divergence. Voir [B5](/le-consensus-sur-la-sphericite/).

 - **Dhū al-Qarnayn** — Roi coranique (al-Kahf 83-98) ayant voyagé aux extrémités de la Terre. Voir [B4](/dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne/).

 - **ʿAyn ḥamiʾah** — Source boueuse dans laquelle le Soleil se couche selon le verset 18:86 et le hadith d'Abū Dharr.

 - **Yaʾjūj wa Maʾjūj** — Gog et Magog. Peuples retenus derrière une barrière de fer construite par Dhū al-Qarnayn.


## Termes scientifiques


 - **MGPP** — Modèle Géocentrique à Plans Parallèles. Cadre cosmologique alternatif proposé dans [L1](/le-modele-geocentrique-a-plans-paralleles/).

 - **Λ-CDM** — Lambda Cold Dark Matter. Le modèle cosmologique standard (Big Bang + matière noire + énergie noire). 95% de son contenu n'a jamais été observé.

 - **BEC** — Condensat de Bose-Einstein. État de la matière à très basse température où tous les atomes se comportent comme un seul. Dans le MGPP, le superfluide inter-plans. Voir [L1](/le-modele-geocentrique-a-plans-paralleles/).

 - **EM (Électromagnétisme)** — Branche de la physique décrivant les interactions entre charges électriques et champs magnétiques. La lumière, les ondes radio, le magnétisme, la foudre sont tous des phénomènes EM. Dans le MGPP, la gravité est un effet EM émergent.

 - **Réfraction atmosphérique** — Déviation de la lumière due aux variations de densité de l'air. Augmente la portée visuelle de 7 à 14%. Voir [O4](/lhorizon-la-perspective-et-la-refraction-ce-que-loptique-explique-vraiment/).

 - **Diffusion de Rayleigh** — Diffusion préférentielle des courtes longueurs d'onde (bleu) par les molécules d'air. Explique le ciel bleu et le Soleil rouge au coucher.

 - **Force de Coriolis** — Déviation prédite par le modèle d'une Terre en rotation. Absence documentée sur les Grands Lacs. Voir [O1](/leau-ne-ment-pas/).

 - **Parallaxe stellaire** — Décalage angulaire apparent d'une étoile. Mesure de distance qui postule le mouvement orbital de la Terre — le même mouvement que 200 ans d'expériences n'ont pas détecté (voir [N7](/200-ans-de-resultats-nuls-darago-a-einstein/)).

 - **Redshift (décalage vers le rouge)** — Allongement de la longueur d'onde de la lumière. Interprété comme vitesse de récession dans le modèle standard. Halton Arp a montré que des objets physiquement liés ont des redshifts discordants. Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **Tired Light (fatigue lumineuse)** — Hypothèse : le redshift résulte de la perte d'énergie des photons avec la distance, pas de l'expansion de l'univers.

 - **Constante G** — Constante gravitationnelle de Newton. La moins précise de toutes les constantes fondamentales (~5 chiffres). Mesures incompatibles à 5σ entre laboratoires. Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **5σ (cinq sigma)** — Seuil statistique correspondant à une probabilité de 1 sur 3,5 millions que l'écart soit dû au hasard. En physique, c'est le seuil de « découverte ». Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **GM (produit gravitationnel)** — Produit de G et de la masse M. En réalité, GM = 4π² × a³/T² (ratio de Kepler × constante géométrique). La « masse » en kg n'apparaît qu'en divisant par G. Voir [N6](/lhypothese-nulle-la-dynamique-najoute-rien-a-la-cinematique/).

 - **Cinématique** — Description du mouvement par positions, vitesses et accélérations. Dit *comment* les choses bougent, pas *pourquoi*.

 - **Dynamique** — Description du mouvement avec ajout de masse et force. Prétend dire *pourquoi* les choses bougent. L'article [N6](/lhypothese-nulle-la-dynamique-najoute-rien-a-la-cinematique/) montre que dynamique = cinématique × 1.

 - **Problème des trois corps** — Le fait mathématiquement prouvé (Bruns 1887, Poincaré 1890) que le mouvement de 3 corps ou plus sous gravité mutuelle n'a pas de solution analytique générale. Voir [N6](/lhypothese-nulle-la-dynamique-najoute-rien-a-la-cinematique/).

 - **Hypothèse nulle (H₀)** — En méthode scientifique, l'hypothèse par défaut (« il n'y a pas d'effet »). On tente de la falsifier. Si on échoue, elle reste en vigueur. Cadre utilisé par SpaceAudits.

 - **Pseudotenseur** — Objet mathématique qui ressemble à un tenseur mais ne se transforme pas correctement sous changement de coordonnées. Le pseudotenseur d'Einstein est utilisé pour calculer l'énergie gravitationnelle — mais Levi-Civita (1917) a prouvé qu'il est inadmissible. Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **Spallation** — Réaction nucléaire où un proton de haute énergie fragmente un noyau atomique, produisant une pluie de particules secondaires. Plus le blindage est épais, plus la pluie est intense (inversion d'effet). Voir [O7](/lespace-une-frontiere-infranchissable/).

 - **Ceintures de Van Allen** — Deux zones de particules chargées piégées par le champ magnétique terrestre (1 000–60 000 km). Protons à plusieurs centaines de MeV. Voir [O7](/lespace-une-frontiere-infranchissable/).

 - **Thermosphère** — Couche atmosphérique entre 100 et 700 km. Température cinétique jusqu'à 2 500°C. Oxygène atomique corrosif. Voir [O7](/lespace-une-frontiere-infranchissable/).

 - **Soudage à froid** — Fusion spontanée de deux surfaces métalliques propres en contact dans l'ultra-haut vide. Documenté par Rabinowicz (1965) et incidents en vol (Galileo 1991). Voir [O7](/lespace-une-frontiere-infranchissable/).

 - **Aberration stellaire** — Décalage apparent de 20,5″ d'arc des étoiles au cours de l'année, interprété comme v/c = 30 km/s / 300 000 km/s. Seule mesure de premier ordre jamais obtenue. Voir [N7](/200-ans-de-resultats-nuls-darago-a-einstein/).

 - **Éther (luminifère)** — Milieu hypothétique à travers lequel la lumière se propage. Toutes les expériences pour le détecter ont échoué — ce qui a conduit soit à la relativité (la question est supprimée) soit à un éther en mouvement avec la Terre (la Terre est immobile).

 - **Entraînement de Fresnel** — Hypothèse (1818) selon laquelle un milieu transparent en mouvement entraîne partiellement la lumière. Coefficient : 1 − 1/n². Calibré pour annuler l'effet du mouvement terrestre.

 - **Transformation de Lorentz** — Équations mathématiques reliant les coordonnées entre deux référentiels en mouvement relatif. Identiques chez Lorentz (1895) et Einstein (1905) — seule l'interprétation diffère.

 - **Théodolite céleste** — Méthode de mesure utilisant les occultations stellaires derrière des pics montagneux pour tester la géométrie terrestre. 11 320 points de données. Voir [O8](/le-theodolite-celeste/).

 - **Sphère céleste** — Modèle géométrique de Ptolémée dans lequel les étoiles sont projetées sur une sphère imaginaire centrée sur l'observateur. Toujours utilisé en navigation céleste.

 - **Van der Waals (forces de)** — Attraction faible entre molécules, due à des fluctuations de charges. Dans le MGPP, les forces de Van der Waals émergentes sont le mécanisme de la « gravité ». Voir [L1](/le-modele-geocentrique-a-plans-paralleles/).

 - **Force de Densité** — Formule F_ρ = V_o × g × (ρ_m − ρ_o). Si l'objet est plus dense que le milieu → il descend. Moins dense → il monte. Alternative à la gravité newtonienne. Voir [L1](/le-modele-geocentrique-a-plans-paralleles/).

 - **Halo solaire** — Anneau lumineux à 22° autour du Soleil, produit par des cristaux de glace hexagonaux dans les cirrus.

 - **Rayons crépusculaires** — Faisceaux lumineux semblant converger vers un point proche du Soleil. Voir [O6](/pression-lumiere-halos-rayons-et-ondes/).

 - **Fata Morgana** — Mirage supérieur (image déformée, flottante, instable). Ne crée pas de source lumineuse — ne peut expliquer les visibilités à longue distance.

 - **Fisheye** — Objectif grand-angle (170°) produisant une distorsion de courbure artificielle.

 - **Ionosphère** — Couche atmosphérique ionisée (60–1 000 km) qui réfléchit les ondes radio. Communications mondiales depuis 1901 sans satellite. Voir [O6](/pression-lumiere-halos-rayons-et-ondes/).

 - **Voûte céleste apparente** — Le ciel perçu comme un dôme aplati, pas une hémisphère. 30+ études (1738–2021). Rayon apparent ≈ 6 375 km. Voir [O3](/la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre/).

 - **Effet Novaya Zemlya** — Apparition du Soleil 2 semaines avant la date prédite aux hautes latitudes. Réfraction de 4°44′ documentée par Nansen (1894). Voir [O3](/la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre/).

 - **Selenelion** — Éclipse lunaire avec Soleil et Lune visibles simultanément au-dessus de l'horizon. Contradiction géométrique avec l'alignement à 180°. Voir [O3](/la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre/).

 - **Ligne de changement de date (LID)** — Ligne internationale séparant deux jours consécutifs. Devrait suivre le méridien 180° mais zigzague dans le Pacifique. Voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/).

 - **Curve-fitting (ajustement de courbe)** — Technique d'ajustement de paramètres pour qu'un modèle colle aux données. Circulaire quand les paramètres sont extraits des observations qu'ils sont censés expliquer (ex : comètes A1-A3). Voir [N8](/neptune-et-pluton-les-faux-triomphes/).

 - **OBT (Orbite Basse Terrestre)** — Zone entre 200 et 2 000 km d'altitude. Depuis 1972 (Apollo 17), aucun humain n'a dépassé l'OBT. Voir [O7](/lespace-une-frontiere-infranchissable/).

 - **LIGO** — Laser Interferometer Gravitational-Wave Observatory. Détection contestée d'ondes gravitationnelles en 2016. Problèmes : injections fantômes, corrélation instrumentale (Creswell 2017), pseudotenseur inadmissible. Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **Formule de courbure** — h = d²/2R. Hauteur cachée par la courbure terrestre à une distance d, pour un rayon R = 6 371 km. À 10 km → 7,85 m. À 100 km → 785 m. Voir [O1](/leau-ne-ment-pas/).


## Termes géographiques et historiques


 - **Éclipse selenelion** — Voir « Selenelion » ci-dessus.

 - **Traité de l'Antarctique (1959)** — Accord international gelant toutes les revendications territoriales sur l'Antarctique.

 - **Neuschwabenland** — Expédition nazie en Antarctique (1938–1939). 350 000 km² cartographiés par la Luftwaffe. Voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/).

 - **Terre Marie Byrd** — Plus grande zone non revendiquée (~1,6 M km²). Voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/).

 - **LORAN** — Long Range Navigation. Navigation terrestre par triangulation radio (1942–2010).

 - **Projection azimutale** — Projection cartographique centrée sur un point, distances exactes depuis le centre. Utilisée par l'ONU.

 - **Projection Mercator** — Projection cylindrique qui déforme les surfaces (Groenland semble aussi grand que l'Afrique). Voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/).

 - **Opération Highjump (1946–1947)** — Expédition militaire américaine en Antarctique dirigée par Byrd. 4 700 hommes, 13 navires. Terminée prématurément. Voir [O5](/cartes-routes-boussoles-et-le-mystere-antarctique/).

 - **Bedford Level (1838)** — Première expérience documentée de mesure de courbure sur 9,66 km. Canal rectiligne, Cambridgeshire. Résultat : pas de courbure mesurée. Voir [O1](/leau-ne-ment-pas/).

 - **Record Guinness 493 km (2024)** — Plus longue ligne de vue photographiée sur Terre. Richard Jezik, Turquie → Géorgie. Courbure théorique : 19 100 m. Voir [O2](/ce-quon-voit-quand-on-ne-devrait-plus-voir/).

 - **Expérience de Cavendish (1798)** — Balance de torsion mesurant l'attraction entre des sphères de plomb. Base de la valeur de G. Cinq failles méthodologiques documentées. Voir [N4](/la-gravite-70-theories-et-aucune-certitude/).

 - **Michelson-Morley (1887)** — Expérience d'interférométrie cherchant le « vent d'éther ». Résultat nul (≤ 1/6 de la vitesse orbitale). Voir [N7](/200-ans-de-resultats-nuls-darago-a-einstein/).

 - **Expérience d'Airy (1871)** — Télescope zénithal rempli d'eau. L'aberration dans l'eau = aberration dans l'air. Résultat nul le plus embarrassant de l'histoire de la physique. Voir [N7](/200-ans-de-resultats-nuls-darago-a-einstein/).

 - **Gài Tiān (蓋天)** — Modèle cosmologique chinois : Terre plane carrée + ciel plat parallèle. Calculs de gnomons identiques à Ératosthène mais concluant un Soleil local à ~40 000 km. Voir [N2](/dune-terre-plate-universelle-a-la-sphere-grecque/).


					

.nx-footer{background:#2C1810;border-top:1px solid #DDD5C5;padding:4rem 2rem 2rem;font-family:'Outfit',sans-serif}
.nx-footer__inner{max-width:1100px;margin:0 auto}
.nx-footer__grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem;margin-bottom:3rem}
.nx-footer__brand-name{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.2rem;font-weight:700;color:#B8860B;margin:0 0 1rem}
.nx-footer__brand-desc{font-family:'Cormorant Garamond',Georgia,serif;font-size:.88rem;line-height:1.65;color:#8A7A6A;margin:0 0 1.5rem}
.nx-footer__brand-verse{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:.82rem;line-height:1.6;color:rgba(212,175,55,.4)}
.nx-footer__col-title{font-size:.65rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:#5C4A3A;margin:0 0 1.2rem}
.nx-footer__links{list-style:none;padding:0;margin:0}
.nx-footer__links li{margin-bottom:.7rem}
.nx-footer__links a{font-size:.82rem;color:#8A7A6A;text-decoration:none;transition:color .3s ease}
.nx-footer__links a:hover{color:#2C1810}
.nx-footer__sep{height:1px;background:#DDD5C5;margin-bottom:1.5rem}
.nx-footer__bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.nx-footer__copy{font-size:.72rem;color:#8A7A6A}
.nx-footer__socials{display:flex;gap:.8rem;align-items:center}
.nx-footer__socials a{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;background:#EDE5D5;border:1px solid #DDD5C5;color:#8A7A6A;font-size:.75rem;text-decoration:none;transition:all .3s ease}
.nx-footer__socials a:hover{border-color:rgba(212,175,55,.3);color:#B8860B;transform:translateY(-2px)}
@media(max-width:768px){.nx-footer__grid{grid-template-columns:1fr;gap:2rem}.nx-footer{padding:3rem 1.5rem 1.5rem}.nx-footer__bottom{flex-direction:column;align-items:flex-start}}


 
 
## Terre Étendue Islam

 
 Un examen rigoureux des paradigmes cosmologiques, 
 croisant sources sacrées et observations empiriques.
 


 
 « Et la terre, comment elle a été étendue ? »

 — Al-Ghashiyah, 88:20
 


 
 
### Explorer

 

 - [Le Nexus](/le-nexus/)

 - [L'Observatoire](/lobservatoire/)

 - [La Bibliothèque](/la-bibliotheque/)

 - [Le Lab](/le-lab/)

 

 
 
### Ressources

 

 - [Glossaire](/glossaire/)

 - [Index thématique](/index-thematique/)

 - [Méthodologie](/methodologie/)

 

 
 
### À propos

 

 - [Manifeste](/manifeste/)

 - [Éthique intellectuelle](/ethique-intellectuelle/)

 - [Contact](/contact-2/)

 

 © 2026 Terre Étendue Islam — Tous droits réservés · [Mentions légales](/mentions-legales-2/)


 [▶](https://www.youtube.com/@TERREETENDUE)
 [◉](https://odysee.com/@terreetendue)
 [✈](https://t.me/LATERREETENDUE)
 [♪](https://tiktok.com/@terreetendue1)