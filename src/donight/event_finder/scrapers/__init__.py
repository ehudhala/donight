from donight.config import facebook_scraping_config
from donight.event_finder.scrapers.facebook_events import FacebookEventsScraper
from donight.event_finder.scrapers.levontin7 import Levontin7Scraper
from donight.event_finder.scrapers.ozen_bar import OzenBarScraper


def get_all_scrapers():
    return [
        Levontin7Scraper(),
        OzenBarScraper(),
        get_facebook_scraper()
    ]


def get_facebook_scraper():
    return FacebookEventsScraper(email=facebook_scraping_config.EMAIL,
                                 password=facebook_scraping_config.PASSWORD,
                                 access_token=facebook_scraping_config.ACCESS_TOKEN,
                                 page_url=facebook_scraping_config.PAGE_URL,
                                 should_stop_scraping=facebook_scraping_config.SHOULD_STOP_SCRAPING)
