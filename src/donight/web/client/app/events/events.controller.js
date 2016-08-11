(function() {
    'use strict';

    angular
        .module('donight.events', [])
        .controller('EventsController', EventsController);

    /* @ngInject */
    function EventsController(Events) {
        var eventsVm = this;

        eventsVm.events = Events;

        eventsVm.priceDisplay = function(event) {
            return event.price !== '' ? event.price + '₪' : 'לא ידוע';
        }
    }

})();