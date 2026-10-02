from odoo import models, fields


class GeoTypeEtablissement(models.Model):
    _name = "geo.type.etablissement"
    _description = "Type d'établissement"
    _order = "name"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")
    actif = fields.Boolean(string="Actif", default=True)

    etablissement_ids = fields.One2many("geo.etablissement", "type_id", string="Établissements")
    nombre_etablissements = fields.Integer(string="Nombre d'établissements", compute="_compute_nombre_etablissements")

    def _compute_nombre_etablissements(self):
        for record in self:
            record.nombre_etablissements = len(record.etablissement_ids)