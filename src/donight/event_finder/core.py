import time
from itertools import chain, imap
from logging import getLogger

from sqlalchemy import func

from donight.config.consts import TIME_BETWEEN_INDEXES
from donight.event_finder.scrapers import Scraper, get_all_scrapers
from donight.events import Session, Event
from donight.utils import get_model_fields


class EventFinder(object):
    """
    This class is used to find events using scrapers,
    and upload all the events to the DB.
    """
    # TODO: Add tests !.
    # TODO: Add tests for the scrapers (against the real internet) !.
    def __init__(self, scrapers=None, session=None, logger=None):
        """
        :param scrapers: A list of scrapers, from which to scrape events and upload to the DB.
        :type scrapers: list(Scraper)
        :param session: A sessions to the DB.
        :type session: Session
        :param logger: Defaults to the logger with the module name.
        :type logger: logging.Logger
        """
        self.scrapers = scrapers or get_all_scrapers()
        self.session = session or Session()
        self.logger = logger or getLogger(__name__)

    def index_forever(self, seconds_between_indexes=TIME_BETWEEN_INDEXES):
        """
        Run as a service, and every given time, index the events from all scrapers.
        This keeps the DB always up-to-date because we update the information on changed events.
        :param seconds_between_indexes: The time to wait between indexes
            (we don't need to index every minute, events don't change that often)
        :type seconds_between_indexes: int
        """
        start_time = time.time()
        self.logger.info("Starting to index events every %d seconds (%d hours)", seconds_between_indexes, seconds_between_indexes / 3600)
        while True:
            try:
                self.index_events()
                time.sleep(seconds_between_indexes - ((time.time() - start_time) % seconds_between_indexes))
            except Exception:
                self.logger.exception("Failed to index events, retrying, exception:")

    def index_events(self):
        """
        Indexes events from all the scrapers.
        Uses each scraper to scrape events, then uploads everything to the db
        (updating existing events or creating new ones)
        """
        all_scraper_names = ', '.join([scraper.get_scraping_source() for scraper in self.scrapers])
        self.logger.info("Indexing events from: %s", all_scraper_names)

        all_events = list(chain.from_iterable(imap(self.safely_scrape, self.scrapers)))

        events_amount = len(all_events)
        self.logger.info("Uploading to the db %d events from: %s", events_amount, all_scraper_names)

        updated = self.upload_to_db(all_events)

        self.logger.info("Finished uploading to the db %d events (%d created, %d updated) from: %s",
                         events_amount, events_amount - updated, updated, all_scraper_names)

    def safely_scrape(self, scraper):
        """
        Used to scrape events from a scraper, but not fail everything if the scraper fails.
        :param scraper: A scraper to scrape events from.
        :type scraper: Scraper
        :return: A list of events scraped from the scraper.
        :rtype: list(Event)
        """
        self.logger.info('Scraping events from %s', scraper.get_scraping_source())
        events = []

        try:
            events.extend([event for event in scraper.scrape() if event and event.title != ''])
        except Exception:
            self.logger.exception("Failed scraping events from %s. Still scraping from other sources. Exception:",
                                  scraper.get_scraping_source())
        finally:
            self.logger.info('Scraped %d events from %s', len(events), scraper.get_scraping_source())

        return events

    def upload_to_db(self, events):
        """
        Uploads all the given events to the db.
        Uploading an event doesn't necessarily mean adding it to the db.
        If the event exists in the db, we only update its information,
        If it doesn't exist yet we update it.
        We return the amount of events updated (and not added).
        :param events: The events to upload to the db.
        :type events: list(Event)
        :return: The amount of updated events.
        :rtype: int
        """
        updated = 0

        for event in filter(None, events):
            existing_similar_event = self.get_similar_event(event)

            if existing_similar_event is not None:
                self.update_in_db(existing_similar_event, event)
                updated += 1
            else:
                self.add_to_db(event)

        self.session.commit()
        return updated

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
            func.date(Event.start_time) == event.start_time.date()).first()

    def add_to_db(self, event):
        """
        Adds the event to the db.
        :param event: The event to upload to the db.
        """
        self.session.add(event)

    def update_in_db(self, existing_event, event):
        """
        Gets two events, one that already exists,
        and one that holds new information we want to insert into the existing event.
        Updates the existing event to hold the information from the given event.
        :param existing_event: An event that already exists in the db, to update with new information.
        :type existing_event: Event
        :param event: An event to get the new information from.
        :type event: Event
        """
        for field_name in get_model_fields(Event, ['id']):
            new_field_value = getattr(event, field_name)
            setattr(existing_event, field_name, new_field_value)

