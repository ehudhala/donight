import datetime

from donight.event_finder.scraping_halt_condition import MaxEventsHaltCondition, MaxEventStartTimeHaltCondition


should_hide_browser_window = True

# The path in which the scraping firefox executable is installed,
# e.g. "C:\Program Files (x86)\Mozilla Firefox\firefox.exe". Use None to use the default installation path.
browser_installation_path = None

# See documentation of FacebookEventsScraper for more details.
default_max_events_per_page = 50
default_max_event_start = datetime.datetime.now() + datetime.timedelta(days=3 * 30)
default_email = None  # TODO fill in
default_password = None  # TODO fill in

facebook_scraped_pages = [
    {
        "page_url": 'https://www.facebook.com/events/subscribed',
        "email": default_email,
        "password": default_password,
        "halt_condition": MaxEventsHaltCondition(default_max_events_per_page) |  # or:
                          MaxEventStartTimeHaltCondition(default_max_event_start)
    }
]
