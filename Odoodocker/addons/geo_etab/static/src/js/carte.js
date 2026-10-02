document.addEventListener("DOMContentLoaded", function () {

    var carteDiv = document.getElementById("carte-etablissements");
    if (!carteDiv) {
        return;
    }

    var defaultCenter = [-18.8792, 47.5079];
    var carte = L.map("carte-etablissements").setView(defaultCenter, 9);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
        maxZoom: 19
    }).addTo(carte);

    var marqueurs = [];
    var groupeMarqueurs = null;
    var marqueurPosition = null;
    var positionUtilisateur = null;

    var iconEtab = L.divIcon({
        className: "geo-marker-etab",
        html: '<div style="background:#3b82f6; width:26px; height:26px; border-radius:50%; border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;"><i class="fa fa-graduation-cap" style="color:#fff;font-size:12px;"></i></div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13],
        popupAnchor: [0, -10]
    });

    var iconPos = L.divIcon({
        className: "geo-marker-pos",
        html: '<div style="position:relative;"><div style="background:#ef4444;width:20px;height:20px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 4px rgba(239,68,68,0.25);"></div><div style="position:absolute;inset:-8px;border-radius:50%;border:2px solid rgba(239,68,68,0.35);animation:geo-pulse 2s infinite;"></div></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function (pos) {
                positionUtilisateur = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                afficherMarqueurPosition(positionUtilisateur.lat, positionUtilisateur.lng);
                recentrerSurPosition();
            },
            function () {
                positionUtilisateur = { lat: defaultCenter[0], lng: defaultCenter[1] };
                afficherMarqueurPosition(positionUtilisateur.lat, positionUtilisateur.lng);
            },
            { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
        );
    } else {
        positionUtilisateur = { lat: defaultCenter[0], lng: defaultCenter[1] };
        afficherMarqueurPosition(positionUtilisateur.lat, positionUtilisateur.lng);
    }

    function afficherMarqueurPosition(lat, lng) {
        if (marqueurPosition) {
            carte.removeLayer(marqueurPosition);
        }
        marqueurPosition = L.marker([lat, lng], {
            icon: iconPos,
            title: "Ma position"
        }).addTo(carte);
    }

    function recentrerSurPosition() {
        if (positionUtilisateur) {
            carte.setView([positionUtilisateur.lat, positionUtilisateur.lng], 12);
        }
    }

    function calculerDistanceKm(lat1, lon1, lat2, lon2) {
        var R = 6371;
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLon = (lon2 - lon1) * Math.PI / 180;
        var a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }

    fetch("/api/etablissements" + window.location.search)
        .then(function (response) {
            if (!response.ok) throw new Error("HTTP " + response.status);
            return response.json();
        })
        .then(function (data) {

            (data.results || []).forEach(function (etab) {

                if (!etab.latitude || !etab.longitude) {
                    return;
                }

                var distanceTxt = "";
                if (positionUtilisateur) {
                    var dist = calculerDistanceKm(
                        positionUtilisateur.lat, positionUtilisateur.lng,
                        etab.latitude, etab.longitude
                    );
                    distanceTxt = (dist < 1
                        ? Math.round(dist * 1000) + " m"
                        : dist.toFixed(1).replace(".0", "") + " km");
                }

                var marqueur = L.marker([etab.latitude, etab.longitude], {
                    icon: iconEtab,
                    title: etab.nom || "Établissement"
                }).addTo(carte);

                var imgHtml = "";
                if (etab.a_une_photo) {
                    imgHtml = "<img class='geo-popup-img' src='/web/image/geo.etablissement/" + etab.id + "/image' alt=''/>";
                } else {
                    imgHtml = "<div class='geo-popup-img-placeholder'><i class='fa fa-university'></i></div>";
                }

                var qualiteLabel = {
                    "moyenne": "Moyenne",
                    "bonne": "Bonne",
                    "tres_bonne": "Très bonne",
                    "excellente": "Excellente"
                }[etab.qualite] || "";

                var contenuPopup =
                    "<div class='geo-popup-card'>" +
                    "<div class='geo-popup-body'>" +
                    "<div class='geo-popup-row'>" +
                    imgHtml +
                    "<div style='flex:1;min-width:0;'>" +
                    "<div class='geo-popup-titre'>" + (etab.nom || "") + "</div>" +
                    (etab.commune ? "<div class='geo-popup-info'><i class='fa fa-map-marker'></i>" + etab.commune + "</div>" : "") +
                    ((etab.type || etab.categorie)
                        ? "<div class='geo-popup-info'><i class='fa fa-university'></i>" +
                        (etab.type || "") +
                        (etab.type && etab.categorie ? " • " : "") +
                        (etab.categorie || "") + "</div>" : "") +
                    "</div>" +
                    "</div>" +

                    "<div class='geo-popup-detail'>" +
                    (qualiteLabel
                        ? "<div class='geo-popup-detail-row'><span style='color:#5a6578;'>Qualité :</span><span class='geo-popup-reussite' style='color:#1a9e5c;font-weight:600;'>" + qualiteLabel + "</span></div>"
                        : "") +
                    (etab.taux_reussite
                        ? "<div class='geo-popup-detail-row'><span style='color:#5a6578;'>Réussite :</span><span class='geo-popup-reussite'>" + etab.taux_reussite + "%</span></div>"
                        : "") +
                    (distanceTxt
                        ? "<div class='geo-popup-detail-row'><span style='color:#5a6578;'>Distance :</span><span>" + distanceTxt + "</span></div>"
                        : "") +
                    "<div style='text-align:right;margin-top:4px;'>" +
                    "<a href='" + (etab.url_detail || "#") + "' class='geo-popup-btn'>Voir détails</a>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "</div>";

                marqueur.bindPopup(contenuPopup, {
                    maxWidth: 300,
                    minWidth: 280,
                    className: "geo-popup-wrapper"
                });

                marqueurs.push(marqueur);
            });

            if (marqueurs.length > 0) {
                groupeMarqueurs = L.featureGroup(marqueurs);
                var bounds = groupeMarqueurs.getBounds();
                if (positionUtilisateur) {
                    bounds.extend([positionUtilisateur.lat, positionUtilisateur.lng]);
                }
                carte.fitBounds(bounds.pad(0.3));
            } else if (positionUtilisateur) {
                recentrerSurPosition();
            }

        })
        .catch(function (erreur) {
            console.error("Erreur de chargement des établissements :", erreur);
        });

    (function initLegende() {
        function setDisplay(selector, visible) {
            marqueurs.forEach(function (m) {
                if (visible) {
                    if (!carte.hasLayer(m)) m.addTo(carte);
                } else {
                    if (carte.hasLayer(m)) carte.removeLayer(m);
                }
            });
        }
        function setDisplayPos(visible) {
            if (!marqueurPosition) return;
            if (visible) {
                if (!carte.hasLayer(marqueurPosition)) marqueurPosition.addTo(carte);
            } else {
                if (carte.hasLayer(marqueurPosition)) carte.removeLayer(marqueurPosition);
            }
        }
        document.addEventListener("change", function (e) {
            if (e.target.id === "legendEtab") setDisplay(".geo-marker-etab", e.target.checked);
            if (e.target.id === "legendPos") setDisplayPos(e.target.checked);
        });
    })();

    if (!document.getElementById("geo-marker-style-inline")) {
        var s = document.createElement("style");
        s.id = "geo-marker-style-inline";
        s.textContent =
            "@keyframes geo-pulse {" +
            "  0%   { transform: scale(0.6); opacity: 0.8; }" +
            "  70%  { transform: scale(1.6); opacity: 0; }" +
            "  100% { transform: scale(1.6); opacity: 0; }" +
            "}" +
            ".geo-marker-etab, .geo-marker-pos { background: transparent; border: none; }" +
            ".leaflet-popup-wrapper .leaflet-popup-content { margin: 0; }";
        document.head.appendChild(s);
    }

});
