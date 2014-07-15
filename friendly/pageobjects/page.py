import base64
import logging
import urlparse
import datetime
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


class PageObjectFactory(object):
    """
    Instantiate a page object from a given class.
    """
    @staticmethod
    def create(driver, klass, **kwargs):
        logger.info('Creating new page "%s"', klass.__name__)
        return klass(driver, **kwargs)


class PageObject(object):
    def __init__(self, driver, **kwargs):
        self.driver = driver

    def create_page(self, klass, **kwargs):
        """
        Creates a new page.

        @type klass: PageObject
        @param klass: PageObject to instantiate
        @return PageObject
        """
        return PageObjectFactory.create(self.driver, klass, **kwargs)

    def reload(self):
        self.driver.navigate().refresh()

    @property
    def url(self):
        return ''

    def navigate(self):
        self.driver.get(self.get_current_base_url() + self.url)

    def get_waiter(self, **kwargs):
        """
        @rtype: WebDriverWait
        """
        return WebDriverWait(self.driver, kwargs.get('timeout', 10))

    def get_action_chain(self, **kwargs):
        """
        @rtype: ActionChains
        """
        return ActionChains(self.driver)

    def wait_until(self, condition):
        """
        Waits until the given condition is true.

        @type condition: ExpectedCondition
        @param condition: Condition to wait for
        """
        self.get_waiter().until(condition)

    def wait_for_page_to_load(self, page_load_condition):
        self.wait_until(page_load_condition)

    def get_page_load_condition(self):
        """
        Returns the condition under which the page is loaded.

        @returns ExpectedCondition
        """
        raise NotImplementedError()

    def visit(self, navigate=True):
        """
        Navigate to the page's URL and wait for it to load.

        @type navigate: bool
        @param navigate: Wether to navigate to the page's URL or not
        """
        if navigate:
            self.navigate()
        self.wait_for_page_to_load(self.get_page_load_condition())
        return self

    def get_current_base_url(self):
        """
        Returns the base-URL of the page.

        @return str
        """
        url = urlparse.urlparse(self.driver.current_url)
        base_url = '%(scheme)s://%(netloc)s' % dict((s, getattr(url, s)) for s in url._fields)
        return base_url

    def get_screenshot_filename(self):
        return datetime.date.today().strftime('screenshot_%Y%m%d_%H%M%S.png')

    def take_screenshot(self):
        filename = self.get_screenshot_filename()
        if isinstance(self.driver, webdriver.Remote):
            # If this is a remote webdriver.  We need to transmit the image data
            # back across system boundries as a base 64 encoded string so it can
            # be decoded back on the local system and written to disk.
            screenshot_file = open(filename, 'wb')
#            base64_data = self.driver.get_screenshot_as_base64()
#            screenshot_data = base64.decodestring(base64_data)
#            screenshot_file.write(screenshot_data)
            screenshot_file.write(self.driver.get_screenshot_as_png())
            screenshot_file.close()
        else:
            self.driver.save_screenshot(filename)