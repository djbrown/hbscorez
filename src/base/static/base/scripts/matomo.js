const _paq = window._paq = window._paq || [];
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);
(function () {
    _paq.push(['setTrackerUrl', `${MATOMO_URL}matomo.php`]);
    _paq.push(['setSiteId', '1']);
    const $script = document.createElement('script');
    const $lastScript = document.getElementsByTagName('script')[0];
    $script.type = 'text/javascript';
    $script.async = true;
    $script.src = `${MATOMO_URL}matomo.js`;
    $lastScript.parentNode.insertBefore($script, $lastScript);
})();
