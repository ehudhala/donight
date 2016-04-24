import sys

from donight.applications.events_to_excel import EventsExcel
from donight.event_finder import EventFinder
from donight.events import Session, Event


def load_events_to_excel(events_file_name):
    session = Session()
    events = session.query(Event).all()
    EventsExcel().create_excel(events, events_file_name)


if __name__ == '__main__':
    events_file_name = 'events.xlsx'
    if len(sys.argv) > 1:
        events_file_name = sys.argv[1]

    EventFinder().index_events()

    load_events_to_excel(events_file_name)
