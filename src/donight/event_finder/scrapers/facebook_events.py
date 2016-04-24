import re
import time

import facebook
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from donight.errors import EventScrapingError
from donight.events import Event
from donight.utils import Counter

assert __name__ != "facebook", "conflict with the facebook-sdk package name"


class FacebookEventsScraper(object):
    # TODO consider using the /events page present in some types of pages (e.g. groups): facebook.com/groups/123/events

    def __init__(self, access_token, page_url, should_stop_scraping, driver=None):
        """
        :type page_url: basestring
        :param access_token: An access token of a user with permissions to `page_url` and the 'user_events' permission
                             on. Get it from https://developers.facebook.com/tools/explorer
        :type access_token: basestring
        :param should_stop_scraping: A function accepting an Event and returning whether to stop scraping more events.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver|None
        """
        self.__page_url = page_url
        self.__access_token = access_token  # TODO scrape access token?
        self.__should_stop_scraping = should_stop_scraping
        self.__driver = driver
        self.__event_id_regex_in_url = re.compile(r'/events/(?P<id>\d+)($|/|\?).*')

    # TODO refactor the shit out of this
    def scrape(self):
        event_scraper = FacebookEventScraper(self.__access_token)
        scraped_events_ids = set()

        should_quit_driver = False
        driver = self.__driver

        if driver is None:
            should_quit_driver = True
            driver = selenium.webdriver.Firefox()

        try:
            driver.maximize_window()
            driver.get(self.__page_url)

            loading_posts_gui_locator = (By.CLASS_NAME, 'uiMorePagerLoader')
            while True:
                try:
                    unscraped_event_anchor = driver.find_element_by_css_selector(
                        'a[href*="/events/"]:not([data-already-scraped])')

                except NoSuchElementException:
                    # load more events
                    driver.execute_script('window.scrollBy(0, document.body.scrollHeight);')
                    time.sleep(0.5)  # wait for browser to respond and create a 'loading' GUI

                    try:
                        loading_posts_gui_element = driver.find_element(loading_posts_gui_locator)
                        is_no_more_posts_to_load = loading_posts_gui_element.is_displayed()
                    except NoSuchElementException:
                        is_no_more_posts_to_load = True

                    if is_no_more_posts_to_load:
                        print("It seems no there are no more events to scrape from the page {}".format(self.__page_url))
                        break

                    try:
                        WebDriverWait(driver, 10).until(
                            EC.invisibility_of_element_located(loading_posts_gui_locator))
                    except TimeoutException as e:
                        print("Facebook is taking too long to load new posts. Please check for internet connectivity "
                              "issues and try again. If the issue persists, debug the code.", e)
                        break

                    continue

                driver.execute_script('arguments[0].setAttribute("data-already-scraped", "true");',
                                      unscraped_event_anchor)

                event_url = unscraped_event_anchor.get_attribute('href')
                try:
                    event_id = self.__parse_event_id(event_url)
                except EventScrapingError as e:
                    print("Skipping URL.", e)
                    continue

                if event_id in scraped_events_ids:
                    continue

                # assuming that if the scraping later fails, it will always fail for this id.
                scraped_events_ids.add(event_id)

                try:
                    event = event_scraper.scrape(event_id)

                except EventScrapingError as e:
                    print('Error scraping facebook event with id {}.'.format(event_id), e)
                    continue

                yield event

                if self.__should_stop_scraping(event):
                    print("Reached events threshold.")
                    break

        finally:
            if should_quit_driver:
                driver.quit()

    def __parse_event_id(self, event_url):
        match = self.__event_id_regex_in_url.search(event_url)
        if match is not None:
            return match.group('id')

        raise EventScrapingError("Unable to parse facebook event id from url: {}".format(event_url))


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
                      start_time=event_dict.get("start_time"),
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
        "https://www.facebook.com/oz.shoshani.3?fref=ts",
        Counter(100).has_reached_threshold)

    for event in s.scrape():
        print (unicode(event))
