import time

from selenium.common.exceptions import NoSuchElementException

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


class Counter(object):
    def __init__(self, threshold):
        self.__threshold = threshold
        self.__call_count = 0

    def has_reached_threshold(self, *args, **kwargs):
        self.__call_count += 1
        return self.__call_count >= self.__threshold
