from donight.utils import Counter

# See documentation of FacebookEventsScraper for more details:
PAGE_URL = 'https://www.facebook.com/hanasich'  # TODO change
EMAIL = None  # TODO fill in
PASSWORD = None  # TODO fill in
ACCESS_TOKEN = None  # can be left empty
SHOULD_STOP_SCRAPING = Counter(20).has_reached_threshold  # set a maximal number of events to scrape from the page
