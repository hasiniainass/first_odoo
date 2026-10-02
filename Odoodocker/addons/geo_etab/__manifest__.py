{
    "name": "Géo Etab",
    "version": "1.0",
    "summary": "Gestion géographique des établissements",
    "description": """
        Gestion des établissements, types, catégories,
        utilisateurs et recherche dans la région Analamanga.
    """,
    "author": "Andriantsara",
    "category": "Education",
    "license": "LGPL-3",

    "depends": ["base", "website"],

    "data": [
        "security/ir.model.access.csv",
        "security/ir_rules.xml",

        "views/website_menu.xml",
        "views/pages_static.xml",
        "views/etablissement.xml",
        "views/etablissement_detail.xml",
        "views/type.xml",
        "views/categorie.xml",
        "views/utilisateur.xml",
        "views/recherche_admin.xml",
        "views/recherche.xml",
        "views/inscription.xml",
        "views/connexion.xml",
        "views/dashboard.xml",
        "views/menu.xml",
    ],

    "assets": {
        "web.assets_frontend": [
            "geo_etab/static/src/css/frontend.css",
            "geo_etab/static/src/css/custom.css",
            "geo_etab/static/src/js/carte.js",
            "geo_etab/static/src/js/carte_detail.js",
            "geo_etab/static/src/js/geolocalisation.js",
            "geo_etab/static/src/js/toast.js",
        ],
        "web.assets_backend": [
            "geo_etab/static/src/css/dashboard.css",
        ],
    },

    "installable": True,
    "application": True,
}