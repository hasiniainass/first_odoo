from odoo import models, fields, api


class GeoUtilisateur(models.Model):
    _name = "geo.utilisateur"
    _description = "Utilisateur de la plateforme"
    _order = "nom, prenom"
    _rec_name = "name"

    name = fields.Char(
            string="Nom complet", 
            compute="_compute_name", 
            store=True
            )

    user_id = fields.Many2one(
            "res.users", 
            string="Compte Odoo",
             required=True, 
             ondelete="cascade"
            )

    nom = fields.Char(
            string="Nom", 
            required=True
            )
    
    prenom = fields.Char(
            string="Prénom", 
            required=True
            )
    
    email = fields.Char(
            string="Email", 
            required=True
            )
    
    telephone = fields.Char(
                string="Téléphone", 
                required=True
            )
    
    date_naissance = fields.Date(string="Date de naissance")

    date_inscription = fields.Datetime(string="Date d'inscription", default=fields.Datetime.now, readonly=True)
    actif = fields.Boolean(string="Actif", default=True)

    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    recherche_ids = fields.One2many("geo.recherche", "utilisateur_id", string="Recherches effectuées")
    nombre_recherches = fields.Integer(string="Nombre de recherches", compute="_compute_nombre_recherches")

    @api.depends("nom", "prenom")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.prenom or ''} {record.nom or ''}".strip()

    def _compute_nombre_recherches(self):
        for record in self:
            record.nombre_recherches = len(record.recherche_ids)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.nom = self.user_id.partner_id.lastname
            self.prenom = self.user_id.partner_id.firstname
            self.email = self.user_id.partner_id.email
            self.telephone = self.user_id.partner_id.phone