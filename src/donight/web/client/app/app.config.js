(function() {
    'use strict';

    angular
        .module('donight')
        .config(config);

    /* @ngInject */
    function config($compileProvider, $httpProvider) {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(http|https):/);
    }

})();
