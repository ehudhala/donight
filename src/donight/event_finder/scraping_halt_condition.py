from abc import abstractmethod, ABCMeta


class ScrapingHaltCondition(object):
    __metaclass__ = ABCMeta

    def __or__(self, other):
        return UnionHaltCondition(self, other)

    @abstractmethod
    def should_stop_scraping(self, event):
        """
        Whether the given event should be the last scraped event.
        :returns: A boolean-convertible object which explains why the scraping should stop/continue.
        :rtype: ScrapingShouldStop|ScrapingShouldContinue
        """
        raise NotImplementedError


class UnionHaltCondition(ScrapingHaltCondition):
    def __init__(self, *halt_conditions):
        self.__halt_conditions = halt_conditions

    def should_stop_scraping(self, event):
        for halt_condition in self.__halt_conditions:
            should_stop_scraping = halt_condition.should_stop_scraping(event)
            if should_stop_scraping:
                return should_stop_scraping
        return ScrapingShouldContinue()


class MaxEventsHaltCondition(ScrapingHaltCondition):
    def __init__(self, max_events):
        self.__max_events = max_events
        self.__total_events = 0

    def should_stop_scraping(self, event):
        self.__total_events += 1
        if self.__total_events >= self.__max_events:
            return ScrapingShouldStop("Scraped the maximal number of events ({}).".format(self.__max_events))
        return ScrapingShouldContinue()


class MaxEventStartTimeHaltCondition(ScrapingHaltCondition):
    def __init__(self, max_time):
        self.__max_time = max_time

    def should_stop_scraping(self, event):
        if event.start_time > self.__max_time:
            return ScrapingShouldStop("Event start time ({}) is after the max time ({}).".format(event.start_time,
                                                                                                 self.__max_time))
        return ScrapingShouldContinue()


class ScrapingShouldStop(object):
    def __init__(self, reason):
        self.why = reason

    def __nonzero__(self):
        return True


class ScrapingShouldContinue(object):
    def __init__(self):
        self.why = "No halt condition has been met."

    def __nonzero__(self):
        return False
