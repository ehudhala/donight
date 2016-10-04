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
                state: 'events',
                config: {
                    url: '/',
                    templateUrl: '/static/build/events/events.html',
                    controller: 'EventsController as eventsVm'
                }
            },
            {
                state: 'events.filter',
                config: {
                    url: 'events?from&eventTypes',
                    params: {
                        from: null,
                        eventTypes: {
                            array: true
                        }
                    },
                    templateUrl: '/static/build/events/events.html',
                    controller: 'EventsController as eventsVm'
                }
            }
        ];
    }

})();
