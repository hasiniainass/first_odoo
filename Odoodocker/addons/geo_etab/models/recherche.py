from odoo import models, fields, api


class GeoRecherche(models.Model):
    _name = "geo.recherche"
    _description = "Recherche effectuée par un utilisateur"
    _order = "date_recherche desc"
    _rec_name = "name"

    name = fields.Char(
        string="Résumé",
        compute="_compute_name",
        store=True
    )

    utilisateur_id = fields.Many2one(
        "geo.utilisateur",
        string="Utilisateur",
        ondelete="cascade",
        required=True
    )

    type_id = fields.Many2one(
        "geo.type.etablissement",
        string="Type recherché"
    )

    categorie_id = fields.Many2one(
        "geo.categorie",
        string="Catégorie recherchée"
    )

    region = fields.Char(
        string="Région"
    )

    district = fields.Selection([
        ("Antananarivo - Renivohitra","Antananarivo - Renivohitra"),
        ("Antananarivo - Avaradrano","Antananarivo - Avardrano"),
        ("Antananarivo - Atsimondrano","Antananarivo - Atsimondrano"),
        ("Ambihidratrimo","Ambohidratrimo"),
        ("ANDRAMASINA","Andramasina"),
        ("Anjozorobe","Anjozozrobe"),
        ("Ankazobe","Ankazobe"),
        ("Manjakandriana","Manjakandriana")
    ],
        string="District"
    )

    commune = fields.Char(
        string="Commune"
    )

    distance_max = fields.Float(
        string="Distance max (km)"
    )

    taux_reussite_min = fields.Float(
        string="Taux de réussite min (%)"
    )

    date_recherche = fields.Datetime(
        string="Date de la recherche",
        default=fields.Datetime.now,
        readonly=True
    )

    nombre_resultats = fields.Integer(
        string="Nombre de résultats trouvés",
        default=0
    )

    @api.depends("type_id", "categorie_id", "commune", "date_recherche")
    def _compute_name(self):
        for record in self:
            parts = []

            if record.type_id:
                parts.append(record.type_id.name)

            if record.categorie_id:
                parts.append(record.categorie_id.name)

            if record.commune:
                parts.append(record.commune)

            resume = " - ".join(parts) if parts else "Recherche"

            record.name = resume