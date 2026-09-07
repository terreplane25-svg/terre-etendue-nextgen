"""
La télémétrie de vol écrite dans le XMP.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que les champs publiés par les constructeurs sont relevés dans les deux formes
d'écriture du XMP, que les grandeurs dont le protocole a besoin sont extraites
nommément, et surtout que ce que le fichier NE PORTE PAS le reste : la position
de la station sol n'est pas remplie par celle du drone, et un tangage absent ne
devient pas « visée horizontale ».

Les paquets XMP sont écrits ici, d'après les espaces de noms publiés. Ils
établissent que le lecteur suit ces espaces — pas qu'un DJI réel écrit
exactement ceci. Confronter le lecteur à des fichiers de drones réels reste
ouvert.
"""

import pytest

from preuve_image.telemetrie import (
    AVERTISSEMENT_ALTITUDE_RELATIVE,
    MOTIF_STATION_SOL_ABSENTE,
    extraire_telemetrie,
)

# ─────────────────────────────────────────────────────────────────────────────
# Paquets d'essai
# ─────────────────────────────────────────────────────────────────────────────

#: Forme ATTRIBUT, celle de DJI. Noter « GpsLongtitude », avec un t de trop :
#: c'est l'orthographe réelle du constructeur, pas une coquille de ce test.
XMP_DJI = b"""<?xpacket begin="\xef\xbb\xbf"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:drone-dji="http://www.dji.com/drone-dji/1.0/"
    drone-dji:AbsoluteAltitude="+152.30"
    drone-dji:RelativeAltitude="+87.50"
    drone-dji:GpsLatitude="46.6186320"
    drone-dji:GpsLongtitude="7.0583110"
    drone-dji:GimbalRollDegree="+0.00"
    drone-dji:GimbalYawDegree="-114.20"
    drone-dji:GimbalPitchDegree="-0.40"
    drone-dji:FlightRollDegree="+1.10"
    drone-dji:FlightYawDegree="-113.80"
    drone-dji:FlightPitchDegree="+2.30"
    drone-dji:RtkFlag="50"
    drone-dji:RtkStdLat="0.01"
    drone-dji:CalibratedFocalLength="3666.666504"
    drone-dji:DewarpFlag="1"/>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""

#: Forme ÉLÉMENT, celle qu'emploient Parrot et plusieurs exports.
XMP_PARROT = b"""<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description xmlns:Camera="http://pix4d.com/camera/1.0/"
                   xmlns:drone-parrot="http://www.parrot.com/drone-parrot/1.0/">
   <Camera:Yaw>112.5</Camera:Yaw>
   <Camera:Pitch>-89.9</Camera:Pitch>
   <Camera:Roll>0.3</Camera:Roll>
   <Camera:AboveGroundAltitude>42.75</Camera:AboveGroundAltitude>
   <Camera:GPSXYAccuracy>1.20</Camera:GPSXYAccuracy>
   <Camera:GPSZAccuracy>2.40</Camera:GPSZAccuracy>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>"""

XMP_SANS_TELEMETRIE = b"""<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                   xmp:CreatorTool="EssaiCorp Editeur 3.1"/>
 </rdf:RDF>
</x:xmpmeta>"""


# ─────────────────────────────────────────────────────────────────────────────
# DJI — forme attribut
# ─────────────────────────────────────────────────────────────────────────────


def test_dji_reconnu():
    t = extraire_telemetrie(XMP_DJI)
    assert t.present is True
    assert t.origine == "DJI"
    assert "drone-dji" in t.prefixes


def test_dji_position_et_altitudes():
    t = extraire_telemetrie(XMP_DJI)
    assert t.latitude_deg == pytest.approx(46.6186320)
    assert t.altitude_absolue_m == pytest.approx(152.30)
    assert t.altitude_relative_m == pytest.approx(87.50)


def test_l_orthographe_dji_de_la_longitude_est_traitee():
    """DJI écrit « GpsLongtitude », avec un t de trop, depuis des années.

    Ne traiter que l'orthographe correcte ferait perdre la longitude sur la
    majorité des images de drone en circulation — silencieusement, puisque le
    champ resterait simplement nul.
    """
    t = extraire_telemetrie(XMP_DJI)
    assert t.longitude_deg == pytest.approx(7.0583110)
    assert b"GpsLongtitude" in XMP_DJI
    assert b"GpsLongitude=" not in XMP_DJI, (
        "le paquet d'essai doit porter UNIQUEMENT l'orthographe fautive, "
        "sinon le test ne prouve rien"
    )


def test_dji_attitude_de_la_nacelle():
    t = extraire_telemetrie(XMP_DJI)
    assert t.tangage_nacelle_deg == pytest.approx(-0.40)
    assert t.lacet_nacelle_deg == pytest.approx(-114.20)
    assert t.roulis_nacelle_deg == pytest.approx(0.0)


def test_signe_explicite_conserve_dans_le_brut():
    """DJI écrit « +152.30 ». Le nombre est converti, la forme est gardée."""
    t = extraire_telemetrie(XMP_DJI)
    champ = next(c for c in t.champs if c.nom == "AbsoluteAltitude")
    assert champ.brut == "+152.30"
    assert champ.valeur == pytest.approx(152.30)


def test_champs_secondaires_releves_avec_leur_sens():
    t = extraire_telemetrie(XMP_DJI)
    cles = {c.cle for c in t.champs}
    assert "drone-dji:RtkFlag" in cles
    assert "drone-dji:CalibratedFocalLength" in cles
    assert t.sens["drone-dji:RtkFlag"] == "état de la correction RTK"
    assert "distorsion" in t.sens["drone-dji:DewarpFlag"]


# ─────────────────────────────────────────────────────────────────────────────
# Parrot — forme élément
# ─────────────────────────────────────────────────────────────────────────────


def test_forme_element_lue_aussi():
    """Les deux écritures du XMP existent, parfois dans le même fichier.

    Ne traiter que la forme attribut perdrait tout Parrot et une partie des
    exports de traitement photogrammétrique.
    """
    t = extraire_telemetrie(XMP_PARROT)
    assert t.present is True
    assert t.tangage_nacelle_deg == pytest.approx(-89.9)
    assert t.lacet_nacelle_deg == pytest.approx(112.5)
    assert t.altitude_sol_m == pytest.approx(42.75)


def test_camera_seul_ne_designe_aucun_constructeur():
    """« Camera » est un espace partagé : l'attribuer serait sans fondement."""
    t = extraire_telemetrie(
        XMP_PARROT.replace(b'xmlns:drone-parrot="http://www.parrot.com/drone-parrot/1.0/"', b""))
    assert t.present is True
    assert t.origine is None
    assert "Camera" in t.prefixes


