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
            return _.filter(events, function(event) {
                return $state.params.startDate === undefined ||
                       event.start_time.isSameOrAfter(moment.utc($state.params.startDate), 'day');
            });
        };
    }

})();
