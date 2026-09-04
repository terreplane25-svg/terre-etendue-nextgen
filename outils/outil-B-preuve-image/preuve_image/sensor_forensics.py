"""
sensor_forensics.py — bruit de photosite (PRNU) et niveau d'erreur de compression (ELA).

Ce module sort du périmètre du protocole « Portion visible d'une cible éloignée
au-dessus de la mer » (qui ne traite ni de l'un ni de l'autre) : il s'appuie sur
la littérature générale de l'expertise d'image numérique, et cite ses sources au
lieu de leur inventer des numéros de section.

Deux techniques, deux limites documentées à chaque fonction qui les met en œuvre :

  - PRNU (Photo Response Non-Uniformity) : chaque capteur laisse dans ses images
    une empreinte de bruit fixe, due aux irrégularités de fabrication des
    photosites (Lukáš, Fridrich & Goljan, « Digital camera identification from
    sensor pattern noise », IEEE T-IFS 2006). Ce module en implémente une
    version simplifiée et le dit explicitement (voir debruiter_ondelettes) —
    ce n'est pas le pipeline complet de l'article de référence.
  - ELA (Error Level Analysis) : réenregistrer une image JPEG à une qualité
    connue et comparer le résultat à l'original révèle des écarts de niveau
    d'erreur de compression, popularisé par Neal Krawetz (« A Picture's Worth »,
    Black Hat 2007/2008). Une carte ELA n'est qu'un indice à examiner, jamais
    une preuve autonome — voir AVERTISSEMENT_ELA.

Ni l'une ni l'autre ne conclut seule à une manipulation : ce module calcule des
statistiques et les documente, il ne rend pas de verdict (cf. la même retenue
que le §28.3, différé, dans visee_optique).

Dépendances tierces assumées : NumPy (calcul), Pillow (décodage/réencodage
JPEG) et PyWavelets (transformée en ondelettes). Contrairement au lecteur
EXIF/TIFF de metadata.py — un format d'étiquettes simple, qu'il valait la peine
d'écrire à la main pour un usage probatoire — ré-écrire un codec JPEG ou une
transformée en ondelettes ici serait hors de proportion : ce module écrit et
documente entièrement la logique d'expertise (filtrage, corrélation, seuils,
interprétation), et délègue seulement les primitives de traitement du signal
à des bibliothèques établies et vérifiables.
"""

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

import numpy as np
import pywt
from PIL import Image
from scipy.ndimage import uniform_filter

__all__ = [
    "SensorForensicsError",
    "charger_luminance",
    "debruiter_ondelettes",
    "residu_bruit",
    "EmpreinteCapteur",
    "calculer_empreinte",
    "correlation_normalisee",
    "ResultatPic",
    "pic_correlation",
    "SEUIL_PCE_CITE_LITTERATURE",
    "interpreter_pce",
    "FORMATS_ELA_APPLICABLES",
    "AVERTISSEMENT_ELA",
    "verifier_applicable_ela",
    "recompresser_jpeg",
    "ResultatELA",
    "carte_ela",
    "intensite_zone",
]


class SensorForensicsError(ValueError):
    """Domaine invalide, images incompatibles, ou méthode inapplicable à la source fournie."""


# --- chargement ---


def charger_luminance(chemin_ou_donnees: Union[str, Path, bytes]) -> np.ndarray:
    """Charge une image en niveaux de gris (conversion PIL « L »), en float64.

    Simplification assumée : la littérature PRNU traite parfois chaque canal
    séparément (ou le seul canal vert, moins bruité par le dématriçage) pour un
    meilleur rapport signal/bruit ; ce module travaille en luminance globale.
    """
    try:
        if isinstance(chemin_ou_donnees, (bytes, bytearray)):
            image = Image.open(io.BytesIO(chemin_ou_donnees))
        else:
            image = Image.open(chemin_ou_donnees)
        with image:
            return np.asarray(image.convert("L"), dtype=np.float64)
    except SensorForensicsError:
        raise
    except Exception as exc:  # decodage Pillow, fichier absent, format non reconnu…
        raise SensorForensicsError(f"Image illisible : {exc}") from exc


# --- PRNU : extraction du bruit de capteur ---

_ONDELETTE_PAR_DEFAUT = "db8"
_NIVEAUX_PAR_DEFAUT = 4


def _estimer_sigma_bruit(coeffs_diagonaux_fins: np.ndarray) -> float:
    """Estimateur MAD de l'écart-type du bruit (Donoho, 1995) sur la sous-bande
    diagonale la plus fine — la moins porteuse de contenu de l'image."""
    return float(np.median(np.abs(coeffs_diagonaux_fins)) / 0.6745)


