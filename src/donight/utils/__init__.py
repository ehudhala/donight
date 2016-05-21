import time

import dateutil.tz
from sqlalchemy import inspect

SECONDS_IN_DAY = 24 * 60 * 60
SECONDS_IN_MONTH = 30 * SECONDS_IN_DAY
SECONDS_IN_YEAR = 365 * SECONDS_IN_DAY


def to_timestamp(date_time_object):
    """
    Gets a unix timestamp (time from epoch) from a datetime object.
    (It isn't easily implemented in the datetime api.)
    :param date_time_object: The datetime to get a timestamp of.
    :type date_time_object: datetime.datetime
    :return: A unix timestamp of the date.
    :rtype: int
    """
    return time.mktime(date_time_object.timetuple())


def to_local_timezone(date_time_object):
    """
    Gets the given datetime adjusted to the local timezone, without the timezone info.
    If the given datetime is timezone-naive, the local timezone is assumed.
    :type date_time_object: datetime.datetime
    :return: The datetime adjusted to the local timezone, without tzinfo.
    :rtype: datetime.datetime
    """
    if date_time_object.tzinfo is None:
        return date_time_object

    return date_time_object.astimezone(dateutil.tz.tzlocal()).replace(tzinfo=None)


def find(iterable, condition, default=None):
    """
    Finds the first item in the iterable that passes the condition.
    If no such item is found, returns the given default.
    :param iterable: The iterable to find a matching item in.
    :type iterable: iterable
    :param condition: The condition for the item to be found,
        should be a function that returns True for the desired item.
    :type condition: function
    :param default: The default value to return in case no item matches the condition.
    :return: The first item in the iterable to pass the condition.
    """
    return next((item for item in iterable if condition(item)), default)


def get_model_fields(model, excluded_fields=list()):
    """
    Returns a list of all the fields an sqlalchemy model has.
    :param model: The model to get the fields of.
    :type model: Base
    :param excluded_fields: A list of fields not to include, even if they exist.
    :type excluded_fields: list(str)
    :return: A list of all the fields of the model.
    :rtype: list(str)
    """
    return [unicode(column.key) for column in inspect(model).mapper.columns
            if column.key not in excluded_fields]


class Counter(object):
    def __init__(self, threshold):
        self.__threshold = threshold
        self.call_count = 0

    def has_reached_threshold(self, *args, **kwargs):
        self.call_count += 1
        return self.call_count >= self.__threshold
