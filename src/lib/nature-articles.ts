// ═══════════════════════════════════════════════════════════════════════════
// NATURE DES ARTICLES — le régime de preuve, article par article
// ═══════════════════════════════════════════════════════════════════════════
//
// Pourquoi ce fichier existe
// ──────────────────────────
// Le site mélange quatre genres sous une seule mise en page : un protocole
// préenregistré, un dossier d'analyse, une explication de physique et une
// étude de sources textuelles s'y présentent avec la même typographie. Un
// lecteur qui ouvre deux articles au hasard ne peut pas savoir lequel repose
// sur une mesure que nous avons faite et lequel repose sur un livre de 1922.
//
// L'encadré « Ce que cet article est » corrige cela. Il dit trois choses,
// avant le corps du texte : le genre, ce sur quoi l'article repose, et ce
// qu'il n'établit pas.
//
// La troisième ligne est la plus importante et la plus inconfortable. Elle
// nous engage à écrire noir sur blanc, en tête de chaque page, la limite de
// ce que nous avançons — y compris quand la conclusion nous plairait.
//
// Un registre plutôt qu'un champ JSON
// ───────────────────────────────────
// Les articles sont des JSON, et le champ aurait pu y vivre. Nous l'avons mis
// ici pour une raison de fond : ces soixante notices doivent se lire les unes
// à côté des autres. C'est côte à côte qu'on voit si l'on est aussi sévère
// avec un article qui nous arrange qu'avec un autre. Éparpillées dans
// soixante fichiers, elles auraient dérivé en une saison.
//
// Même choix, même motif que src/lib/article-images.ts.
//
// Tenir ce fichier à jour
// ───────────────────────
// Tout nouvel article y entre. `verifier-integrite-articles.py` signale les
// manquants. Un article sans notice ne fait pas échouer le rendu : l'encadré
// est simplement absent, et c'est visible.

export type Genre = 'protocole' | 'analyse' | 'explication' | 'textes' | 'outil';

export interface Nature {
  genre: Genre;
  /** Sur quoi l'article repose. Nommer la source, et dire si elle est de nous. */
  repose: string;
  /** Ce que l'article n'établit pas. Toujours renseigné, jamais une formule creuse. */
  netablit: string;
}

export const GENRE_LABEL: Record<Genre, string> = {
  protocole: 'Protocole préenregistré',
  analyse: "Dossier d'analyse",
  explication: 'Explication',
  textes: 'Étude de sources textuelles',
  outil: 'Page de service',
};

export const GENRE_COULEUR: Record<Genre, string> = {
  protocole: 'var(--rose)',
  analyse: 'var(--lavender)',
  explication: 'var(--opal)',
  textes: 'var(--saffron)',
  outil: 'var(--ink-muted)',
};

/** Ce que chaque genre engage. Affiché en infobulle sur le libellé. */
export const GENRE_DEFINITION: Record<Genre, string> = {
  protocole:
    "Énonce ses prédictions et ses critères de décision avant toute acquisition, avec un budget d'erreur chiffré, et les dépose publiquement.",
  analyse:
    "Examine une affirmation courante et les preuves qu'on avance à son appui. Ne produit pas de mesure nouvelle.",
  explication:
    "Expose un phénomène établi et reproductible. Ne défend aucune thèse sur la forme de la Terre.",
  textes:
    "Travaille sur des sources écrites — Coran, hadith, manuscrits, éditions imprimées — et sur ce qu'elles disent réellement.",
  outil: "Page de navigation ou de service. Ne contient pas d'argument.",
};

