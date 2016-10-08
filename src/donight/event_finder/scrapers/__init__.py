from donight.config import facebook_scraping_config
from donight.event_finder.scrapers.base_scraper import Scraper
from donight.event_finder.scrapers.facebook_events import FacebookEventsScraper, FacebookScrapingWebDriver
from donight.event_finder.scrapers.levontin7 import Levontin7Scraper
from donight.event_finder.scrapers.ozen_bar import OzenBarScraper
from donight.event_finder.scrapers.shows_around import ShowsAroundScraper


def get_all_scrapers():
    return [
        Levontin7Scraper(),
        OzenBarScraper(),
        ShowsAroundScraper()
    ] + get_facebook_scrapers()


def get_facebook_scrapers():
    driver = FacebookScrapingWebDriver(facebook_scraping_config.should_hide_browser_window,
                                       facebook_scraping_config.browser_installation_path)
    driver.maximize_window()

    return [FacebookEventsScraper(driver=driver, **kwargs)
            for kwargs in facebook_scraping_config.facebook_scraped_pages]
