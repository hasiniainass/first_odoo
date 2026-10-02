from odoo import models, fields


class GeoCategorie(models.Model):
    _name = "geo.categorie"
    _description = "Catégorie d'établissement"
    _order = "name"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")
    actif = fields.Boolean(string="Actif", default=True)

    etablissement_ids = fields.One2many("geo.etablissement", "categorie_id", string="Établissements")
    nombre_etablissements = fields.Integer(string="Nombre d'établissements", compute="_compute_nombre_etablissements")

    def _compute_nombre_etablissements(self):
        for record in self:
            record.nombre_etablissements = len(record.etablissement_ids)