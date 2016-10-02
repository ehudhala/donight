(function() {
    'use strict';

    angular
        .module('donight.events')
        .factory('Event', Event)
        .factory('Events', Events);

    /* @ngInject */
    function Event($resource) {
        return $resource('/api/events/all', {}, {
            query: {method: 'GET', isArray: true}
        });
    }

    /* @ngInject */
    function Events(Event) {
        return Event.query();
    }

})();