def _wiener_local(coefficient: np.ndarray, sigma_bruit2: float, taille_fenetre: int = 3) -> np.ndarray:
    variance_locale = uniform_filter(coefficient**2, size=taille_fenetre)
    gain = np.maximum(variance_locale - sigma_bruit2, 0.0) / np.maximum(variance_locale, 1e-12)
    return coefficient * gain


def debruiter_ondelettes(
    image: np.ndarray, ondelette: str = _ONDELETTE_PAR_DEFAUT, niveaux: int = _NIVEAUX_PAR_DEFAUT
) -> np.ndarray:
    """Filtre de débruitage en domaine d'ondelettes, inspiré de Lukáš, Fridrich & Goljan (2006).

    Version simplifiée de l'article de référence, assumée comme telle : une seule taille
    de fenêtre pour l'estimation de la variance locale (l'article combine plusieurs tailles
    par un minimum ponctuel), et une variance de bruit estimée une fois sur la sous-bande
    diagonale la plus fine puis appliquée à toutes les échelles. Le résultat isole une
    approximation du contenu de la scène ; le résidu (image − ce résultat, voir
    residu_bruit) est l'estimation du bruit de capteur, dans lequel le PRNU est noyé.
    """
    if image.ndim != 2:
        raise SensorForensicsError("debruiter_ondelettes attend une image en niveaux de gris (2D).")
    coeffs = pywt.wavedec2(image, ondelette, level=niveaux)
    sigma_bruit2 = _estimer_sigma_bruit(coeffs[1][2]) ** 2  # cD du niveau le plus fin
    coeffs_filtres = [coeffs[0]]
    for cH, cV, cD in coeffs[1:]:
        coeffs_filtres.append(
            (
                _wiener_local(cH, sigma_bruit2),
                _wiener_local(cV, sigma_bruit2),
                _wiener_local(cD, sigma_bruit2),
            )
        )
    reconstruite = pywt.waverec2(coeffs_filtres, ondelette)
    return reconstruite[: image.shape[0], : image.shape[1]]


def residu_bruit(
    image: np.ndarray, ondelette: str = _ONDELETTE_PAR_DEFAUT, niveaux: int = _NIVEAUX_PAR_DEFAUT
) -> np.ndarray:
    """Résidu de bruit = image − version débruitée (le PRNU y est noyé avec le bruit
    thermique et de lecture ; c'est pourquoi une seule image ne suffit jamais — voir
    calculer_empreinte)."""
    return image - debruiter_ondelettes(image, ondelette, niveaux)


@dataclass(frozen=True, eq=False)
class EmpreinteCapteur:
    """Empreinte de capteur : moyenne de résidus de bruit sur plusieurs images
    connues du même appareil, à la même résolution (aucun redimensionnement :
    le PRNU est un motif spatial fixe, le déformer invaliderait la comparaison).
    """

    motif: np.ndarray
    n_images: int
    source: str

    def __post_init__(self):
        if self.n_images < 2:
            raise SensorForensicsError("Une empreinte de capteur exige au moins deux images sources.")
        if not self.source or not self.source.strip():
            raise SensorForensicsError("La source de l'empreinte (appareil, lot d'images) doit être documentée.")

    @property
    def fiabilite(self) -> str:
        """Appréciation qualitative de n_images — un usage de la littérature (Lukáš,
        Fridrich & Goljan, 2006), pas un seuil du protocole d'observation."""
        if self.n_images < 20:
            return (
                f"faible ({self.n_images} images) : la littérature recommande généralement "
                "au moins une vingtaine d'images pour une empreinte stable"
            )
        if self.n_images < 50:
            return (
                f"correcte ({self.n_images} images), mais en dessous du nombre couramment "
                "recommandé (~50) pour une empreinte de référence"
            )
        return f"conforme à la pratique usuelle ({self.n_images} images ≥ 50)"


def calculer_empreinte(residus: Sequence[np.ndarray], source: str) -> EmpreinteCapteur:
    """Moyenne des résidus de plusieurs images : le contenu de scène et le bruit
    non fixe (thermique, de lecture) tendent vers zéro par moyennage, le motif
    fixe du capteur (PRNU) reste."""
    if len(residus) < 2:
        raise SensorForensicsError("Au moins deux résidus sont nécessaires pour calculer une empreinte.")
    forme = residus[0].shape
    for residu in residus:
        if residu.shape != forme:
            raise SensorForensicsError(
                "Toutes les images sources d'une empreinte doivent avoir les mêmes dimensions."
            )
    motif = np.mean(np.stack(residus), axis=0)
    return EmpreinteCapteur(motif=motif, n_images=len(residus), source=source)


