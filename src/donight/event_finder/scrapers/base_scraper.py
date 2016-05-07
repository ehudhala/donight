from abc import ABCMeta, abstractmethod
from logging import getLogger


class Scraper(object):
    """
    This is an interface for scrapers.
    Scrapers are used to scrape a specific source's events.
    The only method that must be implemented is scrape, which returns a list of events,
    and all the logic of scraping the source should be implemented in this class.
    """
    __metaclass__ = ABCMeta

    def __init__(self, logger=None):
        """
        A scraper defaultly has a logger,
        it should be used to log important events, mainly failing to scrape events.
        The reason it is important to log scraper failures
        is because we want to know if our scrapers fail (some of our sources chaned their api).
        :param logger: A scraper can get a logger, defaults to the module name logger.
        :type logger: logging.Logger
        """
        self.logger = logger or getLogger(self.__module__)

    @abstractmethod
    def scrape(self):
        """
        This is the main method of a scraper.
        It should be used to scrape events from a single source.
        There are different methods of scraping different sources,
        but this method must eventually return a list of Event objects.
        Tip: The scraper can raise an exception and it will be handled,
        but then the scrapers events won't be used,
        so the scraper itself should handle exceptions, and return as many events as it can,
        while logging failures.
        :return: A list of events from the scraped source.
        :rtype: list(Event)
        """
        pass

    @classmethod
    def get_scraping_source(cls):
        """
        Returns a descriptive title for the source this scraper is scraping,
        usually it will just be the name of the scraper, but this method can be overridden.
        :return: The source this scraper is scraping.
        :rtype: str
        """
        return cls.__name__.replace('Scraper', '').replace('Events', '').replace('Event', '')
