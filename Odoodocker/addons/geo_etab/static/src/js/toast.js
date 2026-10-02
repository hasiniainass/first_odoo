document.addEventListener("DOMContentLoaded", function () {

    var toast = document.getElementById("geo-toast-bienvenue");
    if (!toast) {
        return;
    }

    setTimeout(function () {
        toast.classList.add("geo-toast-out");

        setTimeout(function () {
            toast.remove();
        }, 500);

    }, 3000);

});