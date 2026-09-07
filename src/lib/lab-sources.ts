/**
 * lab-sources.ts — Les provenances courantes, en un clic.
 *
 * POURQUOI DES RACCOURCIS PLUTÔT QU'UNE ATTESTATION GLOBALE
 * ─────────────────────────────────────────────────────────
 * Deux voies étaient possibles pour alléger la saisie : ces raccourcis, ou une
 * case unique en bas de formulaire — « j'atteste avoir vérifié les sources ».
 *
 * La case produirait UN SEUL BIT pour tout le formulaire. L'analyste qui
 * rouvrirait le dossier six mois plus tard y lirait « l'opérateur a coché une
 * case » — c'est-à-dire précisément ce dont on a établi que ça ne vaut rien :
 * ce n'est pas parce que quelque chose est mentionné que c'est vrai.
 *
 * Un raccourci conserve autre chose : la NATURE de la provenance. Savoir que D
 * vient d'un calcul géodésique, que h_obs vient d'un relevé terrain et que la
 * focale vient de l'EXIF ne garantit rien non plus — mais dit à l'analyste ce
 * qu'il doit aller vérifier, et par quel moyen. Une altitude IGN se recontrôle
 * sur le Géoportail en trente secondes ; une altitude « mesurée au terrain » se
 * recontrôle en relisant le carnet de terrain. Ce n'est pas la même démarche,
 * et c'est cette information-là qui est utile.
 *
 * Accessoirement, c'est aussi plus rapide qu'une case : ce qui prend du temps
 * dans un champ de source, c'est de taper la typologie, pas de cocher.
 *
 * Chaque libellé est rédigé pour ne rien affirmer de plus que sa nature. Aucun
 * ne dit « vérifié ».
 */

export interface RaccourciSource {
  /** Ce qui s'affiche sur le bouton. Court : il y en a plusieurs par champ. */
  cle: string;
  /** Ce qui est écrit dans le champ. Dit la nature, jamais la fiabilité. */
  texte: string;
  /** Infobulle : ce que ce choix veut dire, et ce qu'il ne dit pas. */
  aide: string;
}

export const RACCOURCIS_SOURCE: RaccourciSource[] = [
  {
    cle: 'EXIF',
    texte: 'EXIF du fichier — déclaratif appareil, non vérifié',
    aide: 'Ce que l’appareil a écrit dans le fichier. Une métadonnée s’écrit et se modifie : c’est une déclaration, pas une attestation.',
  },
  {
    cle: 'IGN / Géoportail',
    texte: 'IGN — Géoportail / RGE ALTI, consulté par l’opérateur',
    aide: 'Donnée altimétrique ou planimétrique de l’IGN. Recontrôlable sur le Géoportail : notez la date de consultation si le dossier doit tenir dans le temps.',
  },
  {
    cle: 'SHOM / carte marine',
    texte: 'SHOM — carte marine ou fiche d’ouvrage',
    aide: 'Documentation maritime officielle : phares, amers, sondes, marées.',
  },
  {
    cle: 'Fiche technique',
    texte: 'Fiche technique du constructeur ou de l’ouvrage',
    aide: 'Documentation du fabricant, plan coté, notice. Ne dit rien de l’état réel de l’objet au moment de la vue.',
  },
  {
    cle: 'Mesure terrain',
    texte: 'Mesure faite au terrain par l’opérateur',
    aide: 'Relevé de l’opérateur, au mètre, au télémètre ou au niveau. Sa traçabilité repose sur le carnet de terrain, qui doit exister.',
  },
  {
    cle: 'Relevé GNSS',
    texte: 'Relevé GNSS sur site, incertitude annoncée par le récepteur',
    aide: 'Position satellitaire relevée au poste. L’incertitude à déclarer est celle qu’affiche le récepteur, jamais une valeur de catalogue.',
  },
  {
    cle: 'Calcul',
    texte: 'Calculé depuis d’autres grandeurs de cette fiche',
    aide: 'Valeur dérivée. Elle vaut ce que valent les grandeurs dont elle sort : ce sont elles qui restent à établir.',
  },
];

/**
 * L'avertissement qui accompagne les raccourcis, partout où ils sont proposés.
 * Un bouton pratique ne doit pas laisser croire qu'il atteste de quelque chose.
 */
export const AVERTISSEMENT_RACCOURCIS =
  'Un raccourci écrit la NATURE de la provenance, jamais sa fiabilité. Rien dans '
  + 'cet outil ne vérifie qu’une fiche d’ouvrage dit ce qu’on lui fait dire : '
  + 'c’est à l’analyste de l’établir, et savoir par quel moyen lui fait gagner '
  + 'le temps que ce bouton vous fait gagner.';
