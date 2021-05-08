window.addEventListener("load", function () {
    window.cookieconsent.initialise({
        "palette": {
            "popup": {
                "background": "#007bff",
                "text": "#ffffff"
            },
            "button": {
                "background": "#ffffff",
                "text": "#007bff"
            }
        },
        "theme": "classic",
        "content": {
            "message": "Cookies erleichtern die Bereitstellung dieser Webseite. Mit der Nutzung der Webseite erklärst Du Dich damit einverstanden, dass sie Cookies verwendet.",
            "dismiss": "Verstanden!",
            "link": "Mehr erfahren",
            "href": "https://support.mozilla.org/de/kb/cookies-informationen-websites-auf-ihrem-computer"
        }
    });
});
