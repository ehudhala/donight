import time
from itertools import chain, imap

from sqlalchemy import func

from donight.config import TIME_BETWEEN_INDEXES
from donight.event_finder.scrapers import ALL_SCRAPERS
from donight.events import Session, Event


class EventFinder(object):
    """
    This class is used to find events using scrapers,
    and upload all the events to the DB.
    """
    # TODO: Make everything more stable (don't let exceptions fail everything).
    # TODO: Add logs EVERYWHERE !.
    # TODO: Add tests !.
    # TODO: Add tests for the scrapers (against the real internet) !.
    def __init__(self, scrapers=ALL_SCRAPERS, session=None):
        """
        :param scrapers: A list of scrapers, from which to scrape events and upload to the DB.
        :type scrapers: list(Scraper)
        :param session: A sessions to the DB.
        :type session: Session
        """
        self.scrapers = scrapers
        self.session = session or Session()

    def index_forever(self, seconds_between_indexes=TIME_BETWEEN_INDEXES):
        """
        Run as a service, and every given time, index the events from all scrapers.
        This keeps the DB always up-to-date because we update the information on changed events.
        :param seconds_between_indexes: The time to wait between indexes
            (we don't need to index every minute, events don't change that often)
        :type seconds_between_indexes: int
        """
        start_time = time.time()
        while True:
            try:
                self.index_events()
                time.sleep(seconds_between_indexes - ((time.time() - start_time) % seconds_between_indexes))
            except Exception as e:
                # TODO: log
                pass

    def index_events(self):
        """
        Indexes events from all the scrapers.
        Uses each scraper to scrape events, then uploads everything to the db
        (updating existing events or creating new ones)
        """
        all_events = chain.from_iterable(imap(self.safely_scrape, self.scrapers))
        for event in filter(None, all_events):
            self.add_or_update(event)

    def safely_scrape(self, scraper):
        """
        Used to scrape events from a scraper, but not fail everything if the scraper fails.
        :param scraper: A scraper to scrape evvents from.
        :type scraper: Scraper
        :return: A list of events scraped from the scraper.
        :rtype: list(Event)
        """
        try:
            return scraper.scrape()
        except Exception as e:
            # TODO: log something here
            print 'Exception: ', e
            return list()

    def get_similar_event(self, event):
        """
        Given an event, this function finds an event that is similar to it
        (meaning it is actually the same event, with small variances in information).
        :param event: An event to find a similar event to.
        :type event: Event
        :return: An event that is similar to the given event, or None if no such event exists.
        :rtype: Event or None
        """
        # TODO: change string equals to Levenshtein distance.
        return self.session.query(Event).filter(
            Event.title == event.title,
            Event.location == event.location,
            func.date(Event.time) == event.time.date()).first()

    def add_or_update(self, event):
        """
        Adds the event to the db.
        If the event already exists, we update the information to include the new information on the event.
        :param event: The event to upload to the db.
        """
        existing_similar_event = self.get_similar_event(event)
        if existing_similar_event is not None:
            self.session.delete(existing_similar_event)
        self.session.add(event)
        self.session.commit()

