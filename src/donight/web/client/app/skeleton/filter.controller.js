(function() {
    'use strict';

    angular
        .module('donight.filter', [])
        .controller('FilterController', FilterController);

    /* @ngInject */
    function FilterController($state) {
        var filterVm = this;

        filterVm.week = _.map(_.range(7), function(diff) {
            return moment().add(diff, 'day')
        });

        filterVm.calendarDay = function(day) {
            return day.calendar(moment(), {sameDay: 'היום', nextDay: 'מחר', nextWeek: 'dddd'});
        };

        filterVm.filterDay = function(day) {
            $state.go('events.filter', {startDate: day.format('YYYY-MM-DD')});
        };
    }

})();
