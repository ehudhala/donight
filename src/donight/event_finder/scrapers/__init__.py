from donight.config import facebook_scraping_config
from donight.event_finder.scrapers.facebook_events import FacebookEventsScraper
from donight.event_finder.scrapers.levontin7 import Levontin7Scraper
from donight.event_finder.scrapers.ozen_bar import OzenBarScraper
from donight.utils.web_drivers import EnhancedWebDriver


def get_all_scrapers():
    return [
        Levontin7Scraper(),
        OzenBarScraper()
    ] + get_facebook_scrapers()


def get_facebook_scrapers():
    driver = EnhancedWebDriver.get_instance()
    driver.maximize_window()
    return [FacebookEventsScraper(driver=driver, **kwargs)
            for kwargs in facebook_scraping_config.facebook_scraped_pages]