# --- corrélation et détection ---


def correlation_normalisee(a: np.ndarray, b: np.ndarray) -> float:
    """Corrélation croisée normalisée (coefficient de Pearson 2D), à décalage nul."""
    if a.shape != b.shape:
        raise SensorForensicsError("Les deux signaux doivent avoir les mêmes dimensions.")
    a0 = a - a.mean()
    b0 = b - b.mean()
    norme = np.linalg.norm(a0) * np.linalg.norm(b0)
    if norme == 0:
        raise SensorForensicsError("Corrélation indéfinie : au moins un des deux signaux est constant.")
    return float(np.sum(a0 * b0) / norme)


@dataclass(frozen=True)
class ResultatPic:
    """Résultat d'une recherche de pic de corrélation 2D (§ voir pic_correlation)."""

    decalage: Tuple[int, int]
    valeur_pic: float
    pce: float


def pic_correlation(residu: np.ndarray, empreinte: np.ndarray, rayon_exclusion: int = 5) -> ResultatPic:
    """Corrélation croisée 2D par FFT et rapport pic/énergie (PCE), d'après Goljan,
    Fridrich & Filler, « Managing a Large Database of Camera Fingerprints » (2009).

    Cherche le meilleur alignement entre le résidu et l'empreinte plutôt que de
    supposer une correspondance pixel à pixel : un recadrage de quelques pixels ne
    doit pas, à tort, faire chuter une corrélation qui serait sinon significative.
    Le PCE rapporte l'énergie du pic à l'énergie moyenne du reste de la surface de
    corrélation (un voisinage de rayon_exclusion autour du pic en est exclu) — une
    mesure plus robuste aux faux pics qu'une simple corrélation à décalage nul.
    """
    if residu.shape != empreinte.shape:
        raise SensorForensicsError("Le résidu et l'empreinte doivent avoir les mêmes dimensions.")
    a = residu - residu.mean()
    b = empreinte - empreinte.mean()
    normalisation = np.linalg.norm(a) * np.linalg.norm(b)
    if normalisation == 0:
        raise SensorForensicsError("Corrélation indéfinie : au moins un des deux signaux est constant.")

    correlation = np.fft.ifft2(np.fft.fft2(a) * np.conj(np.fft.fft2(b))).real / normalisation

    idx_pic = np.unravel_index(np.argmax(np.abs(correlation)), correlation.shape)
    valeur_pic = float(correlation[idx_pic])
    hauteur, largeur = correlation.shape
    dy = idx_pic[0] if idx_pic[0] <= hauteur // 2 else idx_pic[0] - hauteur
    dx = idx_pic[1] if idx_pic[1] <= largeur // 2 else idx_pic[1] - largeur

    masque = np.ones_like(correlation, dtype=bool)
    y0, y1 = max(0, idx_pic[0] - rayon_exclusion), min(hauteur, idx_pic[0] + rayon_exclusion + 1)
    x0, x1 = max(0, idx_pic[1] - rayon_exclusion), min(largeur, idx_pic[1] + rayon_exclusion + 1)
    masque[y0:y1, x0:x1] = False
    if not masque.any():
        raise SensorForensicsError("Rayon d'exclusion trop grand : aucune énergie hors-pic disponible.")
    energie_hors_pic = float(np.mean(correlation[masque] ** 2))
    if energie_hors_pic == 0:
        raise SensorForensicsError("Énergie hors-pic nulle : PCE indéfini pour ce signal dégénéré.")

    pce = valeur_pic**2 / energie_hors_pic
    return ResultatPic(decalage=(int(dy), int(dx)), valeur_pic=valeur_pic, pce=pce)


SEUIL_PCE_CITE_LITTERATURE = 60.0  # Goljan, Fridrich & Filler (2009)


def interpreter_pce(pce: float) -> str:
    """Replace une valeur de PCE à côté du seuil de 60 couramment cité dans Goljan,
    Fridrich & Filler (2009) — jamais un verdict : ce seuil a été établi pour une
    taille d'image et un contexte de recherche en base donnés, il ne remplace pas
    une calibration propre au cas, et aucune des deux directions n'est concluante
    seule.
    """
    if pce >= SEUIL_PCE_CITE_LITTERATURE:
        return (
            f"PCE = {pce:.1f} : au-dessus du seuil de {SEUIL_PCE_CITE_LITTERATURE:.0f} couramment cité "
            "dans Goljan, Fridrich & Filler (2009) — un indice fort, mais ce seuil dépend de la taille "
            "d'image et du contexte pour lequel il a été établi ; il ne remplace pas une calibration "
            "propre au cas et n'est jamais concluant seul."
        )
    return (
        f"PCE = {pce:.1f} : sous le seuil de {SEUIL_PCE_CITE_LITTERATURE:.0f} couramment cité dans la "
        "littérature. Cela n'établit pas l'absence de correspondance : une empreinte insuffisamment "
        "fournie, un recadrage important ou une forte compression peuvent aussi l'expliquer."
    )


