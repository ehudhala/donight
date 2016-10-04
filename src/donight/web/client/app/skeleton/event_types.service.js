(function() {
    'use strict';

    angular
        .module('donight.filter', [])
        .factory('EventTypes', EventTypes);

    /* @ngInject */
    function EventTypes($resource) {
        return $resource('/api/event_types/all', {}, {
            query: {method: 'GET', isArray: true}
        });
    }

})();
