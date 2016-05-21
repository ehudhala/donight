from donight.utils import Counter


# See documentation of FacebookEventsScraper for more details.

default_max_events_for_page = 100
default_email = None  # TODO fill in
default_password = None  # TODO fill in
default_access_token = None  # can be left empty

facebook_scraped_pages = [
    {
        "page_url": 'https://www.facebook.com/hanasich',  # TODO change
        "email": default_email,
        "password": default_password,
        "access_token": default_access_token,
        "should_stop_scraping": Counter(default_max_events_for_page).has_reached_threshold
    },
    {
        "page_url": 'https://www.facebook.com/hanasich',  # TODO change
        "email": default_email,
        "password": default_password,
        "access_token": default_access_token,
        "should_stop_scraping": Counter(default_max_events_for_page).has_reached_threshold
    }  # TODO add other pages
]