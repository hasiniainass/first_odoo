from odoo import models, fields, api
from datetime import datetime


class GeoDashboard(models.TransientModel):
    _name = "geo.dashboard"
    _description = "Tableau de bord administrateur"

    # ---------- Bloc 1 : cartes statistiques ----------
    nombre_etablissements = fields.Integer(
                                    string="Établissements", 
                                    compute="_compute_stats"
                                    )
    nombre_types = fields.Integer(
                                    string="Types d'établissement", 
                                    compute="_compute_stats"
                                    )
    
    nombre_categories = fields.Integer(
                                    string="Catégories", 
                                    compute="_compute_stats"
                                    )
    nombre_utilisateurs = fields.Integer(
                                    string="Utilisateurs inscrits", 
                                    compute="_compute_stats"
                                    )
    nombre_recherches = fields.Integer(
                                    string="Recherches effectuées", 
                                    compute="_compute_stats"
                                    )
    nombre_resultats_total = fields.Integer(
                                    string="Résultats", 
                                    compute="_compute_stats"
                                    )

    # ---------- Bloc 2 : établissements récents ----------
    etablissement_recent_ids = fields.Many2many(
        "geo.etablissement",
        compute="_compute_recent",
        string="Établissements récents"
    )

    # ---------- Bloc 3 : répartition par type ----------
    repartition_html = fields.Html(
                                    compute="_compute_repartition", 
                                    sanitize=False
                                    )

    # ---------- Bloc 4 : activité récente ----------
    activite_html = fields.Html(
                             compute="_compute_activite", 
                             sanitize=False
                            )

    # ---------- Bloc 5 : recherche rapide ----------
    quick_nom = fields.Char(
                            string="Nom"
                            )
    quick_type_id = fields.Many2one(
                            "geo.type.etablissement",
                            string="Type"
                             )
    quick_categorie_id = fields.Many2one(
                            "geo.categorie",
                            string="Catégorie"
                             )

    def _compute_stats(self):
        for record in self:
            record.nombre_etablissements = self.env["geo.etablissement"].search_count([])
            record.nombre_types = self.env["geo.type.etablissement"].search_count([])
            record.nombre_categories = self.env["geo.categorie"].search_count([])
            record.nombre_utilisateurs = self.env["geo.utilisateur"].search_count([])
            record.nombre_recherches = self.env["geo.recherche"].search_count([])
            record.nombre_resultats_total = sum(
                self.env["geo.recherche"].search([]).mapped("nombre_resultats")
            )

    def _compute_recent(self):
        for record in self:
            recents = self.env["geo.etablissement"].search([], order="id desc", limit=5)
            record.etablissement_recent_ids = recents

    def _compute_repartition(self):
        palette = ["#4c6ef5", "#2f9e5c", "#e0972e", "#7c3aed", "#d63f8f", "#5a6578"]

        for record in self:
            types = self.env["geo.type.etablissement"].search([])
            total = self.env["geo.etablissement"].search_count([])

            lignes = []
            segments = []
            angle_courant = 0

            for i, type_etab in enumerate(types):
                nb = self.env["geo.etablissement"].search_count([("type_id", "=", type_etab.id)])
                if not nb:
                    continue

                pourcentage = round((nb / total) * 100, 1) if total else 0
                couleur = palette[i % len(palette)]

                angle_fin = angle_courant + (pourcentage / 100) * 360
                segments.append(f"{couleur} {angle_courant}deg {angle_fin}deg")
                angle_courant = angle_fin

                lignes.append(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                        <span style="width:10px;height:10px;border-radius:50%;background:{couleur};display:inline-block;flex-shrink:0;"></span>
                        <span style="font-size:0.85rem;color:#4b5568;">{type_etab.name} ({pourcentage}%)</span>
                    </div>
                """)

            gradient = ", ".join(segments) if segments else "#eef1f6 0deg 360deg"

            html = f"""
                <div style="display:flex;flex-direction:column;align-items:center;gap:16px;">
                    <div style="
                        width:140px;height:140px;border-radius:50%;
                        background:conic-gradient({gradient});
                        display:flex;align-items:center;justify-content:center;
                    ">
                        <div style="width:70px;height:70px;border-radius:50%;background:#fff;"></div>
                    </div>
                    <div style="width:100%;">
                        {''.join(lignes)}
                    </div>
                </div>
            """
            record.repartition_html = html

    def _compute_activite(self):
        for record in self:
            evenements = []

            for etab in self.env["geo.etablissement"].search([], order="create_date desc", limit=3):
                if etab.create_date:
                    evenements.append({
                        "date": etab.create_date,
                        "icone": "fa-plus-circle",
                        "couleur": "#2f9e5c",
                        "titre": "Nouvel établissement créé",
                        "detail": etab.nom_etab,
                    })

            for user in self.env["geo.utilisateur"].search([], order="date_inscription desc", limit=3):
                if user.date_inscription:
                    evenements.append({
                        "date": user.date_inscription,
                        "icone": "fa-user-plus",
                        "couleur": "#d63f8f",
                        "titre": "Nouvel utilisateur inscrit",
                        "detail": user.name,
                    })

            for rech in self.env["geo.recherche"].search([], order="date_recherche desc", limit=3):
                if rech.date_recherche:
                    evenements.append({
                        "date": rech.date_recherche,
                        "icone": "fa-search",
                        "couleur": "#4c6ef5",
                        "titre": "Nouvelle recherche effectuée",
                        "detail": rech.name or "Recherche",
                    })

            evenements.sort(key=lambda e: e["date"], reverse=True)
            evenements = evenements[:5]

            lignes = []
            maintenant = datetime.now()

            for ev in evenements:
                delta = maintenant - ev["date"]
                minutes = int(delta.total_seconds() / 60)

                if minutes < 60:
                    temps = f"Il y a {minutes} minute(s)"
                elif minutes < 1440:
                    temps = f"Il y a {minutes // 60} heure(s)"
                else:
                    temps = f"Il y a {minutes // 1440} jour(s)"

                lignes.append(f"""
                    <div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #f0f2f7;">
                        <div style="
                            width:34px;height:34px;border-radius:50%;
                            background:{ev['couleur']}20;color:{ev['couleur']};
                            display:flex;align-items:center;justify-content:center;flex-shrink:0;
                        ">
                            <i class="fa {ev['icone']}"></i>
                        </div>
                        <div style="flex-grow:1;">
                            <div style="font-weight:600;font-size:0.9rem;color:#1a2233;">{ev['titre']}</div>
                            <div style="font-size:0.82rem;color:#6a6478;">{ev['detail']}</div>
                        </div>
                        <div style="font-size:0.78rem;color:#9aa3b2;white-space:nowrap;">{temps}</div>
                    </div>
                """)

            record.activite_html = "".join(lignes) if lignes else "<p class='text-muted'>Aucune activité récente.</p>"

    @api.model
    def action_open_dashboard(self):
        dashboard = self.create({})
        return {
            "type": "ir.actions.act_window",
            "res_model": "geo.dashboard",
            "view_mode": "form",
            "res_id": dashboard.id,
            "target": "main",
        }

    def action_new_etablissement(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "geo.etablissement",
            "view_mode": "form",
            "target": "current",
        }

    def action_quick_search(self):
        domain = []
        if self.quick_nom:
            domain.append(("nom_etab", "ilike", self.quick_nom))
        if self.quick_type_id:
            domain.append(("type_id", "=", self.quick_type_id.id))
        if self.quick_categorie_id:
            domain.append(("categorie_id", "=", self.quick_categorie_id.id))

        return {
            "type": "ir.actions.act_window",
            "res_model": "geo.etablissement",
            "view_mode": "list,form",
            "domain": domain,
            "target": "current",
        }