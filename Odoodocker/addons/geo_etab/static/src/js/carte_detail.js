document.addEventListener("DOMContentLoaded", function () {

    var carteDiv = document.getElementById("carte-etablissement-detail");
    if (!carteDiv) {
        return;
    }

    var lat = parseFloat(carteDiv.dataset.lat);
    var lng = parseFloat(carteDiv.dataset.lng);
    var nom = carteDiv.dataset.nom;

    if (isNaN(lat) || isNaN(lng)) {
        console.error("Coordonnées invalides pour l'établissement.");
        carteDiv.innerHTML = "<div class='alert alert-warning'>Coordonnées de la carte non disponibles.</div>";
        return;
    }

    var carte = L.map(carteDiv).setView([lat, lng], 15);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
        maxZoom: 19
    }).addTo(carte);

    var iconEtab = L.divIcon({
        className: "geo-marker-etab",
        html: '<div style="background:#3b82f6; width:26px; height:26px; border-radius:50%; border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;"><i class="fa fa-graduation-cap" style="color:#fff;font-size:12px;"></i></div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
    });

    L.marker([lat, lng], {
        icon: iconEtab,
        title: nom
    }).addTo(carte)
        .bindPopup("<b>" + nom + "</b>")
        .openPopup();

});