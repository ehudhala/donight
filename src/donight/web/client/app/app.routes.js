(function() {
    'use strict';

    angular
        .module('donight')
        .run(appRun);

    /* @ngInject */
    function appRun(routerHelper) {
        routerHelper.configureStates(getStates(), '/');
    }

    function getStates() {
        return [
            {
                state: 'home',
                config: {
                    url: '/',
                    templateUrl: '/static/build/home/home.html'
                }
            },
            {
                state: 'events',
                config: {
                    url: '/events',
                    templateUrl: '/static/build/events/events.html',
                    controller: 'EventsController as eventsVm'
                }
            }
        ];
    }

})();
