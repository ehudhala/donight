import datetime as dt
import json

import requests

from donight.event_finder.scrapers.base_scraper import Scraper
from donight.events import Event
from donight.utils import jsonp_loads


class ShowsAroundScraper(Scraper):
    """
    This scraper is used to scrape music shows from the ShowsAround app.
    """
    HOST = 'http://showsaround.s3-website-eu-west-1.amazonaws.com/'

    SHOWS_URI = 'shows.json'
    ARTIST_URI = 'artists.json'

    TIME_FORMAT = '%m/%d/%Y %H:%M'

    MEANINGLESS_VALUES = ['t', 'TRUE']

    ARTISTS_SEP = ','

    def scrape(self):
        """
        This method scrapes events (music shows) from the ShowsAround app.
        ShowsAround is actually a website disguised as an app, so it's easier to scrape.
        We use their restful json api to scrape them.
        :return: A list of all the events in ShowsAround.
        :rtype: list(Event)
        """
        shows = jsonp_loads(requests.get(self.HOST + self.SHOWS_URI).content)
        artists = jsonp_loads(requests.get(self.HOST + self.ARTIST_URI).content)

        return [self.show_json_to_event(show, artists) for show in shows]

    def show_json_to_event(self, show, artists):
        """
        Receives a json dict from the ShowsAround restful api representing a show,
        extracts as much data as it can from the dict, and returns an Event object with the data.
        :param show: A dict representing an event from the ShowsAround api.
        :type show: dict
        :return: An event containing the information from the ShowsAround event.
        :rtype: Event
        """
        try:
            if all([not value or value in self.MEANINGLESS_VALUES for value in show.values()]):
                return None

            start_time = dt.datetime.strptime(show['date'] + ' ' + show['time'], self.TIME_FORMAT)
            return Event(title=show['artist'],
                         start_time=start_time,
                         location=show['location'],
                         # ShowsAround hold empty prices for free.
                         price=show['price'] if show['price'] else '0',
                         description=show['details'],
                         image=self.get_show_image(show, artists),
                         url=show['link'])
        except Exception:
            self.logger.exception("Failed turning a ShowsAround event into an event, "
                                  "the ShowsAround event is: \n%s\nException:", json.dumps(show, indent=4))
            return None

    def get_show_image(self, show, artists):
        """
        ShowsAround events rarely have their own image,
        usually they use the artists images.
        :param show: The show to get the image to.
        :type show: dict
        :param artists: A dict from artist name to its detail, used for the image here.
        :type artists: dict[str, dict[str, str]]
        :return: The best image that matches the show. (url)
        :rtype: str
        """
        if show['image']:
            return show['image']

        for artist_name in show['artist'].split(self.ARTISTS_SEP):
            artist = artists.get(artist_name.strip(), {})
            image = artist.get('image', '')

            if image:
                if not image.startswith('http:'):
                    return self.HOST + 'pics/' + image
                return image

