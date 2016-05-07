class EnhancedWebDriver(object):
    __is_initialized = False

    def __init__(self, web_driver):
        self.__driver = web_driver
        self.__is_initialized = True

    def scroll_to_bottom(self):
        self.execute_script('window.scrollBy(0, document.body.scrollHeight);')

    @property
    def body(self):
        return self.find_element_by_tag_name('body')

    def __getattr__(self, item):
        return getattr(self.__driver, item)

    def __setattr__(self, key, value):
        if self.__is_initialized:
            setattr(self.__driver, key, value)
        else:
            object.__setattr__(self, key, value)