const N: Record<string, Nature> = {
  // ══ CENTRE DE RECHERCHE ═══════════════════════════════════════════════════
  'lenigme-de-la-terre-immobile': {
    genre: 'analyse',
    repose:
      "Les publications d'Arago, Fresnel, Fizeau, Airy et Michelson-Morley, lues dans des éditions modernes. Nous n'avons ni les cahiers de laboratoire ni les données brutes d'aucune de ces expériences.",
    netablit:
      "N'établit pas que la Terre est immobile. Retrace une suite de résultats nuls et les hypothèses successivement introduites pour les concilier avec le mouvement.",
  },
  'chronologie-critique-du-modele-globe': {
    genre: 'analyse',
    repose:
      "Des textes d'époque et des travaux d'historiens des sciences, cités d'après des éditions modernes.",
    netablit:
      "N'établit aucune forme de la Terre. Retrace comment le modèle s'est construit et ce que chaque étape supposait déjà acquis.",
  },
  'dune-terre-plate-universelle-a-la-sphere-grecque': {
    genre: 'analyse',
    repose:
      "Des sources antiques et des travaux d'historiens des sciences. Aucune mesure.",
    netablit:
      "N'établit pas laquelle des deux cosmologies est vraie. C'est une histoire des idées, pas un argument physique.",
  },
  'la-cosmologie-comme-instrument-de-domination': {
    genre: 'analyse',
    repose:
      "Des citations d'auteurs et de scientifiques sur le sens qu'ils donnent eux-mêmes au décentrement.",
    netablit:
      "N'établit rien sur la forme de la Terre ni sur l'astronomie. Porte sur les usages idéologiques d'un modèle, ce qui est une autre question que sa validité.",
  },
  'la-gravite-70-theories-et-aucune-preuve': {
    genre: 'analyse',
    repose:
      "La littérature de physique publiée, les valeurs officielles des constantes (CODATA), et les théorèmes de Bruns (1887) et Poincaré (1890) sur le problème des trois corps. Les développements algébriques sont refaits par nous et vérifiables ligne à ligne. La décomposition des forces en repère géocentrique vient de Bouw 2013, classée D dans notre grille, et rapportée comme telle.",
    netablit:
      "N'établit pas que la gravité n'existe pas, ni que la Terre est immobile. Montre qu'aucune théorie unique n'en rend compte, que G reste la constante fondamentale la moins bien mesurée, et que la masse s'annule dans les équations orbitales — ce qui borne ce qu'elles mesurent, sans dire ce qui les cause.",
  },
  'la-rotation-terrestre-experiences-preuves-verdict': {
    genre: 'analyse',
    repose:
      "Les publications originales de Foucault, Sagnac, Hafele-Keating, Eötvös et Thirring. Aucune n'a été reproduite par nous.",
    netablit:
      "N'établit pas que la Terre ne tourne pas. Examine, expérience par expérience, si chacune démontre bien ce qu'on lui fait dire.",
  },
  'le-concordisme': {
    genre: 'textes',
    repose:
      "Le Coran, les exégèses classiques et la lexicographie arabe — sources primaires, référencées et vérifiables.",
    netablit:
      "N'établit pas la forme de la Terre. Porte sur ce qu'un mot arabe signifie, et sur l'écart entre ce sens et ce qu'on lui fait dire aujourd'hui.",
  },
  'lexperience-contre-la-theorie': {
    genre: 'analyse',
    repose:
      "Les publications zététiques du XIXᵉ siècle, prises comme documents d'histoire. Nous n'avons vérifié aucune des mesures qu'elles rapportent.",
    netablit:
      "N'établit aucun résultat physique. Recense un corpus, ses auteurs et son histoire. Citer un texte n'est pas le valider.",
  },
  'le-mythe-deratosthene': {
    genre: 'analyse',
    repose:
      "Des travaux d'historiens des sciences (Pinotsis 2006, Rawlins 2008) et des sources antiques fragmentaires et tardives.",
    netablit:
      "N'établit pas que la mesure d'Ératosthène était fausse. Montre que le récit scolaire ne correspond pas à ce que disent les sources.",
  },
  'les-distances-cosmiques-au-dela-de-la-regle': {
    genre: 'analyse',
    repose:
      "La littérature astronomique publiée — Bessel, Gill, Freedman, Gaia — et l'ouvrage de Gerrard Hickson (1922), dont nous n'avons refait aucun calcul. Aucune observation n'est la nôtre.",
    netablit:
      "N'établit aucune distance de remplacement, et ne reprend pas à son compte les objections qu'il rapporte — celle d'Hickson sur les horizons de Halley est même signalée comme géométriquement fausse. Montre à partir de quel maillon la chaîne de mesure cesse d'être directe.",
  },
  'les-trous-noirs-existent-ils': {
    genre: 'analyse',
    repose:
      "La littérature de relativité générale, des alternatives publiées et évaluées par les pairs, et les objections méthodologiques portées aux données de LIGO — dont celle de Creswell et collaborateurs. Aucune observation de ce dossier n'est la nôtre, et aucune ne pourrait l'être : nous n'avons pas accès aux données de LIGO ni à celles de l'Event Horizon Telescope.",
    netablit:
      "Ne tranche pas l'existence des trous noirs, ni celle des ondes gravitationnelles. Recense ce que le modèle suppose, ce que les images montrent réellement, et quelles objections publiées restent sans réponse.",
  },
  'ligo-londe-qui-nexistait-pas': {
    genre: 'analyse',
    repose:
      "Des objections méthodologiques publiées, dont l'analyse de Creswell et collaborateurs. Nous n'avons pas accès aux données de LIGO et ne les avons pas traitées.",
    netablit:
      "N'établit pas que les ondes gravitationnelles n'existent pas, ni que la détection de 2015 est fausse. Recense des objections publiées et l'état de leur réponse.",
  },
  'lire-le-ciel-avant-le-globe': {
    genre: 'analyse',
    repose:
      "L'histoire des instruments — gnomon, degré, mesure d'ombre — et des sources antiques.",
    netablit:
      "N'établit aucune cosmologie. Montre que les instruments et les angles précèdent de loin le modèle auquel on les attribue.",
  },
  'neptune-et-pluton-les-faux-triomphes': {
    genre: 'analyse',
    repose:
      "Les éléments orbitaux publiés et les récits historiques des deux découvertes.",
    netablit:
      "N'établit pas que la mécanique céleste est fausse. Compare les prédictions annoncées aux positions réellement trouvées.",
  },
  'par-rapport-a-quoi-mesure-t-on-une-altitude': {
    genre: 'explication',
    repose:
      "Des manuels de géodésie et de topographie. Les calculs présentés sont refaits par nous et reproductibles.",
    netablit:
      "Ne tranche aucun modèle. Explique ce qu'une altitude mesure, et par rapport à quelle surface de référence — question préalable à toute mesure de terrain.",
  },
  'pourquoi-tout-remettre-en-question': {
    genre: 'analyse',
    repose:
      "Des textes d'épistémologie et des déclarations de physiciens sur les limites de leur propre discipline.",
    netablit:
      "N'établit aucun fait sur le monde. C'est un texte de méthode : il dit à quelles conditions une affirmation compte comme prouvée.",
  },

  // ══ OBSERVATOIRE ══════════════════════════════════════════════════════════
  'cartes-routes-boussoles-et-le-mystere-antarctique': {
    genre: 'analyse',
    repose:
      "Des cartes publiées, des horaires de vols commerciaux et le texte du Traité sur l'Antarctique. Aucun de ces trajets n'a été parcouru ni chronométré par nous.",
    netablit:
      "N'établit pas la projection réelle de la Terre. Recense des faits cartographiques et des trajets, et ce que chaque modèle en prédit.",
  },
  'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre': {
    genre: 'analyse',
    repose:
      "Des observations rapportées par des tiers et la littérature publiée. Aucune n'a été refaite par nous, et aucune n'est accompagnée de son budget d'erreur.",
    netablit:
      "N'établit ni la nature ni la distance d'aucun astre. Rassemble des observations et signale celles que le modèle standard explique mal.",
  },
  'la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas': {
    genre: 'analyse',
    repose:
      "Des observations rapportées par des tiers et la littérature publiée. Nous n'avons refait aucune de ces six observations.",
    netablit:
      "N'établit pas la nature de la Lune, ni ne propose de modèle de remplacement. Recense six observations que le modèle standard explique mal ou pas.",
  },
  'la-perspective-pourquoi-les-objets-disparaissent': {
    genre: 'analyse',
    repose:
      "L'optique classique, deux constructions que le lecteur peut refaire lui-même — une perspective sur une feuille A3, trois plans photographiés — et des tests au zoom. Les photographies et vidéos citées, elles, ne sont pas les nôtres et n'ont pas de conditions de prise de vue documentées.",
    netablit:
      "N'établit pas que l'horizon est plat. Montre que la disparition d'un objet lointain a plusieurs causes possibles et comment on peut les distinguer.",
  },
  'le-pole-sud-nexiste-pas': {
    genre: 'analyse',
    repose:
      "Les définitions officielles des quatre pôles Sud et le texte du Traité sur l'Antarctique.",
    netablit:
      "N'établit pas qu'il n'existe pas de région polaire australe — le titre est plus tranchant que le contenu. Porte sur le fait que « pôle Sud » désigne quatre points distincts, et sur ce que le régime du Traité autorise.",
  },
  'mesures-sous-le-ciel-trigonometrie-plane': {
    genre: 'analyse',
    repose:
      "Un jeu de 11 320 points de données produit par un tiers, à partir d'occultations stellaires et d'éclipses. Nous n'avons ni les mesures brutes, ni le budget d'erreur, ni le détail de la réduction.",
    netablit:
      "N'établit pas que la trigonométrie plane suffit. Présente un résultat annoncé par un tiers, que nous ne sommes pas en mesure de vérifier.",
  },
  'les-marees-contre-lheliocentrisme': {
    genre: 'analyse',
    repose:
      "Les tables de marée officielles et l'analyse harmonique, qui est la méthode réellement employée pour les prédire.",
    netablit:
      "N'établit pas la cause des marées. Montre que la prédiction opérationnelle est harmonique et non gravitationnelle, ce qui n'est pas la même chose que réfuter la gravitation.",
  },
  'lespace-une-frontiere-infranchissable': {
    genre: 'analyse',
    repose:
      "Des publications de la NASA, de l'ESA et de laboratoires universitaires sur la thermosphère, le soudage à froid et les ceintures de Van Allen.",
    netablit:
      "N'établit pas que le vol spatial habité est impossible. Recense trois contraintes physiques documentées et l'état des réponses publiées.",
  },
  'mesurer-la-courbure-sur-l-eau-cinq-campagnes': {
    genre: 'analyse',
    repose:
      "Les comptes rendus publiés de cinq campagnes — Wallace, Rainy Lake, FECORE, Pontchartrain. Nous n'avons vu les données brutes d'aucune d'entre elles, et nous ne nous en réclamons pas.",
    netablit:
      "N'établit aucun résultat sur la courbure. Montre ce que chaque campagne a mesuré, ce qui lui manquait, et pourquoi la mesure de la loi reste à faire.",
  },
  'vols-avion-et-courbure-terrestre': {
    genre: 'analyse',
    repose:
      "Des manuels de construction aéronautique, des documents déclassifiés et les définitions officielles des instruments de bord. Aucun vol n'a été instrumenté par nous.",
    netablit:
      "N'établit pas que la trajectoire d'un avion est rectiligne. Montre ce que chaque instrument mesure réellement, et ce qu'il ne mesure pas.",
  },

  // ══ BIBLIOTHÈQUE ══════════════════════════════════════════════════════════
  'debut-de-la-creation-le-soleil-mobile-la-terre-immobile': {
    genre: 'textes',
    repose:
      "Le Coran et des hadiths référencés par recueil, numéro et grade.",
    netablit:
      "N'établit pas un fait physique. Établit ce que les textes disent, ce qui est une question distincte de ce qui est vrai du monde.",
  },
  'debut-de-la-creation-selon-le-coran-et-la-sunna': {
    genre: 'textes',
    repose:
      "Le Coran et la Sunna, suivant une série d'exposés dont chaque bloc est référencé.",
    netablit:
      "N'établit pas un fait physique. Restitue un récit de la création tel que les sources le portent.",
  },
  'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne': {
    genre: 'textes',
    repose:
      "Le verset 18:86, des témoignages de Compagnons et six exégètes classiques, cités et référencés.",
    netablit:
      "N'établit pas la géographie réelle du monde. Établit comment les exégètes ont lu ce verset, et à quel moment cette lecture a changé.",
  },
  'la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah': {
    genre: 'textes',
    repose:
      "Une édition imprimée confrontée à trois témoins manuscrits antérieurs. C'est de la critique textuelle, et elle est vérifiable par quiconque consulte les mêmes témoins.",
    netablit:
      "N'établit pas la forme de la Terre. Établit qu'un mot de l'édition imprimée ne figure pas dans les témoins antérieurs.",
  },
  'la-qibla-et-la-direction-cote-ouest': {
    genre: 'analyse',
    repose:
      "La géométrie des projections cartographiques et le calcul de la direction de qibla.",
    netablit:
      "N'établit pas la projection réelle de la Terre. Montre que la direction indiquée dépend de la projection choisie, ce qui est vrai de toute carte.",
  },
  'la-terre-dans-le-coran': {
    genre: 'textes',
    repose:
      "Le texte coranique, le relevé de ses occurrences, et les exégèses classiques citées en arabe et en traduction.",
    netablit:
      "N'établit pas un fait physique. Établit ce que le texte dit et ce que les exégètes ont compris, avant toute question de vérification.",
  },
  'le-consensus-sur-la-sphericite': {
    genre: 'textes',
    repose:
      "Une citation contestée, examinée sur six axes : philologie, filiation, chronologie et contradictions internes. Sources primaires référencées.",
    netablit:
      "N'établit pas la forme de la Terre. Examine si le consensus invoqué remplit les conditions d'un ijmāʿ.",
  },
  'levolution-et-lislam': {
    genre: 'textes',
    repose:
      "Le récit coranique de la création et les positions de savants de l'islam sur la question.",
    netablit:
      "N'établit rien en biologie. Expose une position théologique et la distinction que les sources font entre deux échelles de variation.",
  },
  'mise-en-garde-la-kaaba-et-saturne': {
    genre: 'textes',
    repose:
      "Les allégations circulant sur ce rapprochement, leurs sources, et la position théologique islamique.",
    netablit:
      "N'établit rien en astronomie. C'est une réfutation d'allégations, point par point.",
  },
  'ou-est-allah-le-uluww-et-la-forme-du-monde': {
    genre: 'textes',
    repose:
      "Cinq familles de versets, la Sunna, les Compagnons et les quatre imams — dix-neuf références primaires.",
    netablit:
      "N'établit pas la forme de la Terre. Établit une position doctrinale et montre en quoi elle est liée à la question, sans s'y substituer.",
  },
  'pres-de-cent-savants-de-lislam': {
    genre: 'textes',
    repose:
      "Un relevé nominatif d'autorités, du Compagnon au contemporain, chacune avec sa référence.",
    netablit:
      "N'établit pas un fait physique, et le nombre ne fait pas la preuve. Établit qu'une position existait et chez qui.",
  },
  'sources-historiques-fonds-documentaire': {
    genre: 'outil',
    repose:
      "Un inventaire de publications de 1865 à 1920. Nous n'avons vérifié aucune des mesures que ces ouvrages rapportent.",
    netablit:
      "N'établit rien du tout, et ne valide aucun des textes recensés. C'est un catalogue, pas une caution.",
  },
  'un-traite-ottoman-contre-la-sphericite-1314h': {
    genre: 'textes',
    repose:
      "Un manuscrit daté et localisé, dont les calculs sont repris poste par poste — y compris ceux qui ne tombent pas juste.",
    netablit:
      "N'établit pas la forme de la Terre, et ne prend pas les arguments du traité à son compte. Quatre valeurs incompatibles pour le degré de latitude y sont relevées et signalées.",
  },

  // ══ EXPÉRIENCES ═══════════════════════════════════════════════════════════
  'densite-pourquoi-les-choses-montent-et-descendent': {
    genre: 'explication',
    repose:
      "Le principe d'Archimède et trois expériences réalisables en cuisine avec du matériel courant.",
    netablit:
      "Ne tranche pas entre densité et gravitation comme cause. Montre ce que la densité suffit à expliquer, et où la question reste ouverte.",
  },
  'la-pression-atmospherique-un-ocean-d-air-invisible': {
    genre: 'explication',
    repose:
      "La théorie cinétique des gaz et quatre tests, dont les hémisphères de Magdebourg avec leurs valeurs chiffrées.",
    netablit:
      "N'établit pas que la gravité est inutile pour retenir l'atmosphère — la question de ce qui borne la colonne d'air reste entière. Montre ce que la pression fait, et combien elle vaut.",
  },
  'leau-ne-ment-pas': {
    genre: 'analyse',
    repose:
      "La formule de courbure du modèle sphérique, et des observations rapportées par des tiers — Bedford, Grands Lacs, essais laser. Nous n'avons vu les données brutes d'aucune, et aucune n'était préenregistrée.",
    netablit:
      "N'établit pas que les grandes étendues d'eau sont planes. La mesure qui trancherait est décrite ailleurs sur ce site, et elle reste à faire.",
  },
  'les-forces-invisibles-a-faire-chez-soi': {
    genre: 'explication',
    repose:
      "L'électrostatique, l'électromagnétisme et la troisième loi de Newton, et huit expériences réalisables avec un ballon, un aimant, du fil, une boussole et un skateboard.",
    netablit:
      "Ne tranche aucun modèle cosmologique. Établit qu'une force peut agir sans contact — fait ordinaire, et non argument. C'est une page de socle : ce qu'on y montre sert ailleurs sans être redémontré.",
  },
  'loeil-humain-la-machine-a-voir': {
    genre: 'explication',
    repose:
      "La physiologie de la vision publiée — accommodation, champ, résolution angulaire, tache aveugle.",
    netablit:
      "Ne tranche aucun modèle. Établit les limites de l'instrument avec lequel toute observation à l'œil nu est faite.",
  },
  'monter-l-experience-des-trois-mires': {
    genre: 'protocole',
    repose:
      "Un dispositif à trois perches, un budget d'erreur, des règles de rejet écrites d'avance, et des prédictions figées le 2 août 2026 dans un fichier public daté.",
    netablit:
      "Ne conclut rien à ce jour : aucune campagne n'a encore été menée. N'est pas déposé et ne porte pas de DOI, contrairement au protocole de dépression de l'horizon.",
  },
  'pression-lumiere-halos-rayons-et-ondes': {
    genre: 'explication',
    repose:
      "L'optique atmosphérique et l'acoustique, sur des phénomènes observables sans instrument.",
    netablit:
      "Ne tranche aucun modèle. Rassemble des phénomènes atmosphériques et ce que chacun suppose du milieu.",
  },
  'participer-aux-campagnes-de-mesure': {
    genre: 'outil',
    repose:
      "Les protocoles que nous publions, leur état d'avancement, et le matériel que chacun demande.",
    netablit:
      "Ne rapporte aucun résultat, parce qu'aucune campagne n'a commencé. C'est un appel : elle dit ce qui est prêt à être fait, par qui, et à quelles conditions.",
  },
  'les-protocoles-ce-que-c-est-et-pourquoi': {
    genre: 'outil',
    repose:
      "Les documents que nous publions, et les règles que nous nous sommes données pour les écrire.",
    netablit:
      "N'est pas lui-même un protocole et ne mesure rien. C'est la porte d'entrée de ceux qui mesurent.",
  },

  // ══ MÉTA ══════════════════════════════════════════════════════════════════
  corrections: {
    genre: 'outil',
    repose:
      "Ce que nous tenons pour une erreur, et la procédure par laquelle une erreur signalée est traitée.",
    netablit:
      "N'avance aucune thèse. Ne garantit pas l'absence d'erreur — dit ce qui arrive quand il y en a une.",
  },
  'financement-et-independance': {
    genre: 'outil',
    repose: "Ce que le site s'engage à faire d'un don, et à ne pas en faire.",
    netablit:
      "N'avance aucune thèse et ne demande rien. Un don ne change ni ce qui est mesuré, ni ce qui est conclu.",
  },
  'etat-des-lieux-ou-en-sommes-nous': {
    genre: 'outil',
    repose: "Un bilan interne de ce que le site a publié et de ce qui reste ouvert.",
    netablit: "N'établit rien de neuf. Récapitule, et signale ce qui manque.",
  },
  glossaire: {
    genre: 'outil',
    repose: "Des définitions de termes coraniques, scientifiques et historiques.",
    netablit: "N'avance aucune thèse. Une définition n'est pas un argument.",
  },
  'index-thematique': {
    genre: 'outil',
    repose: "Le classement des articles du site par domaine.",
    netablit: "N'avance aucune thèse. C'est une table des matières.",
  },
  'standards-et-methode': {
    genre: 'outil',
    repose: "Les règles que nous nous imposons, énoncées pour qu'on puisse nous les opposer.",
    netablit:
      "N'établit aucun fait sur le monde. Dit à quelles conditions nous tenons une affirmation pour établie.",
  },
};

export function getNature(slug: string): Nature | null {
  return N[slug] || null;
}

export const NATURES = N;
