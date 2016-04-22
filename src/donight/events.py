from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from donight.config import DB_PATH

MEDIUM_STR_LEN = 1024

Base = declarative_base()

# TODO: inheritance with polymorphism (we want shows, lectures and such to be different)
class Event(Base):
    """
    Represents an event in the db.
    An event has the attributes of this model.

    The db is the interface between scraping events, and using the scraped information.
    (Scrapers only upload to the db, and any application on the event reads from the db.
    """
    __tablename__ = 'events'

    id = Column(Integer, Sequence('event_id_sequence'),primary_key=True)
    title = Column(String(MEDIUM_STR_LEN))
    time = Column(DateTime)
    location = Column(String(MEDIUM_STR_LEN))
    price = Column(String(MEDIUM_STR_LEN))
    url = Column(String(MEDIUM_STR_LEN))
    description = Column(String(MEDIUM_STR_LEN))
    image = Column(String(MEDIUM_STR_LEN))

    def __repr__(self):
       return u'{0} at {1} @ {2}'.format(self.title, self.location, self.time)


engine = create_engine('sqlite:///{0}'.format(DB_PATH))
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
