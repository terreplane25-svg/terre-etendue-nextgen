// ═══════════════════════════════════════════
// LABORATOIRE D'ANALYSE — Données
// ═══════════════════════════════════════════

export interface AnalyseMedia {
  id: string;
  type: 'video' | 'image';
  category: string;
  title: string;
  location?: string;
  date?: string;
  source?: string;
  duration?: string;
  resolution?: string;
  embedUrl?: string;
  imageUrl?: string;
  observation: string;
  analyse: string;
  demarche: string[];
  checklist: string[];
  svgDiagram?: string;
  relatedArticle?: string;
}

export const CATEGORIES = [
  { id: 'atmospherique', label: 'Atmosphérique', icon: '🌫️', color: '#3B8FD4' },
  { id: 'optique', label: 'Optique & perspective', icon: '🔭', color: '#D4943A' },
  { id: 'mecanique', label: 'Physique mécanique', icon: '⚙️', color: '#8B7EC8' },
  { id: 'astronomique', label: 'Astronomique', icon: '🌙', color: '#C45E6A' },
  { id: 'hydrologique', label: 'Eau & fluides', icon: '🌊', color: '#3D9E7C' },
  { id: 'electromagnetique', label: 'Électromagnétisme', icon: '⚡', color: '#E8A838' },
] as const;

export type CategoryId = typeof CATEGORIES[number]['id'];

