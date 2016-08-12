(function() {
    'use strict';

    angular
        .module('donight', [
            // Angular libraries.
            'ngAnimate', 'ngResource', 'ngSanitize',
            // External libraries.
            'ui.bootstrap', 'ui.router', 'ui.select',
            // Donight dependencies
            'angularMoment', 'hm.readmore',
            // App modules
            'blocks.router', 'donight.utils', 'donight.events'
        ])
        .run(setGlobalState);

    /* @ngInject */
    function setGlobalState($rootScope, $state, $stateParams, amMoment) {
        // It's very handy to add references to $state and $stateParams to the $rootScope
        // so that you can access them from any scope within your applications.For example,
        // <li ng-class="{ active: $state.includes('contacts.list') }"> will set the <li>
        // to active whenever 'contacts.list' or one of its descendants is active.
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;

        amMoment.changeLocale('he');
    }

})();
