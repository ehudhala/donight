import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from donight.config.consts import DB_CONNECTION_STRING

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

    id = Column(Integer, Sequence('event_id_sequence'), primary_key=True)
    title = Column(String(MEDIUM_STR_LEN))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String(MEDIUM_STR_LEN))
    price = Column(String(MEDIUM_STR_LEN))
    url = Column(String(MEDIUM_STR_LEN))
    description = Column(Text())
    image = Column(String(MEDIUM_STR_LEN))
    owner = Column(String(MEDIUM_STR_LEN))
    owner_url = Column(String(MEDIUM_STR_LEN))
    ticket_url = Column(String(MEDIUM_STR_LEN))

    event_type = Column(String(MEDIUM_STR_LEN))

    __mapper_args__ = {
        'polymorphic_on': event_type,
        'polymorphic_identity': 'event'
    }

    def __repr__(self):
        return u'{0} at {1} @ {2}'.format(self.title, self.location, self.start_time)

    __serialize_attr_to_dict = {'start_time': datetime.datetime.isoformat,
                                'end_time': datetime.datetime.isoformat}

    def to_dict(self):
        return {column.name: self.get_attr_to_dict(column.name)
                for column in self.__table__.columns}

    def get_attr_to_dict(self, attr_name):
        attr_serializer = self.__serialize_attr_to_dict.get(attr_name, unicode)
        attr = getattr(self, attr_name)
        return attr_serializer(attr) if attr is not None else ''


engine = create_engine(DB_CONNECTION_STRING)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