# --- ELA : niveau d'erreur de compression ---

FORMATS_ELA_APPLICABLES = frozenset({"JPEG"})

AVERTISSEMENT_ELA = (
    "L'ELA ne détecte pas la manipulation : elle révèle des écarts de niveau d'erreur de "
    "compression, qui ont aussi des causes bénignes (recadrage, changement de résolution, "
    "réenregistrements successifs à la même qualité qui convergent vers un écart quasi nul "
    "partout — y compris sur une image authentique). Une carte homogène ne prouve pas "
    "l'absence de retouche ; une zone d'écart élevé n'est pas, à elle seule, la preuve d'un "
    "montage — elle indique seulement un endroit à examiner de plus près, avec d'autres méthodes."
)


def verifier_applicable_ela(format_original: str) -> None:
    if format_original.upper() not in FORMATS_ELA_APPLICABLES:
        raise SensorForensicsError(
            f"L'ELA ne s'applique qu'à une source JPEG (dernière compression connue) ; "
            f"format « {format_original} » non pris en charge par cette méthode."
        )


def recompresser_jpeg(image: Image.Image, qualite: int) -> bytes:
    """Réenregistre une image PIL en JPEG à la qualité donnée, en mémoire.

    La qualité de réenregistrement doit toujours être documentée avec le résultat
    (voir ResultatELA.qualite_recompression) : la carte ELA en dépend entièrement.
    """
    if not (1 <= qualite <= 100):
        raise SensorForensicsError("La qualité de réenregistrement JPEG doit être comprise entre 1 et 100.")
    tampon = io.BytesIO()
    image.convert("RGB").save(tampon, format="JPEG", quality=qualite)
    return tampon.getvalue()


@dataclass(frozen=True, eq=False)
class ResultatELA:
    """La carte ELA et son contexte — jamais la carte seule (§15.4, même discipline :
    la qualité de réenregistrement et le format d'origine sont toujours documentés)."""

    carte: np.ndarray
    qualite_recompression: int
    format_original: str
    valeur_max: float
    valeur_moyenne: float
    avertissement: str


def carte_ela(chemin_ou_donnees: Union[str, Path, bytes], qualite: int = 90) -> ResultatELA:
    """Calcule la carte ELA : différence absolue, canal par canal, entre l'image et
    sa version réenregistrée en JPEG à `qualite`, réduite au maximum des trois
    canaux par pixel. N'accepte qu'une source déjà JPEG (verifier_applicable_ela) :
    l'ELA compare deux compressions, une source sans compression de départ n'a
    rien à y révéler.
    """
    source = io.BytesIO(chemin_ou_donnees) if isinstance(chemin_ou_donnees, (bytes, bytearray)) else chemin_ou_donnees
    try:
        with Image.open(source) as image:
            format_original = image.format or "INCONNU"
            verifier_applicable_ela(format_original)
            image_rgb = image.convert("RGB")
            originale = np.asarray(image_rgb, dtype=np.float64)
    except SensorForensicsError:
        raise
    except Exception as exc:
        raise SensorForensicsError(f"Image illisible : {exc}") from exc

    recompressee = recompresser_jpeg(image_rgb, qualite)
    with Image.open(io.BytesIO(recompressee)) as image2:
        reencodee = np.asarray(image2.convert("RGB"), dtype=np.float64)

    difference = np.abs(originale - reencodee)
    carte = difference.max(axis=2)
    return ResultatELA(
        carte=carte,
        qualite_recompression=qualite,
        format_original=format_original,
        valeur_max=float(carte.max()),
        valeur_moyenne=float(carte.mean()),
        avertissement=AVERTISSEMENT_ELA,
    )


def intensite_zone(carte: np.ndarray, y0: int, y1: int, x0: int, x1: int) -> float:
    """Valeur ELA moyenne sur une région rectangulaire — pour comparer une zone
    suspecte à son voisinage, jamais pour poser un seuil absolu universel : aucune
    valeur d'ELA n'est, en soi, la preuve d'une retouche (voir AVERTISSEMENT_ELA).
    """
    if not (0 <= y0 < y1 <= carte.shape[0] and 0 <= x0 < x1 <= carte.shape[1]):
        raise SensorForensicsError("Région hors des limites de la carte ELA.")
    return float(carte[y0:y1, x0:x1].mean())