export const ANALYSES: AnalyseMedia[] = [
  {
    id: 'mirage-inferieur-route',
    type: 'video',
    category: 'atmospherique',
    title: 'Mirage inférieur sur une route droite',
    location: 'Route désertique, été',
    source: 'Observation amateur vérifiable',
    duration: '~2 min',
    embedUrl: 'https://www.youtube.com/embed/CF-gTmiVEz0',
    observation: `Sur une longue route droite par forte chaleur, la chaussée semble mouillée à quelques centaines de mètres. On aperçoit un « reflet » inversé des véhicules et du ciel sur la route. L'effet disparaît à mesure qu'on s'approche.`,
    analyse: `<p>L'air surchauffé au contact du bitume (60–70 °C) crée une couche d'air <strong>moins dense</strong> juste au-dessus de la route.</p>
<p>L'indice de réfraction de l'air diminue avec la température : <code>n ≈ 1 + 0,000293 × (P/T)</code>. Les rayons lumineux se courbent vers les couches plus denses (<strong>loi de Snell-Descartes</strong> appliquée en gradient continu).</p>
<p>À un angle rasant suffisant, la courbure est telle que la lumière « remonte » vers l'observateur → on voit le ciel projeté sur la route (apparence de flaque d'eau). L'image inversée en dessous de l'objet est caractéristique du <strong>mirage inférieur</strong>.</p>
<p>À distinguer du mirage <em>supérieur</em> (image au-dessus, inversion thermique en altitude) et de la <em>Fata Morgana</em> (couches multiples créant des images empilées et déformées).</p>`,
    demarche: [
      'Identifier le type de mirage : inférieur (sol chaud) vs supérieur (inversion thermique en altitude) vs Fata Morgana (couches multiples)',
      'Documenter les conditions : température au sol, température de l\'air, heure, ensoleillement, nature de la surface',
      'Mesurer si possible : distance d\'observation, angle d\'élévation, hauteur de l\'observateur par rapport au sol',
      'Comparer avec les modèles : le gradient thermique mesuré produit-il la courbure observée ?',
      'Tester la reproductibilité : le même effet se produit-il dans des conditions similaires ?',
    ],
    checklist: [
      'La vidéo montre-t-elle la scène complète (pas de zoom sélectif) ?',
      'Les conditions météo sont-elles documentées (T°, vent, humidité) ?',
      'La distance d\'observation est-elle connue ou estimable ?',
      'La hauteur de la caméra par rapport au sol est-elle précisée ?',
      'Le phénomène disparaît-il à l\'approche (test classique du mirage) ?',
      'A-t-on considéré d\'autres explications (eau réelle, reflet d\'objet) ?',
      'La focale/zoom de la caméra est-elle connue (effet de compression optique) ?',
    ],
    svgDiagram: `<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:700px;border-radius:10px;background:#0d1117">
  <text x="350" y="25" text-anchor="middle" fill="#8B7EC8" font-size="13" font-weight="700" font-family="Plus Jakarta Sans,sans-serif">MIRAGE INFÉRIEUR — COURBURE DES RAYONS LUMINEUX</text>
  <rect x="40" y="200" width="620" height="40" rx="0" fill="#2a3140"/>
  <text x="350" y="225" text-anchor="middle" fill="#607890" font-size="10" font-family="JetBrains Mono,monospace">ROUTE (bitume chaud 60-70°C)</text>
  <text x="60" y="80" fill="#607890" font-size="9" font-family="JetBrains Mono,monospace">AIR FROID (dense)</text>
  <text x="60" y="185" fill="#C45E6A" font-size="9" font-family="JetBrains Mono,monospace">AIR CHAUD (peu dense)</text>
  <line x1="40" y1="95" x2="660" y2="95" stroke="#607890" stroke-width="0.5" stroke-dasharray="4,4"/>
  <line x1="40" y1="140" x2="660" y2="140" stroke="#607890" stroke-width="0.5" stroke-dasharray="4,4"/>
  <line x1="40" y1="175" x2="660" y2="175" stroke="#C45E6A" stroke-width="0.5" stroke-dasharray="4,4"/>
  <text x="670" y="98" fill="#607890" font-size="8" font-family="JetBrains Mono,monospace">n₁</text>
  <text x="670" y="143" fill="#607890" font-size="8" font-family="JetBrains Mono,monospace">n₂</text>
  <text x="670" y="178" fill="#C45E6A" font-size="8" font-family="JetBrains Mono,monospace">n₃</text>
  <circle cx="580" cy="60" r="6" fill="#D4943A"/>
  <text x="580" y="50" text-anchor="middle" fill="#D4943A" font-size="9" font-family="JetBrains Mono,monospace">objet réel</text>
  <path d="M 580,66 Q 400,195 120,150" fill="none" stroke="#D4943A" stroke-width="2"/>
  <path d="M 580,66 L 120,120" fill="none" stroke="#3B8FD4" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="120" cy="150" r="8" fill="none" stroke="#e8edf4" stroke-width="1.5"/>
  <line x1="120" y1="158" x2="120" y2="190" stroke="#e8edf4" stroke-width="1.5"/>
  <text x="120" y="50" text-anchor="middle" fill="#e8edf4" font-size="9" font-family="JetBrains Mono,monospace">observateur</text>
  <text x="350" y="165" text-anchor="middle" fill="#D4943A" font-size="10" font-weight="600" font-family="Plus Jakarta Sans,sans-serif">rayon courbé par le gradient thermique</text>
  <text x="300" y="110" text-anchor="middle" fill="#3B8FD4" font-size="9" font-family="Plus Jakarta Sans,sans-serif">trajet direct (image réelle)</text>
  <line x1="120" y1="155" x2="200" y2="200" stroke="#3D9E7C" stroke-width="1.5" stroke-dasharray="3,3"/>
  <circle cx="210" cy="205" r="4" fill="#3D9E7C" opacity="0.6"/>
  <text x="260" y="250" fill="#3D9E7C" font-size="9" font-family="Plus Jakarta Sans,sans-serif">image inversée (mirage) : le ciel apparaît sur la route</text>
</svg>`,
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
  {
    id: 'mirage-superieur',
    type: 'video',
    category: 'atmospherique',
    title: 'Mirage supérieur — navire qui flotte au-dessus de l\'horizon',
    location: 'Zones côtières froides, mer Baltique, Grand Nord',
    source: 'Observation documentée',
    duration: '~3 min',
    embedUrl: 'https://www.youtube.com/embed/nGBkho1laP4',
    observation: `Un navire (ou une côte, un bâtiment) apparaît surélevé, comme s'il flottait au-dessus de la surface de l'eau. L'image peut être à l'endroit ou inversée, parfois les deux superposés. L'effet est plus fréquent en hiver et dans les régions polaires.`,
    analyse: `<p>Contrairement au mirage inférieur (sol chaud), le mirage supérieur se produit quand une couche d'air <strong>chaud</strong> repose au-dessus d'une couche d'air <strong>froid</strong> — c'est une <strong>inversion thermique</strong>.</p>
<p>L'air froid (plus dense) a un indice de réfraction plus élevé que l'air chaud au-dessus. Les rayons lumineux se courbent <strong>vers le bas</strong>, suivant la courbure de la couche froide. Résultat : l'observateur voit des objets qui sont normalement sous l'horizon optique.</p>
<p>Ce phénomène est bien documenté : il peut faire apparaître des navires, des îles ou des côtes qui sont géométriquement <strong>sous l'horizon</strong>. C'est le même phénomène qui explique pourquoi on peut parfois voir des objets beaucoup plus loin que la distance théorique de l'horizon.</p>
<p><strong>Point clé :</strong> le mirage supérieur est souvent invoqué dans les deux sens du débat — il montre que la réfraction atmosphérique peut « relever » des objets cachés par la distance, ce qui complique tout calcul de courbure basé sur la visibilité.</p>`,
    demarche: [
      `Identifier les conditions thermiques : température de l'eau vs température de l'air (inversion thermique nécessaire)`,
      `Mesurer la distance entre l'observateur et l'objet observé — est-il au-delà de la distance théorique de l'horizon ?`,
      `Documenter si l'image est à l'endroit, inversée, ou les deux (critère de classification du type de mirage)`,
      `Vérifier la stabilité du phénomène : un mirage supérieur peut durer des heures, contrairement au mirage inférieur`,
      `Comparer avec la position réelle connue de l'objet (carte marine, GPS)`,
    ],
    checklist: [
      `Les conditions d'inversion thermique sont-elles documentées ?`,
      `La distance réelle de l'objet est-elle connue ?`,
      `L'image est-elle déformée (étirée verticalement) — signe classique du mirage supérieur ?`,
      `A-t-on exclu un simple effet de perspective (objet réellement visible sans réfraction) ?`,
      `La hauteur de l'observateur par rapport à la surface est-elle précisée ?`,
      `Le phénomène a-t-il été observé à différents moments de la journée (variation thermique) ?`,
    ],
  },
  {
    id: 'fata-morgana',
    type: 'video',
    category: 'atmospherique',
    title: 'Fata Morgana — images empilées et déformées',
    location: 'Détroits, zones polaires, déserts',
    source: 'Observation documentée',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/aK6d0lowbLM',
    observation: `Au-dessus de l'horizon, on observe des structures impossibles : tours, murailles, villes entières qui semblent flotter et se déformer lentement. Les formes changent continuellement — elles s'étirent, se compriment, se dédoublent. Le phénomène peut durer des heures.`,
    analyse: `<p>La Fata Morgana est la forme la plus complexe de mirage. Elle se produit quand <strong>plusieurs couches d'air</strong> à températures différentes s'empilent, créant un gradient de réfraction complexe.</p>
<p>Chaque couche dévie les rayons lumineux différemment, produisant des <strong>images multiples</strong> d'un même objet — certaines à l'endroit, d'autres inversées, à des hauteurs différentes. Le résultat est une image composite déformée qui ressemble à des structures architecturales.</p>
<p>C'est ce phénomène qui a probablement donné naissance aux légendes de villes fantômes et de « Fée Morgane » (d'où le nom). Le détroit de Messine (entre la Sicile et l'Italie) est l'un des lieux les plus célèbres pour l'observer.</p>
<p><strong>Point clé :</strong> la Fata Morgana montre que l'atmosphère peut créer des images extrêmement trompeuses. C'est un rappel que toute observation lointaine doit prendre en compte les conditions atmosphériques avant de tirer des conclusions géométriques.</p>`,
    demarche: [
      `Identifier la structure en couches de l'atmosphère (radiosondage si disponible)`,
      `Observer si les images sont multiples et changeantes (critère distinctif de la Fata Morgana vs mirage simple)`,
      `Documenter la durée et l'évolution du phénomène (les Fata Morgana peuvent durer des heures)`,
      `Tenter d'identifier l'objet réel à l'origine de l'image déformée (navire, côte, iceberg)`,
      `Photographier/filmer à intervalles réguliers pour documenter l'évolution temporelle`,
    ],
    checklist: [
      `Les images sont-elles multiples et superposées (critère clé) ?`,
      `Le phénomène évolue-t-il dans le temps (les vrais objets ne changent pas de forme) ?`,
      `La structure en couches thermiques est-elle documentée ou plausible ?`,
      `A-t-on identifié l'objet source réel ?`,
      `La distance d'observation est-elle connue ?`,
      `A-t-on exclu un montage ou un artefact photographique ?`,
    ],
  },
  {
    id: 'rayons-crepusculaires',
    type: 'video',
    category: 'atmospherique',
    title: 'Rayons crépusculaires — les « doigts de Dieu »',
    location: 'Visible partout, surtout par temps partiellement nuageux',
    source: 'Photographie courante',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/XZ76tNCsTjQ',
    observation: `Des faisceaux de lumière semblent diverger depuis le soleil à travers des trouées dans les nuages. On dirait que les rayons s'écartent en éventail, comme si le soleil était proche et les rayons partaient dans toutes les directions.`,
    analyse: `<p>Les rayons crépusculaires sont des <strong>colonnes de lumière</strong> rendues visibles par la diffusion de la lumière sur les particules en suspension (poussière, humidité). Les zones d'ombre sont créées par les nuages qui bloquent la lumière.</p>
<p>Les rayons sont en réalité <strong>quasi-parallèles</strong> — le Soleil est si loin que ses rayons arrivent pratiquement parallèles à la surface. L'apparence de divergence est un pur <strong>effet de perspective</strong>, identique aux rails de chemin de fer qui semblent converger au loin.</p>
<p>La preuve : si vous vous retournez et regardez le point anti-solaire (à l'opposé du soleil), vous verrez les <strong>rayons anti-crépusculaires</strong> qui semblent converger vers ce point — les mêmes rayons, vus depuis l'autre direction.</p>
<p><strong>Point clé :</strong> ce phénomène est souvent utilisé pour « prouver » que le soleil est proche (puisque les rayons semblent diverger). C'est en réalité un effet de perspective géométrique bien compris, identique à tout point de fuite.</p>`,
    demarche: [
      `Identifier la source de lumière et les obstacles (nuages) qui créent les ombres`,
      `Observer si les rayons semblent diverger (côté soleil) ET converger (côté anti-solaire) — preuve du parallélisme`,
      `Photographier avec un grand angle pour montrer l'ensemble du phénomène, pas juste une portion`,
      `Comparer avec des lignes de perspective connues (rails, routes) pour illustrer l'effet de point de fuite`,
      `Mesurer l'angle apparent entre les rayons — il correspond à la perspective, pas à une divergence réelle`,
    ],
    checklist: [
      `Les rayons sont-ils visibles des deux côtés du ciel (crépusculaires ET anti-crépusculaires) ?`,
      `La photo montre-t-elle un champ suffisamment large pour juger de la géométrie ?`,
      `Les conditions de diffusion sont-elles identifiées (brume, poussière, humidité) ?`,
      `A-t-on vérifié que l'effet de divergence est identique à un point de fuite classique ?`,
      `La focale de l'objectif est-elle connue (un grand angle exagère la divergence apparente) ?`,
      `A-t-on considéré que la perspective fonctionne de la même manière pour un soleil proche OU lointain ?`,
    ],
  },
  {
    id: 'rayons-anti-crepusculaires',
    type: 'video',
    category: 'atmospherique',
    title: 'Rayons anti-crépusculaires — convergence au point anti-solaire',
    location: 'Visible partout, en se tournant à l\'opposé du soleil',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/9anAi3cF3yM',
    observation: `En tournant le dos au soleil lorsque des rayons crépusculaires sont visibles, on observe les mêmes faisceaux qui semblent maintenant converger vers un point unique à l'horizon, diamétralement opposé au soleil.`,
    analyse: `<p>Les rayons anti-crépusculaires sont <strong>exactement les mêmes rayons</strong> que les rayons crépusculaires, vus depuis la direction opposée. Si les rayons semblent diverger du côté du soleil, ils semblent converger du côté anti-solaire.</p>
<p>C'est la preuve directe que la divergence apparente est un <strong>effet de perspective</strong> et non une divergence réelle. Des rayons réellement divergents ne pourraient pas converger de l'autre côté — seuls des rayons parallèles produisent cet effet symétrique.</p>
<p>Analogie : imaginez une longue route droite. D'un côté, elle semble s'élargir vers vous. De l'autre, elle semble se rétrécir vers l'horizon. La route ne change pas de largeur — c'est votre perspective qui change.</p>`,
    demarche: [
      `Observer simultanément les deux côtés du ciel (crépusculaire et anti-crépusculaire)`,
      `Photographier les deux directions avec la même focale pour comparaison`,
      `Vérifier que les « rayons » anti-crépusculaires pointent exactement vers le point anti-solaire (180° du soleil)`,
      `Documenter l'heure et la position du soleil pour confirmer la géométrie`,
    ],
    checklist: [
      `Les rayons convergent-ils exactement au point anti-solaire ?`,
      `La même scène montre-t-elle divergence d'un côté et convergence de l'autre ?`,
      `La photo est-elle prise avec une focale connue ?`,
      `A-t-on exclu des sources de lumière secondaires ?`,
      `L'effet est-il cohérent avec le modèle de rayons parallèles + perspective ?`,
    ],
  },
  {
    id: 'halo-solaire-22',
    type: 'video',
    category: 'atmospherique',
    title: 'Halo solaire à 22° — anneau lumineux autour du soleil',
    location: 'Visible partout, par cirrus (nuages de haute altitude)',
    source: 'Photographie courante',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/k3L1BX0Czak',
    observation: `Un cercle lumineux parfait entoure le soleil à une distance angulaire d'environ 22°. L'intérieur du cercle est légèrement plus sombre que l'extérieur. Parfois, des couleurs irisées sont visibles (rouge à l'intérieur, bleu à l'extérieur).`,
    analyse: `<p>Le halo de 22° est produit par la <strong>réfraction de la lumière</strong> à travers des cristaux de glace hexagonaux en suspension dans les cirrus (nuages entre 5 000 et 13 000 m d'altitude).</p>
<p>La lumière entre par une face du cristal hexagonal et sort par une face non adjacente, ce qui produit une déviation minimale de <strong>21,8°</strong> (arrondi à 22°). C'est pourquoi le halo a toujours le même rayon angulaire, quelle que soit la taille des cristaux.</p>
<p>L'intérieur du cercle est plus sombre parce qu'aucun rayon ne peut être dévié de moins de 22° par ce type de cristal — c'est un <strong>minimum de déviation</strong>. Les couleurs proviennent de la dispersion chromatique (le rouge est moins dévié que le bleu).</p>
<p>Le halo est un phénomène de <strong>réfraction</strong> (pas de réflexion) et ne dépend que de la géométrie hexagonale des cristaux de glace — un phénomène prévisible et reproductible.</p>`,
    demarche: [
      `Mesurer le rayon angulaire du halo (doit être proche de 22° — un poing à bout de bras ≈ 10°, donc environ 2 poings)`,
      `Observer la distribution des couleurs : rouge à l'intérieur, bleu à l'extérieur (dispersion chromatique)`,
      `Vérifier la présence de cirrus ou de voile nuageux de haute altitude`,
      `Chercher d'autres phénomènes associés : parhélies (faux soleils), arc circumzénithal, arc tangent`,
      `Photographier avec un filtre polarisant pour mieux révéler la structure`,
    ],
    checklist: [
      `Le cercle est-il bien centré sur le soleil (ou la lune) ?`,
      `Le rayon angulaire est-il d'environ 22° (pas 46° — c'est un autre halo) ?`,
      `L'intérieur du cercle est-il plus sombre que l'extérieur ?`,
      `Des cristaux de glace sont-ils plausibles à cette altitude (cirrus visibles) ?`,
      `A-t-on noté l'heure, le lieu et les conditions météo ?`,
      `A-t-on vérifié que ce n'est pas une couronne (beaucoup plus petite, couleurs inversées) ?`,
    ],
  },
  {
    id: 'parhelie-faux-soleils',
    type: 'video',
    category: 'atmospherique',
    title: 'Parhélie (faux soleils / sun dogs) — deux soleils à 22°',
    location: 'Régions froides, mais visible partout avec des cirrus',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/8GHZOvhxS1E',
    observation: `Deux taches lumineuses brillantes apparaissent de chaque côté du soleil, à environ 22° de distance. Elles sont souvent colorées (rouge vers le soleil, bleu à l'extérieur). Parfois, seule une parhélie est visible. Elles sont à la même hauteur que le soleil.`,
    analyse: `<p>Les parhélies sont produites par la réfraction de la lumière à travers des <strong>cristaux de glace plats</strong> (en forme de plaquette hexagonale) qui tombent horizontalement dans l'atmosphère, comme des feuilles mortes.</p>
<p>Cette orientation horizontale spécifique fait que la lumière est déviée principalement dans le plan horizontal — d'où les taches lumineuses <strong>à gauche et à droite</strong> du soleil, et non au-dessus ni en dessous.</p>
<p>La distance de 22° est la même que celle du halo, car c'est le même angle de déviation minimale à travers un prisme hexagonal. Mais le halo est produit par des cristaux orientés aléatoirement (cercle complet), tandis que les parhélies sont produites par des cristaux alignés horizontalement (points lumineux).</p>
<p>Quand le soleil est bas sur l'horizon, les parhélies sont exactement à 22°. Quand il monte, elles s'éloignent progressivement.</p>`,
    demarche: [
      `Mesurer la distance angulaire entre le soleil et chaque parhélie (~22° quand le soleil est bas)`,
      `Vérifier que les parhélies sont à la même hauteur que le soleil (critère distinctif)`,
      `Observer la distribution des couleurs (rouge côté soleil, bleu côté extérieur)`,
      `Chercher le halo de 22° — les parhélies apparaissent souvent sur le halo`,
      `Noter la hauteur du soleil au-dessus de l'horizon (les parhélies s'éloignent quand le soleil monte)`,
    ],
    checklist: [
      `Les taches sont-elles symétriques par rapport au soleil ?`,
      `Sont-elles à la même hauteur que le soleil ?`,
      `La distance angulaire est-elle d'environ 22° ?`,
      `Des cirrus ou un voile de glace sont-ils visibles ?`,
      `A-t-on exclu un reflet interne de l'objectif (lens flare) ?`,
      `L'effet disparaît-il si on change de position (un reflet optique suivrait la caméra) ?`,
    ],
  },
  {
    id: 'pilier-lumineux',
    type: 'video',
    category: 'atmospherique',
    title: 'Pilier lumineux — colonne de lumière verticale',
    location: 'Régions froides, villes en hiver',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/h7JGYma5yZ0',
    observation: `Une colonne de lumière verticale s'élève au-dessus (et parfois en dessous) du soleil couchant, ou au-dessus de lampadaires et sources de lumière artificielles par nuit froide. La colonne semble solide et peut s'étendre sur plusieurs degrés.`,
    analyse: `<p>Les piliers lumineux sont un phénomène de <strong>réflexion</strong> (pas de réfraction) sur des cristaux de glace plats qui tombent presque horizontalement dans l'air calme.</p>
<p>Chaque cristal agit comme un minuscule miroir horizontal. La lumière du soleil (ou d'un lampadaire) se reflète sur des millions de ces miroirs microscopiques, à différentes hauteurs. L'ensemble de ces reflets crée l'illusion d'une colonne verticale continue.</p>
<p>Le pilier n'est pas un faisceau de lumière réel — c'est un effet collectif de millions de reflets individuels. C'est pourquoi il est toujours centré sur la source de lumière vue depuis l'observateur.</p>
<p>Les piliers lumineux au-dessus de lampadaires sont particulièrement faciles à observer en hiver dans les régions froides (Canada, Scandinavie, Russie) et prouvent que le phénomène ne nécessite pas le soleil.</p>`,
    demarche: [
      `Identifier la source de lumière (soleil, lampadaire, phare) et vérifier que le pilier est centré dessus`,
      `Observer si le pilier change de position quand l'observateur se déplace (il devrait suivre la source)`,
      `Vérifier les conditions : température négative, air calme, cristaux de glace en suspension`,
      `Comparer avec d'autres sources lumineuses proches — chacune devrait avoir son propre pilier`,
      `Photographier avec différentes expositions pour révéler la structure`,
    ],
    checklist: [
      `Le pilier est-il parfaitement vertical et centré sur la source ?`,
      `La température est-elle suffisamment basse pour des cristaux de glace (-10°C ou moins) ?`,
      `D'autres sources lumineuses produisent-elles aussi des piliers ?`,
      `A-t-on exclu un artefact photographique (reflet interne, flare) ?`,
      `L'air est-il calme (les cristaux doivent tomber horizontalement) ?`,
    ],
  },
  {
    id: 'gloire-brocken',
    type: 'video',
    category: 'atmospherique',
    title: 'Gloire (spectre de Brocken) — halo arc-en-ciel autour de son ombre',
    location: 'Montagnes, avions, brouillard dense',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/Kj4-KFhtV4Y',
    observation: `L'observateur voit sa propre ombre projetée sur un nuage ou du brouillard en contrebas, entourée d'anneaux concentriques colorés (arc-en-ciel). L'ombre semble parfois gigantesque. Le phénomène est centré exactement sur la tête de l'observateur.`,
    analyse: `<p>La gloire est produite par la <strong>rétrodiffusion</strong> de la lumière par de très petites gouttelettes d'eau (brouillard ou nuage). C'est un phénomène d'<strong>optique ondulatoire</strong> — il ne peut pas être expliqué par la simple réfraction géométrique.</p>
<p>La lumière pénètre dans les gouttelettes, subit des réflexions internes, et ressort presque exactement dans la direction d'où elle venait. L'interférence entre les ondes produites par de nombreuses gouttelettes crée les anneaux colorés.</p>
<p>Le phénomène est toujours centré sur le <strong>point anti-solaire</strong> — c'est-à-dire exactement à l'opposé du soleil par rapport à l'observateur. C'est pourquoi chaque personne voit la gloire autour de sa propre tête.</p>
<p>Depuis un avion, la gloire est visible autour de l'ombre de l'avion sur les nuages en dessous — un phénomène fréquent et facilement photographiable.</p>`,
    demarche: [
      `Vérifier que le phénomène est centré sur le point anti-solaire (ombre de la tête de l'observateur)`,
      `Compter le nombre d'anneaux colorés — il dépend de la taille des gouttelettes`,
      `Mesurer le rayon angulaire des anneaux (typiquement 5° à 20°)`,
      `Documenter les conditions : altitude, type de nuage/brouillard, position du soleil`,
      `Observer si d'autres personnes voient la gloire autour de LEUR propre ombre (chacun a la sienne)`,
    ],
    checklist: [
      `Le phénomène est-il centré sur l'ombre de l'observateur (pas ailleurs) ?`,
      `Les anneaux sont-ils concentriques et colorés (pas un simple halo blanc) ?`,
      `Y a-t-il du brouillard ou des nuages en contrebas ?`,
      `Le soleil est-il derrière l'observateur ?`,
      `A-t-on exclu un reflet interne de l'objectif ?`,
      `L'ombre est-elle anormalement grande (effet de projection sur surface éloignée) ?`,
    ],
  },
  {
    id: 'nuages-lenticulaires',
    type: 'video',
    category: 'atmospherique',
    title: 'Nuages lenticulaires — soucoupes au-dessus des montagnes',
    location: 'Zones montagneuses, vents forts en altitude',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/KF0XIGTVR1o',
    observation: `Des nuages en forme de lentille ou de soucoupe volante apparaissent au-dessus ou en aval de reliefs montagneux. Ils semblent immobiles malgré le vent fort, et présentent souvent des bords très nets et des formes empilées.`,
    analyse: `<p>Les nuages lenticulaires (altocumulus lenticularis) se forment dans les <strong>ondes de relief</strong> — des ondulations de l'atmosphère créées quand le vent est forcé de monter au-dessus d'une montagne.</p>
<p>L'air humide monte dans la crête de l'onde, se refroidit, et la vapeur d'eau se condense en nuage. Dans le creux suivant, l'air redescend, se réchauffe, et le nuage s'évapore. Le résultat est un nuage <strong>stationnaire</strong> : l'air le traverse en permanence, mais le nuage reste au même endroit.</p>
<p>C'est comme une vague dans une rivière au-dessus d'un rocher : la vague reste fixe, mais l'eau coule à travers elle. Le nuage est la « vague » atmosphérique.</p>
<p>Les formes empilées (pile d'assiettes) se produisent quand plusieurs couches d'air humide sont séparées par des couches d'air sec, créant une série de lentilles superposées.</p>`,
    demarche: [
      `Identifier le relief responsable de l'onde (montagne, crête) en amont du vent`,
      `Vérifier que le nuage reste stationnaire malgré le vent (critère distinctif — filmer en time-lapse)`,
      `Observer la direction du vent en altitude (le nuage est en aval du relief)`,
      `Chercher d'autres nuages lenticulaires dans la même zone (les ondes produisent souvent une série)`,
      `Documenter la vitesse et direction du vent à différentes altitudes si possible`,
    ],
    checklist: [
      `Le nuage est-il en forme de lentille/disque avec des bords nets ?`,
      `Est-il stationnaire (ne dérive-t-il pas avec le vent) ?`,
      `Y a-t-il un relief montagneux en amont ?`,
      `Le vent souffle-t-il perpendiculairement à la crête ?`,
      `A-t-on exclu un nuage ordinaire qui aurait temporairement cette forme ?`,
      `Un time-lapse montre-t-il que l'air traverse le nuage sans le déplacer ?`,
    ],
  },
  {
    id: 'eclair-chaleur',
    type: 'video',
    category: 'atmospherique',
    title: 'Éclair de chaleur (heat lightning) — foudre sans tonnerre',
    location: 'Visible partout, horizon dégagé, nuit d\'été',
    source: 'Observation courante',
    duration: '~2 min',
    embedUrl: 'https://www.youtube.com/embed/S0y9hEEI0ug',
    observation: `Par nuit d'été, des éclairs illuminent l'horizon sans qu'aucun tonnerre ne soit audible. Le ciel au-dessus de l'observateur est dégagé. Les éclairs semblent silencieux et diffus, sans la forme en zigzag typique de la foudre proche.`,
    analyse: `<p>L'« éclair de chaleur » n'est <strong>pas un phénomène distinct</strong> de la foudre ordinaire. C'est simplement un orage normal si éloigné que le <strong>son ne parvient pas</strong> jusqu'à l'observateur.</p>
<p>Le son du tonnerre se propage dans l'air et s'atténue avec la distance. Au-delà d'environ <strong>15–25 km</strong>, le tonnerre n'est généralement plus audible — l'air absorbe les ondes sonores et la courbure du sol les dévie vers le haut.</p>
<p>En revanche, la <strong>lumière</strong> des éclairs peut être visible à plus de <strong>150 km</strong> de distance, surtout la nuit, car elle se reflète sur les nuages et la vapeur d'eau dans l'atmosphère.</p>
<p>L'apparence diffuse (pas de zigzag visible) s'explique par la distance : les détails du canal de foudre sont trop petits pour être résolus à l'œil nu, et la lumière est diffusée par l'atmosphère intermédiaire.</p>`,
    demarche: [
      `Estimer la distance de l'orage : compter le temps entre l'éclair et le tonnerre (si audible), ou vérifier les cartes météo en temps réel`,
      `Vérifier qu'un orage est effectivement en cours dans la direction observée (radar météo, sites de foudre en temps réel)`,
      `Observer si le phénomène est accompagné de nuages à l'horizon (cumulonimbus lointains)`,
      `Comparer l'apparence avec des éclairs proches : les éclairs lointains sont diffus, les proches sont en zigzag net`,
      `Documenter les conditions locales : aucun nuage au-dessus de l'observateur, ciel dégagé`,
    ],
    checklist: [
      `Un orage est-il confirmé dans la direction observée (radar météo) ?`,
      `Le tonnerre est-il absent (distance > 15-25 km confirmée) ?`,
      `Les éclairs sont-ils diffus (pas de structure nette visible) ?`,
      `Le phénomène est-il localisé à l'horizon (pas au zénith) ?`,
      `A-t-on exclu d'autres sources lumineuses (avions, projecteurs) ?`,
      `La distance estimée est-elle cohérente avec la portée visuelle de la foudre ?`,
    ],
  },
];
