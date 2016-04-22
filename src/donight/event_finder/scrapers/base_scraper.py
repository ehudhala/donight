from abc import ABCMeta, abstractmethod


class BaseScraper(object):
    """
    This is an interface for scrapers.
    Scrapers are used to scrape a specific source's events.
    The only method that must be implemented is scrape, which returns a list of events,
    and all the logic of scraping the source should be implemented in this class.
    """
    __metaclass__ = ABCMeta

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
