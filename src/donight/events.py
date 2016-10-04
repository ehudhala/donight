import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from donight.config.consts import DB_CONNECTION_STRING

DEFAULT_EVENT_TYPE_NAME = 'unknown'
MUSIC_SHOW_EVENT_TYPE_NAME = 'music_show'
LECTURE_EVENT_TYPE_NAME = 'lecture'

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

    # Facebook
    owner_name = Column(String(MEDIUM_STR_LEN))
    owner_id = Column(Integer)
    ticket_url = Column(String(MEDIUM_STR_LEN))

    event_type_name = Column(String(MEDIUM_STR_LEN))

    __mapper_args__ = {
        'polymorphic_on': event_type_name,
        'polymorphic_identity': DEFAULT_EVENT_TYPE_NAME
    }

    def __repr__(self):
        return u'{0} at {1} @ {2}'.format(self.title, self.location, self.start_time)

    __serialize_attr_to_dict = {'start_time': datetime.datetime.isoformat,
                                'end_time': datetime.datetime.isoformat}

    def to_dict(self):
        return {column.name: self.get_attr_to_dict(column.name)
                for column in self.__table__.columns
                if hasattr(self, column.name)}

    def get_attr_to_dict(self, attr_name):
        attr_serializer = self.__serialize_attr_to_dict.get(attr_name, unicode)
        attr = getattr(self, attr_name)
        return attr_serializer(attr) if attr is not None else ''

    @property
    def owner_url(self):
        if self.owner_id:
            return "https://www.facebook.com/" + self.owner_id
        return ''


class MusicShow(Event):
    youtube_url = Column(String(MEDIUM_STR_LEN))

    def __init__(self, *args, **kwargs):
        super(MusicShow, self).__init__(*args, **kwargs)

        if not self.youtube_url:
            self.youtube_url = self.title

    __mapper_args__ = {
        'polymorphic_identity': MUSIC_SHOW_EVENT_TYPE_NAME
    }


class Lecture(Event):
    __mapper_args__ = {
        'polymorphic_identity': LECTURE_EVENT_TYPE_NAME
    }


class FacebookGroup(Base):
    __tablename__ = 'facebook_groups'

    owner_id = Column(Integer, primary_key=True)
    owner_name = Column(String(MEDIUM_STR_LEN))
    type_name = Column(String(MEDIUM_STR_LEN))

    @classmethod
    def get_group(cls, owner_id):
        return session.query(cls).filter(cls.owner_id == owner_id).first()

    @classmethod
    def get_event_type(cls, owner_id):
        group = cls.get_group(owner_id)
        if group is None:
            return Event
        return get_event_type_by_type_name(group.type_name)

    @classmethod
    def create_if_doesnt_exist(cls, owner_id, owner_name):
        group = cls.get_group(owner_id)
        if group is None:
            session.add(cls(owner_id=owner_id, owner_name=owner_name))
            session.commit()


EVENT_TYPES = [Event, MusicShow, Lecture]
EVENT_TYPE_NAME_TO_TYPE = {event_type.__mapper_args__['polymorphic_identity']: event_type
                           for event_type in EVENT_TYPES}
EVENT_TYPE_NAMES = EVENT_TYPE_NAME_TO_TYPE.keys()

def get_event_type_by_type_name(event_type_name):
    return EVENT_TYPE_NAME_TO_TYPE.get(event_type_name, Event)


engine = create_engine(DB_CONNECTION_STRING)
# Event.__table__.drop(engine, checkfirst=True)
# FacebookGroup.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

