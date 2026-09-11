/**
 * verifier-formule-seuil.mjs — La règle du seuil se dit EN ENTIER, partout.
 *
 * LA RÈGLE
 * ────────
 *   Une visée est discriminante quand la courbure masque au moins 10 % de la
 *   hauteur de la cible, EN PARTANT DE SA BASE.
 *
 * Les deux moitiés vont ensemble : le point de départ est la BASE, le
 * dénominateur est la HAUTEUR TOTALE de la cible. Écrire « 10 % de la hauteur
 * de la cible » tout court tait d'où l'on compte, et décrit une autre mesure
 * que celle que l'outil fait — c'est le pied qui disparaît en premier sous
 * l'horizon, et c'est là que les deux modèles divergent en premier.
 *
 * Le défaut ne casse rien, ne lève rien, et se lit comme une phrase correcte.
 * Il s'est produit dans une prose de présentation alors que le code, lui,
 * énonçait la règle entière. D'où ce contrôle : il porte sur les TEXTES, pas
 * sur le calcul.
 *
 *     node scripts/verifier-formule-seuil.mjs
 *
 * COMMENT IL DÉCOUPE
 * ──────────────────
 * Une unité de texte = une ligne de source, sauf continuation évidente : une
 * ligne qui commence par « + », ou une ligne qui commence par un guillemet
 * quand la précédente en finit un sans virgule (concaténation implicite de
 * Python). Sans ce découpage fin, la valeur « 10 % de la hauteur de la cible »
 * d'un couple clé/valeur serait absoute par la ligne voisine qui, elle,
 * mentionne la base — et le contrôle ne servirait à rien.
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = dirname(dirname(fileURLToPath(import.meta.url)));

/**
 * Ce qui est examiné : tout ce qui finit devant un lecteur — les textes de
 * l'interface, les articles, les motifs du paquet de référence, les README.
 */
const DOSSIERS = [
  'src',
  'content/articles',
  'outils/outil-A-visee-optique/visee_optique',
];
const FICHIERS = ['outils/README.md'];

/**
 * Ce qui est ÉCARTÉ, et pourquoi. Une exclusion qu'on ne peut pas lire ne peut
 * pas être contestée.
 */
const EXCLUS = [
  // Un SECOND seuil de 10 % existe sur le site, et il n'a rien à voir : c'est
  // l'écart maximal entre les deux modèles sur les paires du réseau de noyaux.
  // Lui appliquer la règle de la base produirait une phrase fausse.
  ['content/reseau', 'autre seuil de 10 % — écart entre modèles sur les paires du réseau'],
  // Les vecteurs d'or sont ENGENDRÉS depuis le paquet Python : les examiner
  // signalerait deux fois le même défaut, et le corriger à la main serait
  // exactement ce que leur avertissement interdit.
  ['vecteurs-or', 'fichier engendré, la source est le paquet Python'],
  // CLAUDE.md et ce script CITENT les formulations interdites pour les
  // interdire. Les contrôler retournerait la règle contre ses propres énoncés.
  ['CLAUDE.md', 'énonce la règle et cite les formes fautives pour les proscrire'],
  ['verifier-formule-seuil.mjs', 'idem'],
];

/**
 * L'EMPREINTE d'un énoncé de la règle : un POURCENTAGE RAPPORTÉ À LA HAUTEUR
 * DE LA CIBLE. C'est cette tournure-là, et elle seule, qui doit dire d'où l'on
 * compte.
 *
 * Une première version déclenchait sur « seuil », « discriminante » ou
 * « hauteur de la cible » pris isolément, avec un chiffre quelque part. Elle
 * levait dix-huit signalements dont seize faux : l'AUTRE seuil de 10 % du site
 * — l'écart entre modèles sur les paires du réseau, qui ne parle d'aucune
 * base — et les étiquettes de schémas SVG. Un contrôle qui crie à tort finit
 * par être désactivé, ce qui est pire que pas de contrôle.
 */
const DECLENCHE = [
  /%\s*(?:de la|de sa|de)\s+hauteur/i,
  /hauteur de la cible[^.]{0,30}%/i,
  // « fraction MASQUÉE » seulement. « La fraction de la hauteur de la cible qui
  // reste VISIBLE » est l'observable du protocole — une autre grandeur, qui se
  // passe d'ancrage puisqu'elle ne désigne pas l'occultation. L'exiger là
  // aurait signalé une phrase juste, et un contrôle qui crie à tort finit
  // désactivé.
  /fraction\s+masqu\w+/i,
];
/** Un pourcentage doit être en jeu : sans lui, ce n'est pas le seuil. */
const CHIFFRE = [/%/, /\bfraction\b/i];
/** Ce qui suffit à dire d'où l'on compte. */
const ANCRE = [/\bbase\b/i, /\bpied\b/i];

function fichiers(dir) {
  const out = [];
  const explorer = (d) => {
    for (const e of readdirSync(d)) {
      const p = join(d, e);
      if (statSync(p).isDirectory()) { explorer(p); continue; }
      if (['.ts', '.tsx', '.py', '.md', '.json'].includes(extname(p))) out.push(p);
    }
  };
  explorer(join(RACINE, dir));
  return out;
}

