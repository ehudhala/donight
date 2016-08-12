# Donight

## Overview

Donight is a framework for indexing events from the web, and making them **easily accessible.**
It aims to be **easily extensible**, in order to allow an open source community to form around it.

## Installation

To install simply run:

```bash
git clone https://github.com/ehudhala/donight.git
cd donight/src
python setup.py develop
```

(Note: Donight is still under heavy development, so for now installation is only for developing purposes.)

#### Facebook setup:

Additional setup is required to scrape facebook users:

1. Make sure Firefox is installed on the executing computer.
    * Since we're using Selenium to interact with the browser, there may be 
    [compatibility issues](http://www.seleniumhq.org/about/platforms.jsp) between versions.
    Donight has been tested with [Firefox 46.0.1](https://ftp.mozilla.org/pub/firefox/releases/46.0.1/) and 
    selenium 2.53.2. Use `pip install selenium==2.53.2` to install that version.
2. Configure the scraping in src/donight/config/facebook_scraping_config.py. You'll need to specify the scraped
user email, password, the scraped pages URLs, etc. - it's all documented in that page.
4. Configure the scraped user.
    1. Manually login to the scraped user.
    2. Enter the [Graph API Explorer](https://developers.facebook.com/tools/explorer) page.
    3. Click 'Get Token' → 'Get User Access Token'. Make sure the `user_events` option is enabled and click 'Get Access
    Token'. If Facebook requires that you permit the app to access your account, do so.
    4. Enter the user's [language settings page](https://www.facebook.com/settings?tab=language) and set facebook to 
    be shown in `English (US)`.
    

#### Web setup:

In order to develop the web server, the following should be done:

1. Install [node.js](https://nodejs.org/).
2. In `src/donight/web/client` run `npm install`.
3. Run `gulp` in order to compile the sources for the web frontend. 
    (You can run `gulp watch` in order to automatically recompile)
4. Serve the web server by running `python src/donight/web/app.py`.


## Usage

Donight is simple to use. 
To index all events once installed:

```python
from donight.event_finder import EventFinder

EventFinder().index_events()
```

Then to create an excel spreadsheet from the indexed events for easy viewing:

```python
from donight.applications.events_to_excel import EventsExcel
from donight.events import Session, Event

events = Session().query(Event).all()
EventsExcel().create_excel(events, "events.xlsx")
```

As we see in the example Donight is split into two parts:

* EventFinder:
    This module is responsible for finding events, and indexing them to the db.
* applications:
    This package holds anything we want to do with our db full of events.
    
These two parts interface with the DB.
The DB is currently an sqlite3 db, wrapped with sqlalchemy.
The EventFinder uploads events to the DB, and the applications can read data from the DB.

You can dig further into the documentation to find more ways of using Donight !
    
## Contributing

### A little about the design

Donight's event finder gets a list of scrapers when it is initialized, which defaults to all the scrapers.
It then uses every scrapers scrape() method in order to scrape events.
After it collects all the events it either uploads them to the DB, for applications to use,
or updates the information of events that already exist in the DB.

### Guided example

In order to scrape events from a new source, all you have to do is create a new scraper class in the scrapers package,
for example:

> donight/event_finder/scrapers/birthday.py
> ```python
> import datetime
> 
> from donight.event_finder.scrapers.base_scraper import Scraper
> from donight.events import Event
> 
> 
> class BirthDayScraper(Scraper):
>     BIRTHDAYS = {
>         'Ehud': datetime.datetime(1996, 7, 23),
>         'Or': datetime.datetime(1994, 2, 1)
>     }
>     
>     def scrape(self):
>         return [
>             Event(title=name + "'s birthday", start_time=date)
>             for name, date in self.BIRTHDAYS.iteritems()
>         ]
> ```

Then, if you want to enable it in any default event finder you should add it to `ALL_SCRAPERS` in `donight/event_finder/scrapers/__init__.py__`

The scraper you create can implement the scrape method however you wish, but it has to return a list of `Event` items.
For more detailed examples you should look at the scrapers already implemented.

After implementing a scraper, every call to `EventFinder().index_events()` will also upload events scraped by your scraper to the DB :)

## Missing features

* We can give much more value if we add information that can be inferred in a generic way for any event, for example:
    * Add a link to youtube videos of artists.
    * Show percentage of free space for an event.
    * Add a link to the bandcamp / facebook page of artists
    * We can probably think of many more features in this area...
* Many many more scrapers, including:
    * Rothschild 12
    * The Container
    * The Yellow Submarine
    * Pasaz
    * Leeba
    * Bet Avihay
    * Poetry Slam
    * Theatre shows (The Bima, The Camery)
    * We should think of more...
* Nicer views for the data. 
    Currently we only support exporting the events data to excel, but we should support:
    * Sending an organized mail with the data (for a weekly newsletter).
    * A website.
    * An application.
    
