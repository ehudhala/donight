(function() {
    'use strict';

    angular
        .module('donight.events', [])
        .controller('EventsController', EventsController);

    /* @ngInject */
    function EventsController(Events, $state) {
        var eventsVm = this;

        eventsVm.events = Events;

        eventsVm.getPrice = function(event) {
            var price = event.price !== '' ? event.price.split('/')[0] : -1;
            return Number(price);
        };

        eventsVm.priceDisplay = function(event) {
            return event.price !== '' ? event.price + '₪' : 'לא ידוע';
        };

        eventsVm.filteredEvents = function(events) {
            return _.filter(events, function(event) {
                return $state.params.startDate === undefined ||
                       event.start_time.isSameOrAfter(moment.utc($state.params.startDate), 'day');
            });
        };
    }

})();