/** Le texte lisible d'un fichier, et la ligne d'origine de chaque unité. */
function unites(chemin) {
  let brut = readFileSync(chemin, 'utf8');

  // Un article range sa prose dans `htmlBody` : on la sort du JSON et on la
  // dépouille de ses balises, sinon rien n'est lu.
  if (extname(chemin) === '.json') {
    let d;
    try { d = JSON.parse(brut); } catch { return []; }
    const corps = typeof d.htmlBody === 'string' ? d.htmlBody : '';
    if (!corps) return [];
    const texte = corps
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&[a-z]+;|&#\d+;/gi, ' ');
    // Une phrase par unité : l'article est de la prose continue.
    return texte.split(/(?<=[.!?])\s+/)
      .map((t) => ({ ligne: 0, texte: t.replace(/\s+/g, ' ').trim() }))
      .filter((u) => u.texte);
  }

  // Le Markdown replie sa prose : une phrase y court sur plusieurs lignes, et
  // la découper ligne à ligne coupait « masque au moins 10 % » de « de la
  // hauteur de la cible en partant de sa base ». Aucun des deux morceaux ne
  // déclenchait, et la règle raccourcie passait — c'est une rupture délibérée
  // qui l'a montré, pas une relecture. Les paragraphes sont donc rejoints,
  // puis découpés en phrases.
  if (extname(chemin) === '.md') {
    const out = [];
    let debut = 1;
    let tampon = [];
    const vider = () => {
      if (tampon.length === 0) return;
      const texte = tampon.join(' ').replace(/\s+/g, ' ').trim();
      for (const phrase of texte.split(/(?<=[.!?])\s+/)) {
        if (phrase.trim()) out.push({ ligne: debut, texte: phrase.trim() });
      }
      tampon = [];
    };
    brut.split('\n').forEach((l, i) => {
      if (l.trim() === '') { vider(); return; }
      if (tampon.length === 0) debut = i + 1;
      tampon.push(l.trim());
    });
    vider();
    return out;
  }

  const lignes = brut.split('\n');
  const out = [];
  for (let i = 0; i < lignes.length; i++) {
    const l = lignes[i];
    const t = l.trim();
    if (!t) continue;
    const precedent = out[out.length - 1];
    const continuation = precedent !== undefined && (
      t.startsWith('+')
      || (/^['"`]/.test(t) && /['"`]$/.test(precedent.derniere.trim()))
    );
    if (continuation) {
      precedent.texte += ` ${t}`;
      precedent.derniere = l;
    } else {
      out.push({ ligne: i + 1, texte: t, derniere: l });
    }
  }

  // Le balisage sort du texte : les guillemets, les accents graves, les
  // concaténations et les expressions JSX ne sont pas de la prose.
  return out.map((u) => ({
    ligne: u.ligne,
    texte: u.texte
      .replace(/\$\{[^{}]*\}/g, ' ')
      .replace(/\{[^{}]*\}/g, ' ')
      .replace(/[`'"]/g, ' ')
      .replace(/\s\+\s/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  })).filter((u) => u.texte);
}

const exclu = (p) => EXCLUS.find(([motif]) => p.includes(motif));

const cibles = [
  ...DOSSIERS.flatMap(fichiers),
  ...FICHIERS.map((f) => join(RACINE, f)),
].filter((p) => {
  if (exclu(p)) return false;
  // Les tests énoncent des cas, pas la règle publique : ils citent « 10 % pile
  // passe » pour décrire une borne, et l'ancrage y serait du bruit.
  if (p.includes('/tests/')) return false;
  return true;
});

const fautes = [];
let examinees = 0;

for (const chemin of cibles) {
  for (const u of unites(chemin)) {
    const declenche = DECLENCHE.some((r) => r.test(u.texte))
      && CHIFFRE.some((r) => r.test(u.texte));
    if (!declenche) continue;
    examinees += 1;
    if (ANCRE.some((r) => r.test(u.texte))) continue;
    fautes.push({
      fichier: relative(RACINE, chemin),
      ligne: u.ligne,
      texte: u.texte.length > 220 ? `${u.texte.slice(0, 220)}…` : u.texte,
    });
  }
}

if (fautes.length > 0) {
  console.error(
    `\n✗ La règle du seuil est énoncée sans dire d'où l'on compte : `
    + `${fautes.length} énoncé(s) sur ${examinees} examiné(s).\n`,
  );
  for (const f of fautes) {
    console.error(`  ${f.fichier}${f.ligne ? `:${f.ligne}` : ''}`);
    console.error(`    ${f.texte}\n`);
  }
  console.error(
    '  La règle se dit EN ENTIER : « au moins 10 % de la hauteur de la cible,\n'
    + '  EN PARTANT DE SA BASE ». Le point de départ est la base, le\n'
    + '  dénominateur est la hauteur totale — les deux dans la même phrase.\n',
  );
  process.exitCode = 1;
} else {
  console.log(
    `✓ Formule du seuil : ${examinees} énoncé(s) examiné(s) dans `
    + `${cibles.length} fichiers, tous ancrés sur la base.`,
  );
  for (const [motif, raison] of EXCLUS) {
    console.log(`  écarté — ${motif} : ${raison}`);
  }
}
