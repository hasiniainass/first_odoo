from odoo import models, fields, api
import math

class GeoEtablissement(models.Model):
    _name = "geo.etablissement"
    _description = "Établissement"
    _order = "nom_etab"

    nom_etab = fields.Char(string="Nom de l'établissement", required=True)
    adresse = fields.Text(string="Adresse")

    region = fields.Char(
        string="Région",
        default="Analamanga",
        readonly=True
    )

    district = fields.Selection([
        ("Antananarivo - Renivohitra", "Antananarivo - Renivohitra"),
        ("Antananarivo - Avaradrano", "Antananarivo - Avaradrano"),
        ("Antananarivo - Atsimondrano", "Antananarivo - Atsimondrano"),
        ("Ambohidratrimo", "Ambohidratrimo"),
        ("Andramasina", "Andramasina"),
        ("Anjozorobe", "Anjozorobe"),
        ("Ankazobe", "Ankazobe"),
        ("Manjakandriana", "Manjakandriana"),
    ], string="District")

    arrondissement = fields.Char(string="Arrondissement")
    commune = fields.Char(string="Commune")

    latitude_etab = fields.Float(string="Latitude")
    longitude_etab = fields.Float(string="Longitude")

    date_creation = fields.Date(string="Date de création")
    description = fields.Text(string="Description")
    taux_reussite = fields.Float(string="Taux de réussite (%)")

    qualite = fields.Selection([
        ("excellente", "Excellente qualité"),
        ("tres_bonne", "Très bonne qualité"),
        ("bonne", "Bonne qualité"),
        ("moyenne", "Qualité moyenne"),
    ], string="Qualité")

    image = fields.Image(string="Photo", max_width=800, max_height=600)

    type_id = fields.Many2one("geo.type.etablissement", string="Type", ondelete="restrict")
    categorie_id = fields.Many2one("geo.categorie", string="Catégorie", ondelete="restrict")

    @api.onchange("district")
    def _onchange_district(self):
        coordonnees_districts = {
            "Antananarivo - Renivohitra": (-18.8792, 47.5079),
            "Antananarivo - Avaradrano": (-18.8300, 47.5800),
            "Antananarivo - Atsimondrano": (-18.9700, 47.4800),
            "Ambohidratrimo": (-18.7700, 47.4200),
            "Andramasina": (-19.1700, 47.6200),
            "Anjozorobe": (-18.4200, 47.8700),
            "Ankazobe": (-18.3200, 47.1200),
            "Manjakandriana": (-18.9200, 47.8000),
        }
        if self.district in coordonnees_districts:
            lat, lng = coordonnees_districts[self.district]
            self.latitude_etab = lat
            self.longitude_etab = lng

    @api.model
    def calculer_distance(self, lat1, lng1, lat2, lng2):
        """Calcule la distance en km entre deux points GPS (formule de Haversine)."""
        rayon_terre = 6371  # rayon de la Terre en km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return rayon_terre * c