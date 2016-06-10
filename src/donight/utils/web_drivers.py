from contextlib import contextmanager

import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By as BaseBy
from selenium.webdriver.common.keys import Keys


class By(BaseBy):
    pass


class EnhancedWebDriver(object):
    __is_initialized = False
    __driver = None

    def __init__(self, web_driver):
        self.__driver = web_driver
        self.__is_initialized = True

    def scroll_to_bottom(self):
        self.execute_script('window.scrollBy(0, document.body.scrollHeight);')

    def is_scrolled_to_bottom(self):
        """NOTE: taken from a stack overflow answer: http://stackoverflow.com/questions/9439725
                 Might fail if the body has a positive margin/border."""
        return self.execute_script('return window.innerHeight + document.body.scrollTop >= document.body.offsetHeight;')

    @contextmanager
    def new_tab(self, url=None):
        self.body.send_keys(Keys.CONTROL + 't')
        self.switch_to_window(self.window_handles[-1])
        self.hide_window()  # ASSUMPTION: window was hidden before calling this method

        try:
            if url is not None:
                self.get(url)

            yield

        finally:
            self.body.send_keys(Keys.CONTROL + 'w')

    def hide_window(self):
        size = self.get_window_size()

        # position the window outside the screen:
        self.set_window_position(-size['width'] - 10, -size['height'] - 10)

    @property
    def body(self):
        return self.find_element_by_tag_name('body')

    def has_element(self, by=By.ID, value=None):
        try:
            self.find_element(by, value)

        except NoSuchElementException:
            return False

        return True

    def __getattr__(self, item):
        return getattr(self.__driver, item)

    def __setattr__(self, key, value):
        if self.__is_initialized:
            setattr(self.__driver, key, value)
        else:
            object.__setattr__(self, key, value)

    @classmethod
    def get_instance(cls):
        if cls.__driver is None:
            driver = selenium.webdriver.Firefox()  # ASSUMPTION: firefox is already installed.
            cls.__driver = EnhancedWebDriver(driver)

        return cls.__driver

    @classmethod
    def get_enhanced_driver(cls, driver):
        if isinstance(driver, cls):
            return driver

        return cls(driver)
