(function() {
    'use strict';

    angular
        .module('donight.filter')
        .controller('FilterController', FilterController);

    /* @ngInject */
    function FilterController($state, EventTypes) {
        var filterVm = this;

        filterVm.allEventTypes = EventTypes.query();

        filterVm.week = _.map(_.range(7), function(diff) {
            return moment().add(diff, 'day')
        });

        filterVm.calendarDay = function(day) {
            return day.calendar(moment(), {sameDay: 'הערב', nextDay: 'מחר', nextWeek: 'dddd'});
        };

        filterVm.filterDay = function(day) {
            $state.go('events.filter', {from: day.format('YYYY-MM-DD')});
        };

        filterVm.filterType = function(eventType) {
            $state.go('events.filter', {eventTypes: [eventType]});
        };
    }

})();
