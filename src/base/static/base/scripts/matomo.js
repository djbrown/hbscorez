var _paq = _paq || [];
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);
(function () {
    _paq.push(['setTrackerUrl', `${MATOMO_URL}piwik.php`]);
    _paq.push(['setSiteId', '1']);
    var $script = document.createElement('script');
    var $lastScript = document.getElementsByTagName('script')[0];
    $script.type = 'text/javascript';
    $script.async = true;
    $script.defer = true;
    $script.src = `${MATOMO_URL}piwik.js`;
    $lastScript.parentNode.insertBefore($script, $lastScript);
})();