def test_incertitudes_annoncees_relevees():
    t = extraire_telemetrie(XMP_PARROT)
    cles = {c.cle: c.valeur for c in t.champs}
    assert cles["Camera:GPSXYAccuracy"] == pytest.approx(1.20)
    assert cles["Camera:GPSZAccuracy"] == pytest.approx(2.40)


# ─────────────────────────────────────────────────────────────────────────────
# Ce que le fichier ne porte pas
# ─────────────────────────────────────────────────────────────────────────────


def test_la_station_sol_n_est_jamais_remplie_par_la_position_du_drone():
    """Le champ demandé par le cahier des charges n'existe pas dans le cas courant.

    Le remplir avec la position du drone sous une autre étiquette donnerait un
    champ rempli et faux — le pire des deux mondes.
    """
    t = extraire_telemetrie(XMP_DJI)
    assert t.station_sol is None
    assert t.motif_station_sol == MOTIF_STATION_SOL_ABSENTE
    assert "position du drone sous une autre étiquette" in t.motif_station_sol


def test_l_altitude_relative_porte_son_avertissement():
    """Elle est comptée depuis le DÉCOLLAGE, pas depuis le sol ni la mer."""
    t = extraire_telemetrie(XMP_DJI)
    assert t.altitude_relative_m is not None
    assert "POINT DE DÉCOLLAGE" in t.avertissement_altitude
    assert AVERTISSEMENT_ALTITUDE_RELATIVE == t.avertissement_altitude


def test_tangage_absent_ne_devient_pas_visee_horizontale():
    """Une absence de mesure n'établit pas que la visée était inclinée — ni
    qu'elle était horizontale. Le champ vaut None, jamais False.
    """
    sans = XMP_DJI.replace(b'drone-dji:GimbalPitchDegree="-0.40"', b"")
    t = extraire_telemetrie(sans)
    assert t.tangage_nacelle_deg is None
    assert t.visee_horizontale is None


def test_visee_horizontale_quand_le_tangage_est_proche_de_zero():
    assert extraire_telemetrie(XMP_DJI).visee_horizontale is True


def test_visee_en_plongee_n_est_pas_horizontale():
    """Une mesure d'angle sur une image en plongée ne dit pas la même chose."""
    assert extraire_telemetrie(XMP_PARROT).visee_horizontale is False


# ─────────────────────────────────────────────────────────────────────────────
# Absence, robustesse
# ─────────────────────────────────────────────────────────────────────────────


def test_xmp_sans_telemetrie():
    t = extraire_telemetrie(XMP_SANS_TELEMETRIE)
    assert t.present is False
    assert t.prefixes == ()
    assert t.champs == ()


def test_aucun_paquet():
    assert extraire_telemetrie([]).present is False


def test_accepte_bytes_str_et_suites():
    """Les paquets viennent de trois modules différents, sous trois formes."""
    a = extraire_telemetrie(XMP_DJI)
    b = extraire_telemetrie(XMP_DJI.decode("utf-8"))
    c = extraire_telemetrie([XMP_SANS_TELEMETRIE, XMP_DJI])
    assert a.latitude_deg == b.latitude_deg == c.latitude_deg


def test_deux_paquets_fusionnes():
    t = extraire_telemetrie([XMP_DJI, XMP_PARROT])
    assert t.origine == "DJI"
    assert {"drone-dji", "Camera", "drone-parrot"} <= set(t.prefixes)
    # Le tangage DJI l'emporte, parce que GimbalPitchDegree est cherché avant
    # Pitch : c'est le champ le plus spécifique.
    assert t.tangage_nacelle_deg == pytest.approx(-0.40)


def test_valeur_non_numerique_ne_devient_pas_zero():
    """Rendre 0 pour un champ illisible ferait une altitude au niveau de la mer."""
    abime = XMP_DJI.replace(b'drone-dji:RelativeAltitude="+87.50"',
                            b'drone-dji:RelativeAltitude="indisponible"')
    t = extraire_telemetrie(abime)
    assert t.altitude_relative_m is None
    champ = next(c for c in t.champs if c.nom == "RelativeAltitude")
    assert champ.brut == "indisponible"
    assert champ.valeur is None


def test_prefixe_de_drone_hors_table_releve_quand_meme():
    """Savoir qu'il y a de la télémétrie qu'on ne sait pas attribuer est une
    information ; l'écarter en silence n'en est pas une.
    """
    exotique = XMP_DJI.replace(b"drone-dji", b"drone-inconnu")
    t = extraire_telemetrie(exotique)
    assert t.present is True
    assert "drone-inconnu" in t.prefixes
    assert t.origine is None
    assert t.latitude_deg == pytest.approx(46.6186320)
