document.addEventListener("DOMContentLoaded", function () {

    var inputLocalisation = document.getElementById("geo-localisation-input");
    var inputLat = document.getElementById("geo-user-lat");
    var inputLng = document.getElementById("geo-user-lng");

    if (!inputLocalisation) {
        return;
    }

    if (inputLat.value && inputLng.value) {
        inputLocalisation.value = "Position activée";
    }

    inputLocalisation.addEventListener("click", function () {

        if (!navigator.geolocation) {
            alert("La géolocalisation n'est pas supportée par votre navigateur.");
            return;
        }

        inputLocalisation.value = "Localisation en cours...";

        navigator.geolocation.getCurrentPosition(
            function (position) {
                inputLat.value = position.coords.latitude;
                inputLng.value = position.coords.longitude;
                inputLocalisation.value = "Position activée";
            },
            function (erreur) {
                inputLocalisation.value = "Ma position actuelle";
                alert("Impossible d'obtenir votre position. Vérifiez les autorisations du navigateur.");
            }
        );
    });

});