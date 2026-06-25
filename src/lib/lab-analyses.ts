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
    embedUrl: 'https://www.youtube.com/embed/Lgi_kPy-fjQ',
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
    relatedArticle: 'lhorizon-la-perspective-et-la-refraction',
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
    relatedArticle: 'lhorizon-la-perspective-et-la-refraction',
  },
  {
    id: 'rayons-crepusculaires',
    type: 'video',
    category: 'atmospherique',
    title: 'Rayons crépusculaires',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
  {
    id: 'parhelie-faux-soleils',
    type: 'video',
    category: 'atmospherique',
    title: 'Parhélie (faux soleils / sun dogs) — 7 soleils?',
    location: 'Régions froides, mais visible partout avec des cirrus',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/R4cbvsJvGUg',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
  {
    id: 'gloire-brocken',
    type: 'video',
    category: 'atmospherique',
    title: 'Halo arc-en-ciel',
    location: 'Montagnes, avions, brouillard dense',
    source: 'Photographie',
    duration: '~2-5 min',
    embedUrl: 'https://www.youtube.com/embed/KxwvMfzYWwM',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
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
    observation: `Des nuages en forme de lentille ou de soucoupe apparaissent au-dessus ou en aval de reliefs montagneux. Ils semblent immobiles malgré le vent fort, et présentent souvent des bords très nets et des formes empilées.`,
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
    relatedArticle: 'la-pression-atmospherique-un-ocean-d-air-invisible',
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
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
  {
    id: 'compression-perspective-telephoto',
    type: 'video',
    category: 'optique',
    title: 'Compression de perspective au téléobjectif',
    location: 'Tout environnement avec profondeur de champ',
    source: 'Photographie et vidéographie documentée',
    duration: '~3-5 min',
    embedUrl: 'https://www.youtube.com/embed/_TTXY1Se0eg',
    observation: `Quand on filme une scène avec un puissant zoom (téléobjectif), les objets éloignés semblent beaucoup plus proches les uns des autres. Une route paraît écrasée, les montagnes semblent collées aux bâtiments, le soleil ou la lune apparaissent énormes derrière un paysage. Cet effet est absent à l'œil nu ou avec un grand-angle.`,
    analyse: `<p>La <strong>compression de perspective</strong> (ou compression focale) est un phénomène purement géométrique lié à la <strong>distance d'observation</strong>, pas à l'optique de l'objectif en soi.</p>
<p>Un téléobjectif ne "compresse" rien physiquement — il <strong>recadre</strong> une portion étroite du champ visuel. Comme l'observateur est très loin de la scène, les rapports de distance entre les objets proches et lointains deviennent faibles. Résultat : tout semble empilé sur le même plan.</p>
<p>Formellement : si deux objets sont à distances d₁ et d₂ de la caméra, leur taille apparente relative est proportionnelle à d₁/d₂. Quand d₁ et d₂ sont grands et proches, ce rapport tend vers 1 → les objets semblent à la même distance.</p>
<p><strong>Implication pour l'observation :</strong> l'effet de compression peut faire croire qu'un objet "revient" après avoir disparu derrière l'horizon — en réalité, le zoom révèle des détails déjà présents mais trop petits pour l'œil nu. Cela ne signifie pas que l'objet était "caché par la distance" plutôt que par la courbure.</p>`,
    demarche: [
      `Documenter la focale utilisée (mm) — plus la focale est longue, plus l'effet est marqué`,
      `Comparer la même scène à plusieurs focales (grand-angle vs téléobjectif) pour isoler l'effet`,
      `Mesurer les distances réelles entre la caméra et les différents plans de la scène`,
      `Vérifier si l'objet « ramené » au zoom était partiellement visible ou totalement caché`,
      `Distinguer compression de perspective (géométrie) et réfraction (atmosphère)`,
    ],
    checklist: [
      `La focale et le modèle de caméra sont-ils précisés ?`,
      `La distance entre la caméra et le sujet est-elle connue ?`,
      `A-t-on comparé avec d'autres focales depuis le même point ?`,
      `La hauteur de la caméra par rapport au sol/eau est-elle documentée ?`,
      `A-t-on exclu un effet de réfraction atmosphérique (chaleur, humidité) ?`,
      `L'objet est-il réellement ramené ou simplement mieux résolu ?`,
    ],
    relatedArticle: 'la-perspective-lineaire',
  },
  {
    id: 'point-de-fuite-rails',
    type: 'video',
    category: 'optique',
    title: 'Point de fuite et lignes de chemin de fer',
    location: 'Voie ferrée rectiligne, route droite',
    source: 'Géométrie projective classique',
    duration: '~3 min',
    embedUrl: 'https://www.youtube.com/embed/rG3qzZuneRg',
    observation: `En regardant le long d'une voie ferrée droite, les deux rails semblent converger vers un point unique à l'horizon — le point de fuite. Les traverses paraissent de plus en plus serrées. Si on avance, le point de fuite recule toujours. En théorie, les rails sont parallèles et ne se rejoignent jamais.`,
    analyse: `<p>Le <strong>point de fuite</strong> est une conséquence directe de la <strong>projection perspective</strong> — la façon dont notre œil (ou une caméra) projette un espace 3D sur une surface 2D (rétine ou capteur).</p>
<p>Des lignes parallèles dans l'espace 3D convergent vers un point unique dans l'image 2D lorsqu'elles s'éloignent de l'observateur. C'est un théorème de <strong>géométrie projective</strong>, démontrable mathématiquement.</p>
<p>La taille angulaire d'un objet diminue avec la distance selon : <code>θ ≈ h / d</code> (en radians), où h est la hauteur réelle et d la distance. À grande distance, θ devient inférieur à la résolution angulaire de l'œil (~1 minute d'arc) → l'objet devient invisible.</p>
<p><strong>Point clé :</strong> le point de fuite est souvent confondu avec « l'horizon ». Ce sont deux concepts distincts : le point de fuite est géométrique (projection), l'horizon est physique (limite de visibilité). Sur une surface plane infinie, le point de fuite coïncide avec l'horizon géométrique. Sur une surface courbe, l'horizon est plus proche.</p>`,
    demarche: [
      `Observer depuis différentes hauteurs : le point de fuite se déplace-t-il verticalement ?`,
      `Mesurer l'écartement apparent des rails à différentes distances connues`,
      `Vérifier si un objet placé au « point de fuite » est réellement invisible ou simplement trop petit`,
      `Utiliser un téléobjectif pour « ouvrir » le point de fuite — les rails redeviennent-ils parallèles ?`,
      `Distinguer disparition par résolution angulaire et disparition par obstruction (courbure, obstacle)`,
    ],
    checklist: [
      `Le terrain est-il vérifié comme plat et rectiligne (GPS, nivellement) ?`,
      `La hauteur de l'observateur est-elle précisée ?`,
      `A-t-on utilisé plusieurs focales pour observer le même point de fuite ?`,
      `Les conditions atmosphériques permettent-elles une visibilité suffisante ?`,
      `A-t-on mesuré la distance maximale à laquelle un objet de taille connue reste visible ?`,
      `Le phénomène est-il reproductible dans des conditions différentes ?`,
    ],
    relatedArticle: 'la-perspective-lineaire',
  },
  {
    id: 'bateau-zoom-horizon',
    type: 'video',
    category: 'optique',
    title: 'Bateau « disparu » ramené au zoom',
    location: 'Bord de mer, lac, étendue d\'eau',
    source: 'Vidéos documentaires et amateurs',
    duration: '~3-5 min',
    embedUrl: 'https://www.youtube.com/embed/ZtUVandOJj4',
    observation: `Un bateau s'éloigne et semble « couler » progressivement sous l'horizon — d'abord la coque, puis les superstructures. Mais en utilisant un zoom puissant (Nikon P900/P1000), une partie ou la totalité du bateau réapparaît. Ce test est fréquemment utilisé comme argument dans les deux sens du débat.`,
    analyse: `<p>C'est l'un des tests les plus discutés. Plusieurs phénomènes se superposent :</p>
<p><strong>1. Résolution angulaire :</strong> à grande distance, la coque (basse, sombre, contre l'eau) disparaît en premier car sa taille angulaire tombe sous le seuil de résolution. Le zoom augmente la résolution effective → la coque réapparaît.</p>
<p><strong>2. Réfraction atmosphérique :</strong> au-dessus de l'eau, l'air forme un gradient de densité qui courbe les rayons lumineux. Cet effet peut « relever » un bateau théoriquement sous l'horizon géométrique (mirage supérieur).</p>
<p><strong>3. Courbure géométrique :</strong> sur une sphère de rayon R, un objet de hauteur h disparaît au-delà de d ≈ √(2Rh). Pour un observateur à 2m et un bateau à 15km, la courbure cache ~15m de coque.</p>
<p><strong>Le problème :</strong> sans mesures précises de hauteur d'observation, distance, conditions de réfraction, et hauteur du bateau, il est <strong>impossible</strong> de conclure. Chaque variable change le résultat. C'est pourquoi ce test, mal contrôlé, ne prouve rien dans aucun sens.</p>`,
    demarche: [
      `Mesurer précisément : hauteur de l'observateur (GPS + altimètre), distance du bateau (AIS, radar), hauteur du bateau`,
      `Documenter les conditions de réfraction : température air/eau, humidité, pression, vent`,
      `Filmer en continu depuis la disparition jusqu'au zoom maximal — sans coupure`,
      `Comparer ce qui est visible au zoom avec le calcul de courbure + réfraction standard`,
      `Répéter le test à différents moments de la journée (la réfraction varie énormément)`,
      `Utiliser un laser ou une cible de hauteur connue plutôt qu'un bateau (mesures plus contrôlées)`,
    ],
    checklist: [
      `La distance du bateau est-elle mesurée (pas estimée) ?`,
      `La hauteur exacte de l'observateur au-dessus de l'eau est-elle connue ?`,
      `Les conditions de réfraction sont-elles documentées (T° air/eau, gradient) ?`,
      `Le zoom ramène-t-il le bateau EN ENTIER ou seulement partiellement ?`,
      `La coque est-elle réellement visible ou juste un reflet/mirage ?`,
      `Le test a-t-il été répété dans des conditions variées ?`,
      `La focale et le capteur de la caméra sont-ils précisés ?`,
    ],
    relatedArticle: 'la-perspective-pourquoi-les-objets-disparaissent',
  },
  {
    id: 'looming-towering-refraction',
    type: 'video',
    category: 'optique',
    title: 'Looming et towering — objets étirés par réfraction',
    location: 'Zones côtières, lacs, régions arctiques',
    source: 'Météorologie optique documentée',
    duration: '~3 min',
    embedUrl: 'https://www.youtube.com/embed/ILVdi_9C1T0',
    observation: `Des objets lointains (bâtiments, navires, côtes) apparaissent anormalement grands, étirés verticalement, ou surélevés au-dessus de leur position réelle. L'effet peut être spectaculaire : des villes entières semblent flotter, des falaises paraissent deux fois plus hautes. Le phénomène est plus fréquent en conditions d'inversion thermique.`,
    analyse: `<p>Le <strong>looming</strong> (surélévation) et le <strong>towering</strong> (étirement vertical) sont des formes de réfraction anormale causées par des gradients de température non standard dans l'atmosphère.</p>
<p>En conditions normales, la température diminue avec l'altitude (~6.5°C/km). Quand une <strong>inversion thermique</strong> crée une couche d'air chaud au-dessus d'air froid, les rayons lumineux se courbent plus fortement que d'habitude.</p>
<p><strong>Looming :</strong> l'objet entier est relevé — il apparaît plus haut qu'il ne l'est. Cela peut rendre visibles des objets normalement sous l'horizon. <strong>Towering :</strong> la courbure varie avec la hauteur, étirant verticalement l'image de l'objet.</p>
<p>L'effet inverse existe aussi : <strong>sinking</strong> (abaissement) et <strong>stooping</strong> (compression verticale), quand le gradient de température est inversé (air froid en altitude, rare mais possible).</p>
<p>Ces phénomènes montrent que l'atmosphère est un <strong>milieu optique actif</strong> qui déforme systématiquement ce que nous voyons à l'horizon.</p>`,
    demarche: [
      `Documenter le profil thermique vertical (radiosondage ou mesures étagées) au moment de l'observation`,
      `Mesurer la position réelle de l'objet (GPS, carte) et comparer avec sa position apparente`,
      `Photographier à intervalles pour documenter l'évolution temporelle de l'effet`,
      `Comparer avec les prévisions météo : une inversion thermique était-elle prévue ?`,
      `Mesurer l'étirement vertical : rapport entre taille apparente et taille réelle connue`,
    ],
    checklist: [
      `Les conditions d'inversion thermique sont-elles confirmées (données météo) ?`,
      `La position réelle de l'objet est-elle connue avec précision ?`,
      `L'étirement/surélévation est-il documenté photographiquement ?`,
      `A-t-on exclu un simple effet de grossissement optique (focale longue) ?`,
      `Le phénomène évolue-t-il dans le temps (signe d'origine atmosphérique) ?`,
      `La distance et la hauteur d'observation sont-elles documentées ?`,
    ],
    relatedArticle: 'lhorizon-la-perspective-et-la-refraction',
  },
  {
    id: 'scintillation-stellaire',
    type: 'video',
    category: 'optique',
    title: 'Scintillation des étoiles/planètes',
    location: 'Observation nocturne, tout lieu',
    source: 'Astronomie observationnelle fondamentale',
    duration: '~3 min',
    embedUrl: 'https://www.tiktok.com/embed/v2/ZNRTVeGfN',
    observation: `Les étoiles scintillent (clignotent, changent de couleur et d'intensité) surtout près de l'horizon, tandis que les planètes restent relativement stables. L'effet augmente par temps agité et diminue en altitude (montagne) ou dans l'espace (photos satellite). Par temps très calme, même les étoiles scintillent moins.`,
    analyse: `<p>La scintillation est causée par les <strong>turbulences atmosphériques</strong> — des cellules d'air de températures et densités différentes qui se déplacent en permanence.</p>
<p>Chaque cellule d'air agit comme une petite lentille qui dévie légèrement le rayon lumineux. Comme ces cellules bougent constamment, le rayon d'une étoile est dévié de façon aléatoire → l'étoile semble « danser » et changer d'éclat.</p>
<p><strong>Pourquoi les planètes ne scintillent pas (ou peu) ?</strong> Une étoile est une source ponctuelle (taille angulaire ~0.001"). Une planète a un disque mesurable (~10-50"). Les turbulences affectent différentes parties du disque indépendamment, et ces variations se moyennent → la lumière totale reste stable.</p>
<p><strong>Pourquoi plus de scintillation à l'horizon ?</strong> Près de l'horizon, la lumière traverse une épaisseur d'atmosphère ~38× plus grande qu'au zénith (loi de sécante) → plus de cellules turbulentes traversées → plus de déviation.</p>`,
    demarche: [
      `Observer la même étoile à différentes hauteurs au-dessus de l'horizon (du lever au transit)`,
      `Comparer étoile (ponctuelle) vs planète (disque) dans les mêmes conditions`,
      `Documenter les conditions météo : vent en altitude, stabilité atmosphérique (seeing)`,
      `Observer depuis différentes altitudes (plaine vs montagne) pour vérifier l'effet de l'épaisseur d'air`,
      `Filmer au ralenti pour décomposer les variations de luminosité et de couleur`,
    ],
    checklist: [
      `L'objet observé est-il identifié (étoile, planète, satellite, avion) ?`,
      `La hauteur au-dessus de l'horizon est-elle mesurée ?`,
      `Les conditions atmosphériques sont-elles documentées (seeing, vent) ?`,
      `A-t-on comparé avec une planète visible au même moment ?`,
      `Le phénomène varie-t-il au cours de la nuit (changement de conditions) ?`,
      `L'altitude du lieu d'observation est-elle précisée ?`,
    ],
    relatedArticle: 'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
  },
  {
    id: 'rayon-vert-sunset',
    type: 'video',
    category: 'optique',
    title: 'Rayon vert (green flash) au coucher de soleil',
    location: 'Horizon maritime dégagé, conditions atmosphériques stables',
    source: 'Phénomène optique atmosphérique bien documenté',
    duration: '~2-3 min',
    embedUrl: 'https://www.youtube.com/embed/BA4qFJ22yTU',
    observation: `Pendant une fraction de seconde, juste au moment où le dernier segment du soleil disparaît sous l'horizon, un éclat vert vif apparaît. Le phénomène est bref (1-2 secondes), rare dans des conditions parfaites, et plus fréquent sur un horizon maritime dégagé. Il existe aussi au lever du soleil (premier segment).`,
    analyse: `<p>Le rayon vert est un phénomène de <strong>dispersion atmosphérique</strong> combiné à la réfraction.</p>
<p>L'atmosphère agit comme un prisme : elle réfracte davantage les courtes longueurs d'onde (bleu, vert) que les longues (rouge). Au coucher, le soleil produit en réalité un petit spectre vertical : une image rouge en bas, verte en haut, bleue encore plus haut.</p>
<p>Normalement ces images se chevauchent et on ne voit que du blanc-jaune. Mais quand le <strong>dernier fragment</strong> du soleil est visible, seule l'image la plus réfractée (verte) reste au-dessus de l'horizon. L'image bleue est trop diffusée par l'atmosphère (diffusion Rayleigh) pour être visible.</p>
<p>Le rayon vert nécessite : (1) un horizon très net et dégagé, (2) une atmosphère stable (pas trop de turbulence), (3) une réfraction suffisante mais pas excessive. C'est un phénomène parfaitement prédit par l'optique atmosphérique.</p>`,
    demarche: [
      `Se positionner face à un horizon maritime dégagé, sans obstacle`,
      `Filmer le coucher de soleil en continu avec un téléobjectif (200mm+)`,
      `Documenter l'heure exacte, la position GPS, les conditions météo`,
      `Comparer avec les éphémérides : le soleil se couche-t-il exactement où et quand prévu ?`,
      `Répéter l'observation sur plusieurs jours pour évaluer la fréquence du phénomène`,
    ],
    checklist: [
      `L'horizon est-il parfaitement dégagé (mer, pas de nuages bas) ?`,
      `La vidéo est-elle en continu (pas de montage autour du moment critique) ?`,
      `Le flash vert dure-t-il 1-2 secondes (durée attendue) ?`,
      `Les conditions atmosphériques sont-elles documentées ?`,
      `A-t-on exclu un artéfact optique de la caméra (aberration chromatique, flare) ?`,
      `L'heure et la position sont-elles cohérentes avec les éphémérides solaires ?`,
    ],
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
  {
    id: 'gyroscope-moment-angulaire',
    type: 'video',
    category: 'mecanique',
    title: 'Gyroscope',
    location: 'Laboratoire, démonstration de physique',
    source: 'Mécanique classique fondamentale',
    duration: '~5 min',
    embedUrl: 'https://www.youtube.com/embed/giiRLMesFFA',
    observation: `Un gyroscope en rotation résiste aux changements d'orientation : il maintient son axe fixe dans l'espace même quand on incline son support. Si on applique une force pour le faire basculer, il ne tombe pas mais « précesse » — son axe tourne lentement autour de la verticale. Plus il tourne vite, plus il est stable.`,
    analyse: `<p>Le gyroscope illustre la <strong>conservation du moment cinétique</strong> (L = Iω). Un objet en rotation possède un vecteur moment cinétique aligné avec son axe de rotation. Ce vecteur ne change de direction que si un <strong>couple extérieur</strong> (torque) est appliqué.</p>
<p>La <strong>précession</strong> se produit quand la gravité exerce un couple sur le gyroscope incliné. Au lieu de tomber, l'axe tourne perpendiculairement au couple — c'est la règle du produit vectoriel : dL/dt = τ.</p>
<p>La vitesse de précession est : <code>Ω = τ / (Iω)</code> — plus le gyroscope tourne vite (ω grand), plus la précession est lente et l'axe est stable.</p>
<p><strong>Applications :</strong> le gyrocompas (navigation), les gyroscopes MEMS (smartphones), la stabilisation des satellites, et historiquement l'argument de la rotation terrestre (le gyroscope maintient son axe fixe par rapport aux étoiles, pas par rapport au sol).</p>`,
    demarche: [
      `Varier la vitesse de rotation et observer l'effet sur la stabilité et la vitesse de précession`,
      `Mesurer la vitesse de précession et comparer avec la formule théorique Ω = mgl/(Iω)`,
      `Tester dans différentes orientations pour vérifier l'indépendance du comportement par rapport à la gravité locale`,
      `Documenter la masse, le rayon, la vitesse de rotation avec des instruments de mesure`,
      `Comparer gyroscope mécanique et gyroscope laser (Sagnac) — mêmes principes ?`,
    ],
    checklist: [
      `La vitesse de rotation du gyroscope est-elle mesurée (tachymètre) ?`,
      `La vitesse de précession observée correspond-elle à la théorie ?`,
      `Le gyroscope est-il suffisamment isolé des vibrations extérieures ?`,
      `A-t-on testé à différentes vitesses pour vérifier la relation inverse ?`,
      `Le frottement de l'axe est-il minimisé (roulement de qualité) ?`,
      `L'expérience est-elle reproductible avec les mêmes paramètres ?`,
    ],
    relatedArticle: 'la-rotation-terrestre-deux-experiences-zero-preuve',
  },
  {
    id: 'coriolis-evier-drain',
    type: 'video',
    category: 'mecanique',
    title: 'Effet Coriolis et sens de rotation dans un évier',
    location: 'Hémisphère Nord et Sud (démonstration comparative)',
    source: 'SmarterEveryDay / Veritasium (vidéos synchronisées)',
    duration: '~5-8 min',
    embedUrl: 'https://www.youtube.com/embed/aDorTBEhEtk',
    observation: `Le mythe populaire dit que l'eau d'un évier tourne dans un sens dans l'hémisphère Nord et dans l'autre sens au Sud. En réalité, dans un évier ordinaire, le sens dépend de la géométrie du bassin et des conditions initiales. MAIS dans des conditions très contrôlées (grande bassine, eau immobile depuis longtemps, bouchon retiré par en dessous), l'effet Coriolis est détectable.`,
    analyse: `<p>La <strong>force de Coriolis</strong> est une force fictive (inertielle) qui apparaît dans un référentiel en rotation. Sur Terre, tout objet en mouvement subit une déviation : vers la droite dans l'hémisphère Nord, vers la gauche au Sud.</p>
<p>L'accélération de Coriolis est : <code>a = -2ω × v</code>, où ω est la vitesse angulaire de la Terre (~7.3×10⁻⁵ rad/s) et v la vitesse de l'objet. Pour un évier, cette accélération est <strong>extrêmement faible</strong> — ~10⁻⁷ m/s² — des millions de fois plus petite que les courants résiduels dans l'eau.</p>
<p>C'est pourquoi le sens de rotation d'un évier ordinaire est aléatoire. Pour observer l'effet Coriolis à cette échelle, il faut : (1) une grande bassine (~1.5m), (2) laisser l'eau se stabiliser pendant 24h+, (3) retirer le bouchon par en dessous sans perturber l'eau.</p>
<p><strong>Point clé :</strong> l'effet Coriolis est bien réel et mesurable à grande échelle (cyclones, courants océaniques, balistique longue portée). Son absence dans un évier ne prouve pas qu'il n'existe pas — il est simplement masqué par des forces bien plus grandes.</p>`,
    demarche: [
      `Distinguer clairement les deux échelles : évier (Coriolis négligeable) vs grande bassine contrôlée (détectable)`,
      `Pour une démonstration rigoureuse : bassin de 1.5m+, eau stabilisée 24h, retrait du bouchon par en dessous`,
      `Répéter l'expérience plusieurs fois pour vérifier la cohérence du sens de rotation`,
      `Si possible, réaliser la même expérience dans les deux hémisphères (comme Veritasium/SmarterEveryDay)`,
      `Calculer l'accélération de Coriolis attendue et comparer avec les forces parasites estimées`,
    ],
    checklist: [
      `La taille du bassin est-elle suffisante pour que Coriolis soit détectable ?`,
      `L'eau a-t-elle été laissée au repos suffisamment longtemps ?`,
      `Le bouchon a-t-il été retiré sans perturber l'eau ?`,
      `L'expérience a-t-elle été répétée plusieurs fois ?`,
      `Le sens de rotation est-il cohérent avec l'hémisphère (antihoraire au Nord, horaire au Sud) ?`,
      `A-t-on exclu les effets de la géométrie du bassin et des conditions initiales ?`,
    ],
    relatedArticle: 'la-rotation-terrestre-deux-experiences-zero-preuve',
  },
  {
    id: 'pendule-foucault-rotation',
    type: 'video',
    category: 'mecanique',
    title: 'Pendule de Foucault — preuve de la rotation terrestre ?',
    location: 'Panthéon de Paris, musées de sciences',
    source: 'Léon Foucault (1851), reproductions multiples',
    duration: '~5 min',
    embedUrl: 'https://odysee.com/$/embed/@Flat-Earth-Odysee:5/%E2%9E%96Terre-plate%E2%9E%96-Le-pendule-de-Foucault:c',
    observation: `Un long pendule (67m au Panthéon) oscille librement. Au fil des heures, son plan d'oscillation semble tourner lentement par rapport au sol. Au Panthéon (latitude 48.8°N), le plan tourne de ~11.3° par heure. À l'équateur, il ne tournerait pas. Au pôle, il ferait un tour complet en ~24h.`,
    analyse: `<p>Le pendule de Foucault est présenté comme une preuve directe de la rotation terrestre. Le pendule, une fois lancé, oscille dans un plan fixe par rapport aux étoiles — c'est le <strong>sol qui tournerait sous le pendule</strong>.</p>
<p>La vitesse de rotation apparente dépend de la latitude : <code>T = 24h / sin(φ)</code>. À Paris (48.8°N) : le plan tourne de ~11.3°/h.</p>
<p><strong>Le problème épistémologique :</strong> cette interprétation repose sur un <strong>postulat implicite non démontré</strong> — l'existence d'un espace absolu par rapport auquel le pendule reste fixe. Or, c'est précisément ce que l'expérience est censée démontrer. Le raisonnement est <strong>circulaire</strong> : on suppose ce qu'on veut prouver.</p>
<p><strong>Le principe de Mach :</strong> Ernst Mach a proposé que l'inertie d'un objet est déterminée par les masses lointaines de l'univers. Dans ce cadre, le pendule ne prouve pas que la Terre tourne — il montre qu'il existe une rotation <em>relative</em> entre le sol et l'ensemble des masses de l'univers. Impossible de déterminer « qui tourne » sans un référentiel absolu.</p>
<p><strong>Anomalies documentées :</strong> Maurice Allais (prix Nobel d'économie) a documenté des anomalies dans le comportement du pendule paraconique — des mouvements non expliqués par la rotation terrestre seule, notamment pendant les éclipses solaires. Ces anomalies n'ont jamais été expliquées de manière satisfaisante.</p>
<p><strong>Sensibilité aux perturbations :</strong> le pendule est extrêmement sensible aux courants d'air, à la symétrie du fil, à la forme de la masse, au mode de lancement. De nombreuses reproductions ont donné des résultats incohérents ou variables.</p>`,
    demarche: [
      `Vérifier que la vitesse de rotation mesurée correspond à la formule sin(latitude)`,
      `Documenter les conditions : longueur du fil, masse, amplitude, courants d'air, température`,
      `Mesurer sur une longue durée (24h+) pour vérifier la régularité de la rotation`,
      `Comparer avec un gyroscope de précision au même endroit`,
      `Rechercher les anomalies documentées (effets Allais, éclipses)`,
    ],
    checklist: [
      `La longueur du pendule est-elle suffisante pour minimiser les erreurs ?`,
      `Le point d'attache est-il parfaitement symétrique (pas de direction préférentielle) ?`,
      `Les courants d'air sont-ils contrôlés (enceinte fermée) ?`,
      `La vitesse de rotation mesurée correspond-elle à ω×sin(φ) ?`,
      `L'expérience dure-t-elle assez longtemps pour mesurer plusieurs degrés de rotation ?`,
      `A-t-on documenté d'éventuelles anomalies ou irrégularités ?`,
    ],
    relatedArticle: 'la-rotation-terrestre-deux-experiences-zero-preuve',
  },
  {
    id: 'nivellement-eau-communicants',
    type: 'video',
    category: 'mecanique',
    title: 'Nivellement de l\'eau et vases communicants',
    location: 'Laboratoire, canal, terrain',
    source: 'Physique des fluides fondamentale',
    duration: '~3 min',
    embedUrl: 'https://www.youtube.com/embed/_x3rRM9k_LE',
    observation: `Dans des vases communicants, l'eau trouve toujours le même niveau, quelle que soit la forme des récipients. Sur un canal rectiligne, la surface de l'eau apparaît parfaitement plane. Ce principe est utilisé en topographie (niveau à eau) depuis l'Antiquité. La question : sur de grandes distances, l'eau suit-elle la courbure terrestre ou reste-t-elle plane ?`,
    analyse: `<p>Le principe des vases communicants découle de la <strong>pression hydrostatique</strong> : P = ρgh. À l'équilibre, la pression est la même en tout point connecté → le niveau est le même.</p>
<p>À petite échelle (quelques mètres), la surface de l'eau est effectivement plane à la précision de mesure ordinaire. La courbure terrestre abaisse la surface de ~8 cm/km² (formule approchée pour de petites distances).</p>
<p>À grande échelle, la surface libre de l'eau suit une <strong>équipotentielle gravitationnelle</strong> — elle est perpendiculaire à la direction de la gravité locale. Sur un globe, cette surface est courbe. Sur un plan, elle serait plate.</p>
<p><strong>Le défi expérimental :</strong> mesurer la courbure de la surface de l'eau sur de longues distances est difficile. La réfraction atmosphérique (au-dessus de l'eau, air froid en bas) courbe les rayons lumineux et peut faire apparaître une surface courbe comme plane (ou inversement). Les mesures au laser sur de longs canaux sont perturbées par ces mêmes effets.</p>`,
    demarche: [
      `Mesurer le niveau de l'eau à plusieurs points le long d'un canal rectiligne de grande longueur`,
      `Utiliser un laser et une cible étalonnée pour détecter un éventuel écart par rapport à la planéité`,
      `Documenter les conditions de réfraction (température de l'eau, de l'air à différentes hauteurs)`,
      `Comparer la déviation mesurée avec la déviation attendue par courbure (8 cm par km²)`,
      `Répéter à différents moments de la journée (la réfraction varie avec le gradient thermique)`,
    ],
    checklist: [
      `La distance du canal est-elle suffisante pour que la courbure théorique soit mesurable ?`,
      `Le laser ou l'instrument de mesure est-il calibré et sa divergence connue ?`,
      `Les conditions de réfraction atmosphérique sont-elles documentées ?`,
      `La température de l'eau et de l'air est-elle mesurée à plusieurs hauteurs ?`,
      `A-t-on pris en compte la réfraction dans l'interprétation des résultats ?`,
      `L'expérience a-t-elle été répétée dans des conditions différentes ?`,
    ],
    relatedArticle: 'leau-ne-ment-pas',

  },
  {
    id: 'eclipse-solaire-totale',
    type: 'video',
    category: 'astronomique',
    title: 'Éclipse solaire totale',
    location: 'Zone de totalité (bande étroite sur Terre)',
    source: 'Événement astronomique prévisible avec précision',
    duration: '~5-8 min',
    embedUrl: 'https://www.youtube.com/embed/zD9ryv_QhpY',
    observation: `La Lune passe exactement devant le Soleil, obscurcissant progressivement son disque. Pendant la totalité (2-7 minutes), on voit la couronne solaire, les protubérances, les « perles de Baily ». L'obscurité tombe en plein jour, la température chute, les étoiles et planètes deviennent visibles. La bande de totalité est étroite (~150 km) et prévisible des siècles à l'avance.`,
    analyse: `<p>L'éclipse solaire totale est l'un des phénomènes astronomiques les plus spectaculaires et les plus rigoureusement prévisibles. La coïncidence de taille apparente Soleil/Lune (~0.5°) est remarquable : le Soleil est ~400× plus grand mais aussi ~400× plus loin.</p>
<p>Les éclipses sont prévisibles grâce au <strong>cycle de Saros</strong> (18 ans 11 jours 8 heures) connu depuis l'Antiquité babylonienne. Aujourd'hui, les calculs de mécanique céleste prédisent les éclipses à la seconde et au kilomètre près, des siècles à l'avance.</p>
<p>Cette précision de prédiction est souvent considérée comme une <strong>validation du modèle héliocentrique</strong>. Cependant, historiquement, les éclipses étaient aussi prédites dans le cadre géocentrique (Ptolémée) et même par les cycles empiriques babyloniens sans modèle géométrique.</p>
<p><strong>Question épistémologique :</strong> la capacité à prédire un phénomène prouve-t-elle que le modèle sous-jacent est vrai, ou simplement qu'il est <em>calculatoirement adéquat</em> ? Plusieurs modèles géométriques différents peuvent produire les mêmes prédictions.</p>`,
    demarche: [
      `Vérifier la prédiction : heure de début, durée de totalité, position de la bande — correspondent-elles aux calculs ?`,
      `Mesurer la taille angulaire du Soleil et de la Lune avant et pendant l'éclipse`,
      `Observer les phénomènes spécifiques : perles de Baily, couronne, protubérances, ombre en mouvement`,
      `Documenter la chute de température et de luminosité pendant la totalité`,
      `Comparer les observations depuis plusieurs points de la bande de totalité`,
    ],
    checklist: [
      `L'heure exacte de la totalité correspond-elle à la prédiction (à la seconde) ?`,
      `La position géographique est-elle dans la bande de totalité prédite ?`,
      `La durée de la totalité observée correspond-elle au calcul ?`,
      `A-t-on documenté la couronne et les protubérances (photos) ?`,
      `La taille angulaire apparente de la Lune est-elle mesurée ?`,
      `A-t-on comparé avec les prédictions de plusieurs modèles ?`,
    ],
    relatedArticle: 'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
  },
  {
    id: 'rotation-ciel-etoile',
    type: 'video',
    category: 'astronomique',
    title: 'Rotation apparente du ciel étoilé',
    location: 'Tout lieu à ciel dégagé, nuit sans lune',
    source: 'Observation millénaire, astrophotographie',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/hPJdB7pOk7I',
    observation: `En posant longtemps une caméra vers le nord (hémisphère Nord), les étoiles tracent des cercles concentriques autour de l'étoile Polaire. Le mouvement complet fait 360° en ~23h 56min (jour sidéral). Au Sud, les étoiles tournent autour du pôle céleste sud (pas d'étoile brillante). À l'équateur, les étoiles se déplacent d'est en ouest en lignes parallèles.`,
    analyse: `<p>Ce mouvement apparent a deux explications possibles :</p>
<p><strong>1. La Terre tourne</strong> (modèle standard) : la Terre effectue un tour sur elle-même en 23h 56min. L'axe de rotation pointe vers le pôle céleste nord (près de Polaris). Tout le ciel semble tourner autour de cet axe.</p>
<p><strong>2. Le ciel tourne</strong> (modèle géocentrique) : la sphère céleste (ou l'ensemble des étoiles) tourne autour d'une Terre fixe. C'était le modèle de Ptolémée et d'Aristote, et c'est ce que l'observation directe montre.</p>
<p><strong>Le problème :</strong> l'observation seule ne permet pas de distinguer entre les deux cas — c'est un mouvement <strong>relatif</strong>. Des expériences supplémentaires (Foucault, Coriolis, aberration stellaire) sont invoquées pour trancher, mais chacune a ses nuances et ses objections.</p>
<p>Le jour sidéral (23h 56min 4s) est plus court que le jour solaire (24h) car la Terre avance aussi sur son orbite — en un jour, elle doit tourner un peu plus pour retrouver le Soleil à la même position.</p>`,
    demarche: [
      `Réaliser un timelapse longue pose pointé vers le pôle céleste`,
      `Mesurer la vitesse de rotation apparente (degrés par heure)`,
      `Vérifier que la période est ~23h 56min (pas 24h)`,
      `Observer depuis différentes latitudes : l'angle d'élévation du pôle correspond-il à la latitude ?`,
      `Comparer l'observation nord et sud : les rotations sont-elles en sens opposé ?`,
    ],
    checklist: [
      `Le timelapse couvre-t-il plusieurs heures (idéalement une nuit entière) ?`,
      `Le pôle céleste est-il identifié correctement dans l'image ?`,
      `La vitesse de rotation mesurée est-elle ~15°/heure ?`,
      `L'étoile Polaire est-elle bien au centre des cercles (hémisphère Nord) ?`,
      `Les conditions météo sont-elles suffisantes (ciel dégagé, pas de pollution lumineuse) ?`,
      `La latitude du lieu est-elle vérifiée par rapport à l'élévation du pôle ?`,
    ],
    relatedArticle: 'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
  },
  {
    id: 'retrogradation-mars',
    type: 'video',
    category: 'astronomique',
    title: 'Rétrogradation de Mars — mouvement apparent en boucle',
    location: 'Observable lors des oppositions de Mars (~tous les 2 ans)',
    source: 'Astronomie observationnelle, connue depuis l\'Antiquité',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/hOjrPcD6Iuc',
    observation: `Normalement, Mars se déplace lentement vers l'est par rapport aux étoiles fixes (mouvement direct). Mais périodiquement (~tous les 26 mois), Mars semble s'arrêter, reculer vers l'ouest pendant quelques semaines (mouvement rétrograde), puis reprendre son mouvement normal. Le résultat est une boucle ou un « Z » tracé sur le fond des étoiles.`,
    analyse: `<p>La rétrogradation de Mars a été l'un des grands casse-têtes de l'astronomie antique. Dans le modèle <strong>héliocentrique</strong>, l'explication est simple : la Terre, plus proche du Soleil, tourne plus vite que Mars. Quand la Terre « double » Mars, celle-ci semble reculer par effet de parallaxe — comme un camion doublé sur l'autoroute semble reculer.</p>
<p>Dans le modèle <strong>géocentrique</strong> de Ptolémée, la rétrogradation était expliquée par des <strong>épicycles</strong> — des cercles sur des cercles. Ce système était calculatoirement complexe mais produisait des prédictions correctes.</p>
<p><strong>Point épistémologique important :</strong> Copernic n'a pas « prouvé » l'héliocentrisme — il a montré qu'un modèle plus simple (sans épicycles majeurs) produisait les mêmes résultats. Les deux modèles sont <strong>cinématiquement équivalents</strong> pour les observations à l'œil nu. C'est le rasoir d'Ockham, pas une preuve empirique, qui favorise l'héliocentrisme dans ce cas.</p>`,
    demarche: [
      `Photographier Mars chaque semaine pendant 6 mois autour de l'opposition`,
      `Tracer la trajectoire apparente par rapport aux étoiles fixes de référence`,
      `Mesurer les dates de début et fin de rétrogradation et comparer avec les éphémérides`,
      `Comparer les prédictions du modèle héliocentrique et géocentrique (épicycles) — sont-elles distinguables ?`,
      `Observer d'autres planètes (Jupiter, Saturne) pour vérifier le même phénomène`,
    ],
    checklist: [
      `Les observations couvrent-elles la période complète de rétrogradation ?`,
      `Les étoiles de référence sont-elles identifiées pour tracer le mouvement relatif ?`,
      `Les dates de station (arrêt apparent) correspondent-elles aux éphémérides ?`,
      `La boucle tracée est-elle documentée photographiquement ?`,
      `A-t-on comparé avec les prédictions de plusieurs modèles ?`,
      `Les observations sont-elles faites depuis le même lieu et avec le même matériel ?`,
    ],
    relatedArticle: 'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
  },
  {
    id: 'analemme-solaire',
    type: 'video',
    category: 'astronomique',
    title: 'Analemme solaire — la figure en 8 du Soleil',
    location: 'Tout lieu, photographie sur un an',
    source: 'Astrophotographie et mécanique céleste',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/Deli5COMJhs',
    observation: `Si on photographie le Soleil chaque jour à la même heure depuis le même point pendant un an, les positions forment un 8 (ou une figure asymétrique selon la latitude). Le Soleil n'est pas au même endroit dans le ciel à la même heure d'un jour à l'autre. Les extrémités du 8 correspondent aux solstices, le croisement aux équinoxes.`,
    analyse: `<p>L'analemme résulte de deux effets combinés :</p>
<p><strong>1. L'inclinaison de l'axe terrestre</strong> (~23.4°) : elle fait varier la déclinaison du Soleil au fil de l'année (mouvement nord-sud). C'est ce qui crée l'extension verticale du 8.</p>
<p><strong>2. L'excentricité de l'orbite terrestre</strong> (e ≈ 0.017) : la Terre va plus vite au périhélie (janvier) qu'à l'aphélie (juillet) — loi de Kepler. Le jour solaire varie légèrement (~16 minutes d'avance/retard sur l'année) — c'est l'<strong>équation du temps</strong>. C'est ce qui crée l'extension horizontale et l'asymétrie du 8.</p>
<p>L'analemme est une « empreinte digitale » des paramètres orbitaux. Chaque planète a son propre analemme (celui de Mars est en forme de goutte). Si l'orbite était parfaitement circulaire et l'axe non incliné, l'analemme serait un point.</p>
<p>Ce phénomène est prédit avec une précision totale par la mécanique céleste — c'est un excellent test de cohérence du modèle orbital.</p>`,
    demarche: [
      `Photographier le Soleil à la même heure (heure civile) chaque semaine pendant un an depuis un trépied fixe`,
      `Superposer les images pour tracer la figure en 8`,
      `Comparer la forme obtenue avec le modèle théorique (inclinaison + excentricité)`,
      `Mesurer l'amplitude verticale (liée à l'inclinaison) et horizontale (liée à l'excentricité)`,
      `Vérifier les dates des extrema (solstices) et du croisement (proches des équinoxes)`,
    ],
    checklist: [
      `Les photos couvrent-elles au moins un cycle complet (365 jours) ?`,
      `L'appareil photo est-il fixe (trépied, même position exacte) ?`,
      `L'heure de prise de vue est-elle constante (horloge précise, même heure civile) ?`,
      `Le filtre solaire est-il adapté et constant ?`,
      `La forme obtenue correspond-elle à l'analemme théorique pour cette latitude ?`,
      `A-t-on identifié les dates des extrema et du point central ?`,
    ],
    relatedArticle: 'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
  },
  {
    id: 'vagues-houle-propagation',
    type: 'video',
    category: 'hydrologique',
    title: 'Vagues et houle — propagation sur longue distance',
    location: 'Océan, côtes exposées à la houle',
    source: 'Océanographie physique',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/84W2uhyBUxI',
    observation: `La houle océanique peut voyager des milliers de kilomètres sans perdre beaucoup d'énergie. Des vagues générées par une tempête en Antarctique arrivent sur les côtes californiennes plusieurs jours plus tard. Les vagues ne transportent pas d'eau — elles transportent de l'énergie. Un bouchon flottant monte et descend mais n'avance pas (mouvement orbital).`,
    analyse: `<p>Les vagues de surface sont des <strong>ondes de gravité</strong> — la gravité agit comme force de rappel quand la surface est perturbée. L'eau elle-même effectue des mouvements circulaires (orbitaux) qui diminuent exponentiellement avec la profondeur.</p>
<p>La vitesse de propagation dépend de la longueur d'onde : <code>c = √(gλ/2π)</code> en eau profonde. Les longues longueurs d'onde (houle) voyagent plus vite que les courtes (clapot) → la houle se « trie » en voyageant, arrivant par période croissante.</p>
<p>En eau peu profonde (profondeur < λ/2), la vitesse devient <code>c = √(gh)</code> — elle ne dépend plus de la longueur d'onde mais de la profondeur. C'est pourquoi les vagues ralentissent, se redressent et déferlent à l'approche de la côte.</p>
<p><strong>Point clé :</strong> les vagues démontrent un principe fondamental : une onde peut transporter de l'énergie sur de grandes distances sans transport net de matière. Ce principe s'applique aussi à la lumière et au son.</p>`,
    demarche: [
      `Mesurer la période et la longueur d'onde de la houle à l'arrivée`,
      `Remonter la trajectoire de la houle avec les cartes météo (identifier la tempête source)`,
      `Vérifier que la vitesse de propagation correspond à √(gλ/2π)`,
      `Observer le mouvement d'un flotteur : confirme-t-il le mouvement orbital (pas de transport net) ?`,
      `Comparer le comportement en eau profonde et en zone de déferlement`,
    ],
    checklist: [
      `La période de la houle est-elle mesurée avec précision ?`,
      `La source (tempête) est-elle identifiée sur les cartes météo ?`,
      `Le temps de propagation correspond-il à la vitesse de groupe théorique ?`,
      `A-t-on vérifié l'absence de transport net d'eau (flotteur) ?`,
      `Le comportement en eau peu profonde (déferlement) est-il documenté ?`,
      `Les conditions locales (courants, vent) sont-elles notées ?`,
    ],
    relatedArticle: 'leau-ne-ment-pas',
  },
  {
    id: 'marees-cycle-lunaire',
    type: 'video',
    category: 'hydrologique',
    title: 'Marées',
    location: 'Zones côtières à fort marnage (Mont-Saint-Michel, baie de Fundy)',
    source: 'Océanographie, mécanique céleste',
    duration: '~5 min',
        observation: `Le niveau de la mer monte et descend environ deux fois par jour (~12h 25min entre deux marées hautes). L'amplitude varie avec les phases lunaires : grandes marées aux nouvelles et pleines lunes (vives-eaux), petites marées aux quartiers (mortes-eaux). Le marnage varie de quelques centimètres (Méditerranée) à plus de 15 mètres (baie de Fundy).`,
    analyse: `<p>Les marées sont souvent présentées comme une preuve évidente de la gravitation newtonienne. Pourtant, une analyse rigoureuse des données officielles (NOAA, SHOM, TPXO) révèle des contradictions profondes.</p>
<p><strong>Le paradoxe gravitationnel :</strong> le Soleil est 27 millions de fois plus massif que la Lune et exerce une force gravitationnelle 177 fois supérieure. Pourtant, l'influence lunaire sur les marées est 2,3 fois supérieure à celle du Soleil. La réponse officielle (gradient en 1/d³) ne résout pas le problème de la force centrifuge solaire.</p>
<p><strong>Les renflements n'existent pas :</strong> la théorie prédit deux renflements océaniques permanents se déplaçant avec la Lune. Aucune mesure directe n'a jamais détecté ces renflements. Les cartes officielles montrent des marées contrôlées par des <strong>points amphidromiques</strong> locaux, avec des amplitudes et directions complètement variables.</p>
<p><strong>Le décalage de 45° :</strong> les marées de vives eaux ne se produisent pas directement sous la Lune lors de l'alignement, mais avec un décalage d'environ 45° — cohérent avec une interaction électromagnétique perpendiculaire, pas avec la gravité.</p>
<p><strong>Prédiction sans gravité :</strong> la méthode réelle de prédiction (analyse harmonique) décompose les données historiques en constituants sinusoïdaux. Elle n'utilise ni la constante G, ni la masse de la Lune, ni le modèle héliocentrique. Elle fonctionne parce que les marées sont <strong>cycliques</strong> — pas parce qu'on comprend leur cause.</p>`,
    demarche: [
      `Mesurer le niveau d'eau à intervalles réguliers pendant au moins un mois`,
      `Corréler les maxima avec les phases lunaires et la position du Soleil`,
      `Comparer les marées observées avec les prédictions des tables de marées officielles`,
      `Mesurer en plusieurs lieux côtiers pour observer les différences de marnage et de phase`,
      `Documenter les marées exceptionnelles (tempêtes, surcotes) et les comparer au modèle`,
    ],
    checklist: [
      `Les mesures couvrent-elles au moins un cycle lunaire complet (29.5 jours) ?`,
      `La corrélation avec les phases lunaires est-elle claire ?`,
      `Les prédictions des tables de marées sont-elles vérifiées ?`,
      `Le délai entre le passage de la Lune au méridien et la marée haute est-il mesuré ?`,
      `Les variations saisonnières (équinoxes) sont-elles documentées ?`,
      `A-t-on noté les conditions météo (pression, vent) qui modifient le niveau ?`,
    ],
    relatedArticle: 'les-marees-contre-lheliocentrisme',

  },
  {
    id: 'tsunami-propagation-profondeur',
    type: 'video',
    category: 'hydrologique',
    title: 'Tsunami — propagation en eau profonde vs peu profonde',
    location: 'Océan Pacifique, zones de subduction',
    source: 'Sismologie et océanographie',
    duration: '~5 min',
    embedUrl: 'https://www.youtube.com/embed/aB9BmM7y4dI',
    observation: `Un tsunami en plein océan est presque invisible : une vague de quelques dizaines de centimètres de haut, avec une longueur d'onde de 100-200 km, se déplaçant à 700-800 km/h. Mais en approchant de la côte, l'eau ralentit (profondeur diminue), la longueur d'onde se raccourcit, et la hauteur augmente dramatiquement — jusqu'à 30 mètres dans les cas extrêmes.`,
    analyse: `<p>Un tsunami est une <strong>onde de gravité en eau peu profonde</strong> à très grande longueur d'onde. Sa vitesse est <code>c = √(gh)</code>, où h est la profondeur. En plein océan (h ≈ 4000m) : c ≈ 200 m/s ≈ 720 km/h.</p>
<p>Comme la <strong>longueur d'onde</strong> (100-200 km) est bien plus grande que la profondeur, l'onde « touche le fond » même en plein océan — c'est une onde d'eau peu profonde malgré la profondeur.</p>
<p>Le <strong>shoaling</strong> (amplification côtière) résulte de la conservation de l'énergie : quand la profondeur diminue, la vitesse diminue, et comme l'énergie doit être conservée, l'amplitude augmente. La formule approchée est : h₂/h₁ ≈ (d₁/d₂)^(1/4).</p>
<p>Le temps d'arrivée d'un tsunami est prévisible avec une grande précision grâce à la bathymétrie (carte des profondeurs) et à la formule c = √(gh). Les systèmes d'alerte se basent sur ce calcul.</p>`,
    demarche: [
      `Analyser les données sismiques : magnitude, profondeur, mécanisme (subduction, effondrement)`,
      `Calculer le temps de propagation avec la formule c = √(gh) et la bathymétrie`,
      `Comparer le temps d'arrivée calculé avec l'observation réelle (marégraphes)`,
      `Mesurer l'amplification côtière et comparer avec le modèle de shoaling`,
      `Documenter la hauteur maximale (run-up) et la distance d'inondation`,
    ],
    checklist: [
      `La source sismique est-elle bien caractérisée (magnitude, localisation, profondeur) ?`,
      `Le temps de propagation calculé correspond-il aux observations des marégraphes ?`,
      `L'amplification côtière est-elle cohérente avec la bathymétrie locale ?`,
      `Les données des bouées DART (capteurs de fond) sont-elles disponibles ?`,
      `Le run-up mesuré est-il documenté par des relevés de terrain ?`,
      `A-t-on comparé avec les simulations numériques ?`,
    ],
    relatedArticle: 'leau-ne-ment-pas',
  },
  {
    id: 'foudre-decharge-electrique',
    type: 'video',
    category: 'electromagnetique',
    title: 'Foudre — décharge électrique entre nuage et sol',
    location: 'Orage, zones à forte activité orageuse',
    source: 'Physique de l\'atmosphère, électricité atmosphérique',
    duration: '~4 min',
    embedUrl: 'https://www.youtube.com/embed/qQKhIK4pvYo',
    observation: `Un éclair illumine le ciel en une fraction de seconde. Au ralenti, on découvre un processus complexe : un « traceur par pas » (stepped leader) descend du nuage, invisible à l'œil nu, par bonds de 50-100m. Quand il approche du sol, un arc de retour (return stroke) remonte à ~100 000 km/s — c'est le flash visible. Le tonnerre arrive avec un délai (~3s/km).`,
    analyse: `<p>La foudre est une <strong>décharge électrique</strong> géante. Dans un cumulonimbus, la séparation de charges crée des potentiels de centaines de millions de volts. Le champ électrique finit par dépasser la rigidité diélectrique de l'air (~3 MV/m) → claquage.</p>
<p>Le processus en deux temps est remarquable : (1) le <strong>traceur par pas</strong> ionise un canal dans l'air (courant ~200A, peu lumineux, vitesse ~200 km/s). (2) Quand il atteint le sol (ou un streamer montant), le <strong>coup de retour</strong> remonte le canal ionisé avec un courant de ~30 000A et une température de ~30 000 K → c'est le flash aveuglant.</p>
<p>Le <strong>tonnerre</strong> est causé par la dilatation explosive de l'air chauffé à 30 000 K (5× la surface du Soleil). L'onde de choc se transforme en onde sonore. Le délai son/lumière permet d'estimer la distance (vitesse du son ~340 m/s).</p>
<p>La Terre subit ~100 éclairs par seconde. La foudre maintient le <strong>circuit électrique global</strong> atmosphérique — les orages rechargent en permanence la différence de potentiel entre l'ionosphère et le sol (~300 kV).</p>`,
    demarche: [
      `Filmer en haute vitesse (1000+ fps) pour décomposer le traceur et le coup de retour`,
      `Mesurer le délai tonnerre/éclair pour estimer la distance`,
      `Utiliser un détecteur de champ électrique pour mesurer les variations pendant l'orage`,
      `Analyser le spectre lumineux de l'éclair (raies d'azote, oxygène ionisé)`,
      `Documenter les conditions météo : type de nuage, température, humidité, vent`,
    ],
    checklist: [
      `La vidéo au ralenti montre-t-elle clairement la séquence traceur/coup de retour ?`,
      `La distance de l'éclair est-elle estimée (délai tonnerre/éclair) ?`,
      `Les conditions météo sont-elles documentées ?`,
      `La luminosité et les couleurs sont-elles cohérentes avec une décharge électrique dans l'air ?`,
      `A-t-on détecté le champ électrique au sol pendant l'orage ?`,
      `La vidéo est-elle prise en sécurité (distance suffisante, abri) ?`,
    ],
    relatedArticle: 'magnetisme-et-electromagnetisme',
  },
];
