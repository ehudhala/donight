import re
from contextlib import contextmanager
import time

import facebook
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from donight.errors import EventScrapingError
from donight.event_finder.scrapers.base_scraper import Scraper
from donight.events import Event
from donight.utils import Counter
from donight.utils.web_drivers import EnhancedWebDriver

assert __name__ != "facebook", "conflict with the facebook-sdk package name"


class FacebookEventsScraper(Scraper):
    __LOADING_POSTS_GUI_LOCATOR = (By.CLASS_NAME, 'uiMorePagerLoader')

    def __init__(self, access_token, page_url, should_stop_scraping, driver=None, logger=None):
        """
        :type page_url: basestring
        :param access_token: An access token of a user with permissions to access the `page_url` and the 'user_events'
                             permission set on. Get it from https://developers.facebook.com/tools/explorer
        :type access_token: basestring
        :param should_stop_scraping: A function accepting an Event and returning whether to stop scraping more events.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver|None
        """
        super(FacebookEventsScraper, self).__init__(logger)
        self.__page_url = page_url
        self.__access_token = access_token  # TODO scrape access token?
        self.__should_stop_scraping = should_stop_scraping
        self.__driver = driver
        self.__event_id_regex_in_url = re.compile(r'/events/(?P<id>\d+)($|/|\?).*')

    def scrape(self):
        # TODO consider using the /events page present in some types of pages (e.g. groups): fb.com/groups/123/events
        event_scraper = FacebookEventScraper(self.__access_token)

        with self.__get_driver() as driver:
            driver.maximize_window()

            driver.get(self.__page_url)

            for event_id in self.__iterate_unique_events_ids(driver):
                try:
                    event = event_scraper.scrape(event_id)

                except EventScrapingError:
                    self.logger.exception('Error scraping facebook event with id {}.'.format(event_id))
                    continue

                yield event

                if self.__should_stop_scraping(event):
                    self.logger.warn("Reached events threshold.")
                    break

    @contextmanager
    def __get_driver(self):
        if self.__driver is None:
            should_quit_driver = True
            driver = selenium.webdriver.Firefox()
        else:
            should_quit_driver = False
            driver = self.__driver

        try:
            driver = EnhancedWebDriver(driver)

            yield driver

        finally:
            if should_quit_driver:
                driver.quit()

    def __iterate_unique_events_ids(self, driver):
        scraped_events_ids = set()

        for event_anchor in self.__iterate_events_anchors(driver):
            event_url = event_anchor.get_attribute('href')

            event_id = self.__parse_event_id(event_url)

            if event_id in scraped_events_ids:
                continue
            else:
                # assuming that if the scraping later fails, it will always fail for this id.
                scraped_events_ids.add(event_id)

            yield event_id

    def __parse_event_id(self, event_url):
        match = self.__event_id_regex_in_url.search(event_url)
        if match is not None:
            return match.group('id')

        raise EventScrapingError("Unable to parse facebook event id from url: {}".format(event_url))

    def __iterate_events_anchors(self, driver):
        while True:
            try:
                event_anchor = driver.find_element_by_css_selector('a[href*="/events/"]:not([data-already-handled])')

            except NoSuchElementException:
                if self.__load_more_posts(driver):
                    continue
                else:
                    break

            driver.execute_script('arguments[0].setAttribute("data-already-handled", "true");',
                                  event_anchor)

            if self.__event_id_regex_in_url.search(event_anchor.get_attribute('href')) is None:
                # That's not really an event anchor
                continue

            yield event_anchor

    def __load_more_posts(self, driver):
        """
        :returns: Whether there were new posts to load
        :rtype: bool
        """
        driver.scroll_to_bottom()
        time.sleep(0.5)

        try:
            loading_posts_gui_element = driver.find_element(self.__LOADING_POSTS_GUI_LOCATOR)

        except NoSuchElementException:
            is_no_more_posts_to_load = True

        except:
            raise

        else:
            is_no_more_posts_to_load = loading_posts_gui_element.is_displayed()

        if is_no_more_posts_to_load:
            self.logger.info("It seems no there are no more events to scrape from the page {}".format(self.__page_url))
            return False

        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located(self.__LOADING_POSTS_GUI_LOCATOR))
        except TimeoutException as e:
            raise EventScrapingError("Facebook is taking too long to load new posts. "
                                     "Please check for internet connectivity issues and try again. "
                                     "If the issue persists, debug the code.", e)

        return True


class FacebookEventScraper(object):
    """docs at https://developers.facebook.com/docs/graph-api/reference/event/"""

    def __init__(self, access_token):
        self.__graph = facebook.GraphAPI(access_token, version='2.5')

    def scrape(self, event_id):
        try:
            event_dict = self.__graph.get_object(
                event_id,
                fields="place,name,description,start_time,end_time,ticket_uri,can_guests_invite,cover")
        except facebook.GraphAPIError as e:
            raise EventScrapingError("Could not access facebook event with id {}.".format(event_id), e)

        if not event_dict.get("can_guests_invite"):
            # TODO what if scraped for personal use?
            raise EventScrapingError("Event does not allow inviting guests")

        description = event_dict.get("description")
        ticket_url = event_dict.get("ticket_uri")
        if ticket_url:
            description += '\nTicket: ' + event_dict.get("ticket_uri")

        event = Event(title=event_dict.get("name"),
                      time=event_dict.get("start_time"),
                      end_time=event_dict.get("end_time"),
                      location=event_dict.get("place", {}).get("name"),  # coordinates and id also available
                      price=None,  # TODO parse
                      url="https://www.facebook.com/events/" + event_dict.get("id", event_id),
                      description=description,
                      image=event_dict.get("cover", {}).get("source"))
        return event


if __name__ == '__main__':  # TODO remove
    s = FacebookEventsScraper(
        NotImplemented,  # TODO add access token to test this
        "https://www.facebook.com/hanasich",
        Counter(100).has_reached_threshold)

    try:
        for event in s.scrape():
            s.logger.debug(unicode(event))
    except Exception as e:
        print repr(e)
        import traceback
        traceback.print_exc()

        raise
