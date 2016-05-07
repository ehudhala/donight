from itertools import groupby
from pyexcelerate import Workbook

from donight.events import Event
from donight.utils import get_model_fields


class EventsExcel(object):
    """
    Used to turn information about events into an excel spreadsheet.
    """
    EXCLUDED_FIELDS = ['id']
    FIELD_NAMES = get_model_fields(Event, EXCLUDED_FIELDS)

    def create_excel(self, events, events_file_name):
        """
        Gets a list of events, and a destination file name.
        It creates an excel spreadsheet containing information about all the events given, split up by the day.
        The format of the spreadsheet is:
        a header line with column names,
        then for every day a line with only the day,
        then for every event of that day all the information about the event.
        :param events: The events to write to the excel.
        :type events: list(Event)
        :param events_file_name: The name of the final excel file.
        :type events_file_name: str
        """
        events = list(sorted(events, key=lambda event: event.start_time))
        workbook = Workbook()
        events_data = [map(unicode.title, self.FIELD_NAMES)]

        for day, day_events in groupby(events, key=lambda event: event.start_time.date()):
            events_data += [[unicode(day)]]
            events_data += map(self.get_attributes, day_events)

        workbook.new_sheet('Events', data=events_data)
        workbook.save(events_file_name)

    def get_attributes(self, event, attributes=FIELD_NAMES):
        """
        Gets an event, and a list of attributes to get from that event,
        and returns a list of all those attributes from the event.
        :param event: The event to get the attributes of.
        :type event: Event
        :param attributes: A list of attributes to get from the event.
        :type attributes: list(str)
        :return: A list of the values of the attributes in the event.
        :rtype: list
        """
        return [unicode(getattr(event, attr)) for attr in attributes]

