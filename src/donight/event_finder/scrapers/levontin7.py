import datetime as dt
import json
import time

import requests

from donight.event_finder.scrapers.base_scraper import Scraper
from donight.events import Event
from donight.utils import SECONDS_IN_MONTH, SECONDS_IN_YEAR, find, to_local_timezone


class Levontin7Scraper(Scraper):
    """
    This scraper is used to scrape indie music shows from the Levontin 7 website.
    """
    URL = 'http://www.levontin7.com/'

    EVENTS_PARAMS = {'rhc_action': 'get_calendar_events',
                     'post_type': 'events'}

    LEVONTIN_LOCATION = u'\u05dc\u05d1\u05d5\u05e0\u05d8\u05d9\u05df 7'

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    SHEKEL_CHAR = u'\u20aa'
    FREE_STRINGS = [u'\u05d7\u05d9\u05e0\u05dd', u'\u05db\u05e0\u05d9\u05e1\u05d4 \u05d7\u05d5\u05e4\u05e9\u05d9\u05ea']

    def scrape(self):
        """
        This method scrapes events (music shows) from the Levontin 7 website.
        Levontin's website exposes a restful json api for its clients,
        so we use that api and just parse the json for the events.
        :return: A list of all the events in Levontin 7.
        :rtype: list(Event)
        """
        event_range = {'start': time.time() - 3 * SECONDS_IN_MONTH, 'end': time.time() + SECONDS_IN_YEAR}
        response = requests.post(self.URL, params=self.EVENTS_PARAMS, data=event_range)

        events_list = json.loads(response.content)['EVENTS']
        return map(self.levontin_json_to_event, events_list)

    def levontin_json_to_event(self, levontin_event):
        """
        Receives a json dict from the levontin restful api representing an event,
        extracts as much data as it can from the dict, and returns an Event object with the data.
        :param levontin_event: A dict representing an event from the Levontin api.
        :type levontin_event: dict
        :return: An event containing the information from the levontin event.
        :rtype: Event
        """
        try:
            start_time = self.levontin_time_to_time(levontin_event['start'])
            end_time = self.levontin_time_to_time(levontin_event['end'])
            description = self.remove_line_breaks_from_description(levontin_event['description'])
            price = self.get_price_from_description(description)
            image = levontin_event['image'][0] if levontin_event['image'] else ''
            return Event(title=levontin_event['title'],
                         start_time=start_time,
                         end_time=end_time,
                         location=self.LEVONTIN_LOCATION,
                         price=price,
                         url=levontin_event['url'],
                         description=description,
                         image=image,
                         owner=None,
                         owner_url=None)
        except Exception:
            self.logger.exception("Failed turning a Levontin event into an event, "
                                  "the Levontin event is: \n%s\nException:", json.dumps(levontin_event, indent=4))
            return None

    def get_price_from_description(self, description):
        """
        The Levontin json for an event doesn't include a price for the event,
        but the price in most of the events is included in the description.
        This method uses heuristics on the description to try to find the price of an event.
        It works in about 95% of the events. (it doesn't work when the price isn't included in the description).
        :param description: The description of the event.
        :type description: str
        :return: The price of the event.
        :rtype: str
        """
        # TODO: refactor !
        if any([free_string in description for free_string in self.FREE_STRINGS]):
            return '0'

        if self.SHEKEL_CHAR in description:
            description_words = description.split()

            if self.SHEKEL_CHAR in description_words:
                # There is a space between the shekel and the price, we take the price that is before the shekel.
                shekel_index = description_words.index(self.SHEKEL_CHAR)
                return description_words[shekel_index - 1]
            else:
                # There is no space between the shekel char and the price, so we take the price from the word of the shekel.
                shekel_word = find(description_words, lambda word: self.SHEKEL_CHAR in word, '')
                return shekel_word.replace(self.SHEKEL_CHAR, '')

        return ''

    def remove_line_breaks_from_description(self, description):
        """
        The way that the Levontin website works is that the description received from the json api
        is rendered as html.
        We only need the text from the description, and don't want to bloat it with html line breaks,
        so we remove those.
        :param description: The description of an event from the Levontin website.
        :type description: str
        :return: The same description, without html line breaks.
        :rtype: str
        """
        # TODO: remove all html elements, leave only text.
        return description.replace('<br>\n', '').replace('<br>', '')

    def levontin_time_to_time(self, levontin_time):
        """
        Creates a datetime object from a string describing time in a levontin event.
        :param levontin_time: The time string from a levontin event.
        :type levontin_time: str
        :return: A datetime object of that time.
        :rtype: datetime.datetime
        """
        return to_local_timezone(dt.datetime.strptime(levontin_time, self.TIME_FORMAT))

