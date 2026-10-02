import json
import math
import secrets
from odoo import http, exceptions
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GeoEtabController(http.Controller):

    @http.route("/etablissements", 
                 type="http", 
                 auth="public", 
                 website=True
                )
    def etablissements(self, **kwargs):
        nom = kwargs.get("nom", "").strip()
        district = kwargs.get("district", "").strip()
        commune = kwargs.get("commune", "").strip()
        type_id_str = kwargs.get("type_id", "").strip()
        categorie_id_str = kwargs.get("categorie_id", "").strip()
        qualite = kwargs.get("qualite", "").strip()
        taux_reussite_min_str = kwargs.get("taux_reussite_min", "").strip()
        user_lat_str = kwargs.get("user_lat", "").strip()
        user_lng_str = kwargs.get("user_lng", "").strip()
        rayon_km_str = kwargs.get("rayon_km", "").strip()
        region = kwargs.get("region", "").strip()

        domain = []

        if nom:
            domain.append(("nom_etab", "ilike", nom))
        if region:
            domain.append(("region", "ilike", region))
        if district:
            domain.append(("district", "=", district))
        if commune:
            domain.append(("commune", "ilike", commune))

        try:
            if type_id_str:
                type_id = int(type_id_str)
                domain.append(("type_id", "=", type_id))
            if categorie_id_str:
                categorie_id = int(categorie_id_str)
                domain.append(("categorie_id", "=", categorie_id))
        except ValueError:
            pass

        if qualite:
            niveaux = ["moyenne", "bonne", "tres_bonne", "excellente"]
            if qualite in niveaux:
                index_min = niveaux.index(qualite)
                domain.append(("qualite", "in", niveaux[index_min:]))

        try:
            if taux_reussite_min_str:
                taux_reussite_min = float(taux_reussite_min_str)
                domain.append(("taux_reussite", ">=", taux_reussite_min))
        except ValueError:
            pass

        etablissements = request.env["geo.etablissement"].sudo().search(domain)

        etablissements_avec_distance = []
        try:
            if user_lat_str and user_lng_str:
                lat_user = float(user_lat_str)
                lng_user = float(user_lng_str)
                rayon_km = float(rayon_km_str) if rayon_km_str else None

                for etab in etablissements:
                    distance = None
                    if etab.latitude_etab and etab.longitude_etab:
                        distance = etab.calculer_distance(
                            lat_user, lng_user, etab.latitude_etab, etab.longitude_etab
                        )

                    if rayon_km is not None and (distance is None or distance > rayon_km):
                        continue

                    etablissements_avec_distance.append({"etab": etab, "distance": distance})

                etablissements_avec_distance.sort(
                    key=lambda x: x["distance"] if x["distance"] is not None else float("inf")
                )
            else:
                etablissements_avec_distance = [{"etab": etab, "distance": None} for etab in etablissements]
        except ValueError:
            etablissements_avec_distance = [{"etab": etab, "distance": None} for etab in etablissements]

        types = request.env["geo.type.etablissement"].sudo().search([], order="name")
        categories = request.env["geo.categorie"].sudo().search([], order="name")
        district_selection = request.env["geo.etablissement"].fields_get(["district"])["district"]["selection"]

        if not request.env.user._is_public() and any([nom, region, district, commune, type_id_str, categorie_id_str]):
            geo_utilisateur = request.env["geo.utilisateur"].sudo().search(
                [("user_id", "=", request.env.user.id)], limit=1
            )
            if geo_utilisateur:
                try:
                    vals = {
                        "utilisateur_id": geo_utilisateur.id,
                        "nombre_resultats": len(etablissements_avec_distance),
                        "region": region,
                        "district": district,
                        "commune": commune,
                    }
                    if type_id_str:
                        vals["type_id"] = int(type_id_str)
                    if categorie_id_str:
                        vals["categorie_id"] = int(categorie_id_str)
                    request.env["geo.recherche"].sudo().create(vals)
                except (ValueError, Exception) as e:
                    _logger.warning(f"Impossible d'enregistrer la recherche: {e}")

        return request.render(
            "geo_etab.recherche_etablissement",
            {
                "etablissements_avec_distance": etablissements_avec_distance,
                "types": types,
                "categories": categories,
                "districts": district_selection,
                "values": kwargs,
            }
        )


           # etablissement detail
    @http.route(
            "/etablissement/<int:etablissement_id>", 
            type="http", 
            auth="public", 
            website=True
        )
    def etablissement_detail(self, etablissement_id, **kwargs):
        etablissement = request.env["geo.etablissement"].sudo().browse(etablissement_id)
        if not etablissement.exists():
            return request.not_found()

        return request.render(
            "geo_etab.template_etablissement_detail",
            {
                "etablissement": etablissement
            }
        )


    # API JSON DE RECHERCHE
    @http.route(
            "/api/etablissements", 
            type="http", 
            auth="public", 
            methods=["GET"], 
            csrf=False
        )
    def api_etablissements(self, **kwargs):

        nom = kwargs.get("nom", "").strip()
        district = kwargs.get("district", "").strip()
        commune = kwargs.get("commune", "").strip()
        type_id_str = kwargs.get("type_id", "").strip()
        categorie_id_str = kwargs.get("categorie_id", "").strip()
        qualite = kwargs.get("qualite", "").strip()
        taux_reussite_min_str = kwargs.get("taux_reussite_min", "").strip()

        domain = []

        if nom:
            domain.append(("nom_etab", "ilike", nom))
        if district:
            domain.append(("district", "=", district))
        if commune:
            domain.append(("commune", "ilike", commune))

        try:
            if type_id_str:
                domain.append(("type_id", "=", int(type_id_str)))
            if categorie_id_str:
                domain.append(("categorie_id", "=", int(categorie_id_str)))
        except ValueError:
            pass

        if qualite:
            niveaux = ["moyenne", "bonne", "tres_bonne", "excellente"]
            if qualite in niveaux:
                index_min = niveaux.index(qualite)
                domain.append(("qualite", "in", niveaux[index_min:]))

        try:
            if taux_reussite_min_str:
                domain.append(("taux_reussite", ">=", float(taux_reussite_min_str)))
        except ValueError:
            pass

        etablissements = request.env["geo.etablissement"].sudo().search(domain)

        resultats = [
            {
                "id": etab.id,
                "nom": etab.nom_etab,
                "adresse": etab.adresse,
                "region": etab.region,
                "district": etab.district,
                "commune": etab.commune,
                "type": etab.type_id.name if etab.type_id else None,
                "categorie": etab.categorie_id.name if etab.categorie_id else None,
                "qualite": etab.qualite,
                "taux_reussite": etab.taux_reussite,
                "latitude": etab.latitude_etab,
                "longitude": etab.longitude_etab,
                "a_une_photo": bool(etab.image),
                "url_detail": f"/etablissement/{etab.id}",
            }
            for etab in etablissements
        ]

        response_data = {"count": len(resultats), "results": resultats}

        return request.make_response(
            json.dumps(response_data, ensure_ascii=False),
            headers=[("Content-Type", "application/json")],
        )

    
    # inscription detail
    @http.route(
            "/inscription", 
            type="http", 
            auth="public", 
            website=True, 
            methods=["GET"]
        )
    def inscription_formulaire(self, **kwargs):
            return request.render(
                "geo_etab.template_inscription", 
                {"error": None, "values": {}}
            )

    @http.route(
            "/inscription", 
            type="http", 
            auth="public", 
            website=True, 
            methods=["POST"], 
            csrf=True
        )
    def inscription_soumettre(self, **post):

        nom = post.get("nom", "").strip()
        prenom = post.get("prenom", "").strip()
        email = post.get("email", "").strip()
        telephone = post.get("telephone", "").strip()
        date_naissance = post.get("date_naissance", "").strip()
        password = post.get("password", "")
        confirmation = post.get("confirmation", "")

        if not nom or not prenom or not email or not telephone or not password:
            return request.render(
                "geo_etab.template_inscription",
                {"error": "Merci de remplir tous les champs obligatoires.", "values": post}
            )

        if password != confirmation:
            return request.render(
                "geo_etab.template_inscription",
                {"error": "Les mots de passe ne correspondent pas.", "values": post}
            )

        if len(password) < 6:
            return request.render(
                "geo_etab.template_inscription",
                {"error": "Le mot de passe doit contenir au moins 6 caractères.", "values": post}
            )

        existing_user = request.env["res.users"].sudo().search([("login", "=", email)], limit=1)

        if existing_user:
            return request.render("geo_etab.template_inscription",
                {"error": "Un compte existe déjà avec cet email.", "values": post}
            )

        try:
            new_res_user = request.env["res.users"].sudo().create({
                "name": f"{prenom} {nom}",
                "login": email,
                "password": password,
                "groups_id": [(6, 0, [request.env.ref("base.group_portal").id])],
            })

            request.env["geo.utilisateur"].sudo().create({
                "user_id": new_res_user.id,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "telephone": telephone,
                "date_naissance": date_naissance or False,
            })
          
            request.env.cr.commit()

        except Exception as e:
            request.env.cr.rollback()
            return request.render(
                "geo_etab.template_inscription",
                {"error": f"Une erreur est survenue lors de la création du compte : {str(e)}", "values": post}
            )

        # Automatic login
        try:
            request.session.authenticate(request.session.db, email, password)
            return request.redirect("/etablissements")
        except Exception:
            # If auto-login fails, the user account is already created.
            # Redirect to login page with an explanatory message.
            return request.render("geo_etab.template_connexion",
                {"error": "Votre compte a été créé, Veuillez vous connecter manuellement.", "values": {"email": email}})



    # CONNEXION VISITEUR (frontend custom)
    @http.route(
            "/connexion", 
            type="http", 
            auth="public", 
            website=True, 
            methods=["GET"]
            )
    def connexion_formulaire(self, redirect=None, **kwargs):
        if not request.env.user._is_public():
            return request.redirect("/my")

        error_message = None
        if kwargs.get("error") == "auth_failed":
            error_message = "Votre compte a été créé, mais la connexion a échoué. Veuillez réessayer."
        elif "error" in kwargs:
            error_message = kwargs["error"]

        return request.render(
            "geo_etab.template_connexion",
            {"error": error_message,
             "values": {},
             "redirect": redirect
             }
        )

    @http.route(
        "/connexion",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True
    )
    def connexion_soumettre(self, **post):

        if not request.env.user._is_public():
            return request.redirect("/my")

        email = (post.get("email") or post.get("login") or "").strip()
        password = post.get("password", "")

        if not email or not password:
            return request.render(
                "geo_etab.template_connexion",
                {"error": "Merci de saisir votre email et votre mot de passe.", "values": post},
            )

        try:
            credential = {"login": email, "password": password, "type": "password"}
            auth_info = request.session.authenticate(request.session.db, credential)

            if not auth_info:
                raise exceptions.AccessDenied()

        except exceptions.AccessDenied:
            return request.render(
                "geo_etab.template_connexion",
                {"error": "Email ou mot de passe incorrect.", "values": post},
            )

        except Exception as e:
            _logger.error("Erreur de connexion inattendue : %s", e, exc_info=True)
            return request.render(
                "geo_etab.template_connexion",
                {"error": f"Erreur technique : {str(e)}", "values": post},
            )

        return request.redirect("/accueil?connexion=reussie")
    
    @http.route(
            "/deconnexion", 
            type="http", 
             auth="user", 
             website=True, 
             methods=["GET"], 
            csrf=False
        )
    def deconnexion(self, **kwargs):
        request.session.logout(keep_db=True)
        return request.redirect("/connexion")


    # pages static du site

    @http.route(
            "/accueil", 
            type="http", 
            auth="public", 
            website=True
        )
    def accueil(self, **kwargs):
        return request.render(
            "geo_etab.template_accueil", {}
        )

    @http.route("/a-propos", 
                type="http", 
                auth="public", 
                website=True
                )
    def a_propos(self, **kwargs):
        return request.render(
            "geo_etab.template_a_propos", {}
        )

    @http.route(
            "/contact", 
             type="http", 
            auth="public", 
            website=True
        )
    def contact(self, **kwargs):
        return request.render(
            "geo_etab.template_contact", {}
        )
    

    # MON COMPTE (page pour visiteur connecté)
    @http.route(
            "/my", 
            type="http", 
            auth="user", 
            website=True
        )
    def mon_compte(self, **kwargs):
        user = request.env.user
        geo_utilisateur = request.env["geo.utilisateur"].sudo().search(
            [("user_id", "=", user.id)], limit=1
        )

        recherches_recentes = request.env["geo.recherche"].sudo().search(
            [("utilisateur_id", "=", geo_utilisateur.id)],
            order="create_date desc",
            limit=5
        )

        nom_affichage = geo_utilisateur.nom if geo_utilisateur else user.name

        return request.render(
            "geo_etab.template_mon_compte",
            {
                "user": user,
                "geo_utilisateur": geo_utilisateur,
                "recherches_recentes": recherches_recentes,
                "nom_affichage": nom_affichage,
            }
        )