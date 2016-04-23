import datetime as dt
import re
from itertools import chain

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from donight.event_finder.scrapers.base_scraper import BaseScraper
from donight.events import Event

TIME_SEPERATOR = ':'

NUMBER_REGEX = '.*?([0-9]+).*?'
HOUR_REGEX = '.*?([0-9]+:[0-9]+).*?'


class OzenBarScraper(BaseScraper):
    """
    This scraper is used to scrape music shows from the OzenBar website.
    """
    EVENTS_URL = 'http://www.ozenbar.com/wp-admin/admin-ajax.php'

    OZEN_BAR_LOCATION = 'OzenBar'

    def scrape(self):
        """
        This method scrapes events (mostly music shows) from the OzenBar website.
        The OzenBar website exposes a php view, that receives a month and a year,
        and returns an html representation of a list of the events of that month.
        We send requests for three months back, and a year forward,
        parse the returned html, and scrape information on the events from that.
        :return: A list of all the events in the OzenBar.
        :rtype: list(Event)
        """
        today = dt.date.today()
        dates_in_surrounding_months = [today + relativedelta(months=diff)
                                       for diff in xrange(-3, 13)]

        return chain.from_iterable([self.get_events_for_month(date.year, date.month)
                                    for date in dates_in_surrounding_months])

    def get_events_for_month(self, year, month):
        """
        The OzenBar website exposes a php view, that receives a month and a year,
        and returns an html representation of a list of the events of that month.
        This method sends a request for the given month,
        and parses the returned html into a list of events.
        :param year: The year to get the events of.
        :type year: int
        :param month: The month to get the events of.
        :type month: int
        :return: A list of events of that month.
        :rtype: list(Event)
        """
        # The month is 0-based, WTF ?
        request_data = {'action': 'get_event_showpage',
                        'year': year, 'month': month - 1}
        response = requests.post(self.EVENTS_URL, data=request_data)

        events_soup = BeautifulSoup(response.content, 'lxml', from_encoding='utf8')

        all_event_elements = events_soup.find_all('li')
        return [self.create_event_from_element(event_element, year, month)
                for event_element in all_event_elements]

    def create_event_from_element(self, event_element, year, month):
        """
        Receives an event element, that should be displayed in the OzenBar website,
        scrapes out the important data from the html, and returns an Event object representing the event.
        :param event_element: A beutifulsoup element representing an OzenBar event.
        :type event_element: bs4.Tag
        :param year: The year the event is held in.
        :type year: int
        :param month: The month the event is held in.
        :type month: int
        :return: An event containing all the information from the element.
        :rtype: Event
        """
        try:
            title = event_element.find('h2').text
            time = self.parse_time(event_element, year, month)
            price = event_element.find('b').text
            url = event_element.find('a')['href']
            description = event_element.find('p').text
            image = event_element.find('img')['src']
        except Exception as e:
            # TODO: log and fix this !
            return None

        return Event(title=title, time=time, location=self.OZEN_BAR_LOCATION,
                     price=price, url=url, description=description, image=image)

    def parse_time(self, event_element, year, month):
        """
        The html representing an OzenBar event doesn't hold the time in some plain string.
        It doesn't hold the year, the month is in hebrew text,
        and the day and time are scattered across many sub-elements.
        This method parses the day and time, and receives the month and year,
        to create a full datetime object for the time of the event.
        :param event_element: A beutifulsoup element representing an OzenBar event.
        :type event_element: bs4.Tag
        :param year: The year the event is held in.
        :type year: int
        :param month: The month the event is held in.
        :type month: int
        :return:
        :rtype:
        """
        date_element = event_element.find('div', {'class': 'date'})
        day = int(re.findall(NUMBER_REGEX, date_element.text)[0])

        time_element = event_element.find('div', {'class': 'times'})
        full_time = re.findall(HOUR_REGEX, time_element.text)[0]
        hour, minute = map(int, full_time.split(TIME_SEPERATOR))

        return dt.datetime(year, month, day, hour, minute)
