(function() {
    'use strict';

    angular
        .module('donight')
        .config(config);

    /* @ngInject */
    function config($compileProvider, $httpProvider) {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(http|https):/);

        $httpProvider.defaults.transformResponse.push(function(responseData) {
            convertDateStringsToDates(responseData);
            return responseData;
        });
    }

    var regexIso8601 = /^(\d{4}|\+\d{6})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2}):(\d{2}):(\d{2})(\.(\d{1,}))?(Z|([\-+])(\d{2}):(\d{2}))?)?)?)?$/;

    function convertDateStringsToDates(input) {
        // Ignore things that aren't objects.
        if (typeof input !== 'object') {
            return input;
        }

        for (var key in input) {
            if (!input.hasOwnProperty(key)) {
                continue;
            }

            var value = input[key];
            var match;
            if (typeof value === 'string' && (match = value.match(regexIso8601))) {
                var milliseconds = Date.parse(match[0]);
                if (!isNaN(milliseconds)) {
                    input[key] = moment.utc(milliseconds);
                }
            } else if (typeof value === 'object') {
                // Recurse into object
                convertDateStringsToDates(value);
            }
        }
    }

})();
