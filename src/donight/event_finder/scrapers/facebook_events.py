import json
import logging
import re
import time
from contextlib import contextmanager

import dateutil.parser
import facebook
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import keys

from donight.errors import EventScrapingError
from donight.event_finder.scrapers.base_scraper import Scraper
from donight.events import Event
from donight.utils.web_drivers import EnhancedWebDriver, By

assert __name__ != "facebook", "conflict with the facebook-sdk package name"


# TODO a more descriptive return value for self.get_scraping_source (including scraped page).
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
        :param driver: A selenium web driver. If not supplied, a firefox driver is created, but this requires firefox
                       to be installed. Currently tested for a firefox driver only.
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
        self.__graph_api_explorer_url = 'https://developers.facebook.com/tools/explorer'
        self.__is_already_refreshed = False

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
        :returns: Whether there were new posts to load. NOTE: returns a false negative if there's no internet connection
        :rtype: bool
        """
        driver.scroll_to_bottom()

        got_confused_error_message = 'Sorry, we got confused'
        try_refreshing_error_message = 'Please try refreshing the page'

        # wait up to 5 seconds for new posts to load
        for i in xrange(10):
            if driver.is_scrolled_to_bottom():
                time.sleep(0.5)
            else:
                return True

        if driver.has_element(By.XPATH,
                              '//*[@role="dialog"][//*[contains(text(),{})]][//*[contains(text(),{})]]'.format(
                                  json.dumps(got_confused_error_message), json.dumps(try_refreshing_error_message))):
            if self.__is_already_refreshed:
                raise EventScrapingError('Facebook is not reacting properly: received "{}" error twice.'.format(
                    try_refreshing_error_message))

            driver.refresh()
            self.__is_already_refreshed = True
            self.logger.warn('Received an error from facebook: "{}". Refreshing and retrying'.format(
                try_refreshing_error_message))
            # We're returning a possibly incorrect value without loading new posts.
            # ASSUMPTION: other parts of the code will handle this.
            return True

        self.logger.info("It seems no there are no more events to scrape from the page {}".format(self.__page_url))
        return False

    def __scrape_access_token(self, driver):
        with driver.new_tab(self.__graph_api_explorer_url):
            # ASSUMPTION: not logged in. logging in:
            email_input = driver.find_element_by_id('email')
            email_input.send_keys(self.__email)

            password_input = driver.find_element_by_id('pass')
            password_input.send_keys(self.__password)
            password_input.send_keys(keys.Keys.ENTER)

            if not driver.current_url.startswith(self.__graph_api_explorer_url):
                raise EventScrapingError('Email or password seem to be incorrect.')

            # refresh access token:
            # ASSUMPTION: the 'user_events' permission has already been given to the GraphApi Explorer by that user.
            get_token_button = driver.find_element_by_link_text('Get Token')
            get_token_button.click()
            get_user_access_token_button = driver.find_element_by_link_text('Get User Access Token')
            get_user_access_token_button.click()

            possible_get_access_token_submit_buttons = driver.find_elements_by_css_selector('button[type="submit"]')
            for button in possible_get_access_token_submit_buttons:
                if button.get_attribute('textContent') == 'Get Access Token':
                    break
            else:
                raise NoSuchElementException("Can't find the 'Get Access Token' submit button.")

            button.click()

            access_token_output = driver.find_element_by_css_selector(
                "input[placeholder='Paste in an existing Access Token or click \"Get User Access Token\"']")
            access_token = access_token_output.get_attribute('value')
            return access_token


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

        start_time = event_dict.get("start_time")
        end_time = event_dict.get("end_time")
        event = Event(title=event_dict.get("name"),
                      start_time=self.__parse_datetime(start_time),
                      end_time=self.__parse_datetime(end_time),
                      location=event_dict.get("place", {}).get("name"),  # coordinates and id also available
                      price=None,  # TODO parse
                      url="https://www.facebook.com/events/" + event_dict.get("id", event_id),
                      description=description,
                      image=event_dict.get("cover", {}).get("source"))
        return event

    def __parse_datetime(self, string):
        if string is None:
            return None

        return dateutil.parser.parse(string)


class AuthError(Exception):
    pass
