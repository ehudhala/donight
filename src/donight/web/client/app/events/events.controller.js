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

        var specialPriceDisplays = {
            '': 'לא ידוע',
            '0': 'חינם !'
        };

        eventsVm.priceDisplay = function(event) {
            var specialDisplay = specialPriceDisplays[event.price];
            return specialDisplay !== undefined ? specialDisplay : event.price + '₪';
        };

        eventsVm.filteredEvents = function(events) {
            console.log($state.params);
            return _.filter(events, function(event) {
                var dateFilter = !$state.params.from ||
                       event.start_time.isSameOrAfter(moment.utc($state.params.from), 'day');

                var typeFilter = !$state.params.eventTypes ||
                        _.contains($state.params.eventTypes, event.event_type_name);

                return dateFilter && typeFilter;
            });
        };
    }

})();
