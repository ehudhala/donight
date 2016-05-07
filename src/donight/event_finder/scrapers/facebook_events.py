import json
import logging
import re
from contextlib import contextmanager
import time

import facebook
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from donight.errors import EventScrapingError
from donight.event_finder.scrapers.base_scraper import Scraper
from donight.events import Event
from donight.utils import Counter
from donight.utils.web_drivers import EnhancedWebDriver

assert __name__ != "facebook", "conflict with the facebook-sdk package name"


class FacebookEventsScraper(Scraper):
    def __init__(self, **kwargs):
        """
        :param page_url: The page to be scraped. Use https://facebook.com/me to scrape your wall.
        :type page_url: basestring

        User authentication data:
        :param access_token: An access token of a user with permissions to access the `page_url` and the 'user_events'
                             permission set on. Get it from https://developers.facebook.com/tools/explorer
        :type access_token: basestring|None
        --- or: ---
        :type email: basestring|None
        :type password: basestring|None

        :param should_stop_scraping: A function accepting an Event and returning whether to stop scraping more events.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver|None
        :type logger: logging.Logger|None
        """
        super(FacebookEventsScraper, self).__init__(kwargs.pop('logger', None))

        self.__access_token = kwargs.pop('access_token', None)
        self.__email = kwargs.pop('email', None)
        self.__password = kwargs.pop('password', None)
        if (self.__access_token is None) and (self.__email is None or self.__password is None):
            raise TypeError('Expecting an access token or email and password.')

        self.__page_url = kwargs.pop('page_url')
        self.__should_stop_scraping = kwargs.pop('should_stop_scraping')
        self.__driver = kwargs.pop('driver', None)

        if kwargs:
            raise TypeError('Received some redundant arguments: {}'.format(', '.join(kwargs.keys())))

        self.__event_id_regex_in_url = re.compile(r'/events/(?P<id>\d+)($|/|\?).*')
        self.__loading_posts_gui_class_name = 'uiMorePagerLoader'

    def scrape(self):
        # TODO consider using the /events page present in some types of pages (e.g. groups): fb.com/groups/123/events

        with self.__get_driver() as driver:
            driver.maximize_window()
            event_scraper = FacebookEventScraper(self.__access_token or self.__scrape_access_token(driver))
            driver.get(self.__page_url)

            for event_id in self.__iterate_unique_events_ids(driver):
                try:
                    event = event_scraper.scrape(event_id)

                except AuthError:
                    if self.__email is None or self.__password is None:
                        raise

                    event_scraper = FacebookEventScraper(self.__scrape_access_token(driver))

                    try:
                        event = event_scraper.scrape(event_id)

                    except EventScrapingError:
                        self.logger.exception('Error scraping facebook event with id {}.'.format(event_id))
                        continue

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

        are_there_more_posts_to_load = driver.execute_script(
            'var loadingGuiElements = document.getElementsByClassName({});'
            'lastLoadingElement = loadingGuiElements[loadingGuiElements.length - 1];'
            'return getComputedStyle(lastLoadingElement).displayed != "none";'.format(
                json.dumps(self.__loading_posts_gui_class_name)))

        if not are_there_more_posts_to_load:
            self.logger.info("It seems no there are no more events to scrape from the page {}".format(self.__page_url))
            return False

        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, self.__loading_posts_gui_class_name)))
        except TimeoutException as e:
            raise EventScrapingError("Facebook is taking too long to load new posts. "
                                     "Please check for internet connectivity issues and try again. "
                                     "If the issue persists, debug the code.", e)

        return True

    def __scrape_access_token(self, driver):
        GRAPH_API_EXPLORER_URL = 'https://developers.facebook.com/tools/explorer'
        driver.get(GRAPH_API_EXPLORER_URL)

        # ASSUMPTION: not logged in. logging in:
        email_input = driver.find_element_by_id('email')
        email_input.send_keys(self.__email)

        password_input = driver.find_element_by_id('pass')
        password_input.send_keys(self.__password)
        password_input.send_keys(keys.Keys.ENTER)

        if not driver.current_url.startswith(GRAPH_API_EXPLORER_URL):
            raise EventScrapingError('Email or password seem to be incorrect.')

        # refresh access token
        # ASSUMPTION: the 'user_events' permission has already been given to the GraphApi Explorer by that user.
        driver.body.send_keys(Keys.ALT + 'T')  # refresh access token only if it's expired

        access_token_output = driver.find_element_by_css_selector(
            "input[placeholder='Paste in an existing Access Token or click \"Get User Access Token\"']")
        return access_token_output.get_attribute('value')


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
            if e.type == 'OAuthException':
                raise AuthError(e)

            raise EventScrapingError("Could not access facebook event with id {}.".format(event_id), e)

        if not event_dict.get("can_guests_invite"):
            # TODO what if scraped for personal use?
            raise EventScrapingError("Event does not allow inviting guests")

        description = event_dict.get("description")
        ticket_url = event_dict.get("ticket_uri")
        if ticket_url:
            description += '\nTicket: ' + event_dict.get("ticket_uri")

        event = Event(title=event_dict.get("name"),
                      start_time=event_dict.get("start_time"),
                      end_time=event_dict.get("end_time"),
                      location=event_dict.get("place", {}).get("name"),  # coordinates and id also available
                      price=None,  # TODO parse
                      url="https://www.facebook.com/events/" + event_dict.get("id", event_id),
                      description=description,
                      image=event_dict.get("cover", {}).get("source"))
        return event


class AuthError(Exception):
    pass


def main():  # TODO delete
    with open(r'config\personal-data\facebook-auth-data.json') as f:
        facebook_auth_data = json.load(f)

    # create logger
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    s = FacebookEventsScraper(
        access_token=facebook_auth_data.get('access_token'),
        email=facebook_auth_data.get('email'),
        password=facebook_auth_data.get('password'),
        page_url="https://www.facebook.com/hanasich",
        should_stop_scraping=Counter(100).has_reached_threshold,
        logger=logger)

    try:
        for event in s.scrape():
            print(unicode(event))
    except Exception as e:
        print repr(e)
        import traceback

        traceback.print_exc()

        raise


if __name__ == '__main__':  # TODO delete
    main()