import os
import urlparse
import datetime
import logging
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, Proxy
from selenium.webdriver.common.proxy import ProxyType

logger = logging.getLogger(__name__)


class DriverFactory(object):
    """
    The C{DriverFactory} encapsulates the instantiation of new C{WebDriver} instances.
    """
    TYPE_LOCAL = 'LOCAL'
    TYPE_REMOTE = 'REMOTE'

    DRIVER_CHROME = "CHROME"
    DRIVER_FIREFOX = "FIREFOX"
    DRIVER_INTERNETEXPLORER = "INTERNETEXPLORER"
    DRIVER_OPERA = "OPERA"
    DRIVER_PHANTOMJS = "PHANTOMJS"
    DRIVER_SAFARI = "SAFARI"

    DRIVER_HTMLUNIT = "HTMLUNIT"
    DRIVER_HTMLUNITWITHJS = "HTMLUNITWITHJS"
    DRIVER_ANDROID = "ANDROID"
    DRIVER_IPAD = "IPAD"
    DRIVER_IPHONE = "IPHONE"

    LOCAL_DRIVERS = {
        DRIVER_CHROME: lambda self: self._create_chrome_driver,
        DRIVER_FIREFOX: lambda self: self._create_firefox_driver,
        DRIVER_INTERNETEXPLORER: lambda self: self._create_ie_driver,
        DRIVER_OPERA: lambda self: self._create_opera_driver,
        DRIVER_PHANTOMJS: lambda self: self._create_phantomjs_driver,
        DRIVER_SAFARI: lambda self: self._create_safari_driver,
    }

    DRIVER_CAPABILITIES = {
        DRIVER_HTMLUNIT: DesiredCapabilities.HTMLUNIT,
        DRIVER_HTMLUNITWITHJS: DesiredCapabilities.HTMLUNITWITHJS,
        DRIVER_ANDROID: DesiredCapabilities.ANDROID,
        DRIVER_CHROME: DesiredCapabilities.CHROME,
        DRIVER_FIREFOX: DesiredCapabilities.FIREFOX,
        DRIVER_INTERNETEXPLORER: DesiredCapabilities.INTERNETEXPLORER,
        DRIVER_IPAD: DesiredCapabilities.IPAD,
        DRIVER_IPHONE: DesiredCapabilities.IPHONE,
        DRIVER_OPERA: DesiredCapabilities.OPERA,
        DRIVER_SAFARI: DesiredCapabilities.SAFARI,
        DRIVER_PHANTOMJS: DesiredCapabilities.PHANTOMJS
    }

    @staticmethod
    def is_supported_browser(browser_name):
        """
        Checks wether the given browser is supported

        @type browser_name: str
        @param browser_name: Identifier of the browser
        @return bool
        """
        return browser_name.upper() in DriverFactory.LOCAL_DRIVERS

    def create(self, driver_type, driver, **kwargs):
        """
        @type driver_type: DriverFactory.TYPE_LOCAL | DriverFactory.TYPE_REMOTE
        @type driver: DriverFactory.DRIVER_CHROME | DriverFactory.DRIVER_FIREFOX |
                      DriverFactory.DRIVER_INTERNETEXPLORER | DriverFactory.DRIVER_OPERA |
                      DriverFactory.DRIVER_PHANTOMJS | DriverFactory.DRIVER_SAFARI | DriverFactory.DRIVER_HTMLUNIT |
                      DriverFactory.DRIVER_HTMLUNITWITHJS | DriverFactory.DRIVER_ANDROID |
                      DriverFactory.DRIVER_IPHONE | DriverFactory.DRIVER_IPAD
        """
        logger.info('Creating driver')
        if driver_type == self.TYPE_REMOTE:
            instance = self._create_remote_driver(driver, **kwargs)
        else:
            instance = self._create_local_driver(driver, **kwargs)

        try:
            instance.maximize_window()
        except:
            datetime.time.sleep(10)
            try:
                instance.maximize_window()
            except Exception:
                raise

        return instance

    def _create_local_driver(self, driver, **kwargs):
        logger.debug('Creating local driver "%s"', driver)
        try:
            return self.LOCAL_DRIVERS[driver](self)(**kwargs)
        except KeyError:
            raise TypeError("Unsupported Driver Type {0}".format(driver))

    def _create_remote_driver(self, driver, **kwargs):
        if not 'remote_url' in kwargs:
            raise ValueError('Remote drivers require the declaration of a remote_url')

        remote_url = kwargs.get('remote_url')

        logger.info('Creating remot driver "%s" (remote_url=%s)', driver, remote_url)

        try:
            # Get a copy of the desired capabilities object. (to avoid overwriting the global.)
            capabilities = self.DRIVER_CAPABILITIES[driver].copy()
        except KeyError:
            raise TypeError("Unsupported Browser Type {0}".format(driver))

        if 'capabilities' in kwargs:
            for c in kwargs.get('capabilities'):
                capabilities.update(c)

        if 'proxy' in kwargs:
            proxy_url = kwargs.get('proxy')
            proxy = Proxy({
                'httpProxy': proxy_url,
                'ftpProxy': proxy_url,
                'sslProxy': proxy_url,
                'noProxy': None,
                'proxyType': ProxyType.MANUAL,
                'autodetect': False
            })
            proxy.add_to_capabilities(capabilities)

        driver_instance = webdriver.Remote(
            desired_capabilities=capabilities,
            command_executor=remote_url
        )
        return driver_instance

    def _create_opera_driver(self):
        return webdriver.Opera()

    def _create_ie_driver(self):
        return webdriver.Ie()

    def _create_safari_driver(self, **kwargs):
        if not 'executable_path' in kwargs:
            raise ValueError('Local Safari requires a local Selenium-server. '
                             'Please configure the executable_path at the settings.')
        os.environ['SELENIUM_SERVER_JAR'] = kwargs.get('executable_path')
        return webdriver.Safari()

    def _create_phantomjs_driver(self, **kwargs):
        ignore_ssl_errors = 'true' if 'ignore-ssl-errors' in kwargs else 'false'

        params = {
            'executable_path': kwargs.get('executable_path', '/usr/local/bin/phantomjs'),
            'service_args': ['--ignore-ssl-errors=%s' % ignore_ssl_errors]
        }

        return webdriver.PhantomJS(**params)

    def _create_firefox_driver(self, **kwargs):
        firefox_profile = webdriver.FirefoxProfile()

        if 'proxy' in kwargs:
            url = urlparse.urlparse(kwargs.get('proxy'))
            proxy_host, proxy_port = url.netloc.rsplit(':', 1)

            firefox_profile.set_preference('network.proxy.type', 1)
            firefox_profile.set_preference('network.proxy.http', proxy_host)
            firefox_profile.set_preference('network.proxy.http_port', int(proxy_port))
            firefox_profile.set_preference('network.proxy.ssl', proxy_host)
            firefox_profile.set_preference('network.proxy.ssl_port', int(proxy_port))
            firefox_profile.set_preference('network.proxy.no_proxies_on', '127.0.0.1, localhost, .local')
            firefox_profile.update_preferences()

        return webdriver.Firefox(firefox_profile=firefox_profile)

    def _create_chrome_driver(self, **kwargs):
        chrome_options = webdriver.ChromeOptions()

        if 'proxy' in kwargs:
            url = urlparse.urlparse(kwargs.get('proxy'))
            logger.info('Using proxy %s', url.netloc)
            chrome_options.add_argument('--proxy-server=%s' % url.netloc)

        params = {
            'executable_path': kwargs.get('executable_path', '/usr/local/bin/chromedriver'),
            'chrome_options': chrome_options
        }

        return webdriver.Chrome(**params)


class DriverManager(object):
    """
    The C{DriverManager} manages the instantiation, handling and configuration
    of the required Selenium-driver instance.

    @type settings: Settings
    @param settings: An instance of the settings the C{DriverManager} should
                     use. If C{None} is given the manager will use the
                     default-instance.
    @type driver_factory: DriverFactory
    @param driver_factory: An instance of the C{DriverFactory} the manager
                           should use. If C{None} is given it will use
                           the default-instance.
    """
    def __init__(self, settings=None, driver_factory=None):
        self._driver = None

        if not settings:
            from friendly.pageobjects.settings import settings
        self._settings = settings

        self._factory = driver_factory if driver_factory else DriverFactory()

        self._reusebrowser = settings.get('selenium.reusebrowser', True)
        self._dont_close = settings.get('selenium.dont_close', True)

    def __del__(self):
        try:
            self.close_driver()
        except:
            pass

    def _create_driver(self):
        driver_type = DriverFactory.TYPE_REMOTE \
            if self._settings['selenium.browser.remote'] else DriverFactory.TYPE_LOCAL
        driver_name = self._settings['selenium.browser.name'].upper()

        logger.info('Creating driver (type=%s, name=%s)', driver_type, driver_name)

        kwargs = {}
        if 'selenium.browser.executable_path' in self._settings:
            executable_path = self._settings['selenium.browser.executable_path']
            if not os.path.exists(executable_path):
                raise ValueError('Invalid selenium.browser.executable_path in settings. {0} does not exist.'
                                 .format(executable_path))
            kwargs['executable_path'] = executable_path

        if 'selenium.browser.proxy' in self._settings:
            kwargs['proxy'] = self._settings['selenium.browser.proxy']

        if 'selenium.browser.name' in self._settings:
            kwargs['name'] = self._settings['selenium.browser.name']

        if 'selenium.browser.capabilities' in self._settings:
            kwargs['capabilities'] = self._settings['selenium.browser.capabilities']

        if 'SELENIUM_SERVER_JAR' in os.environ:
            server_path = os.getenv('SELENIUM_SERVER_JAR')
        elif 'selenium.server_path' in self._settings:
            server_path = self._settings['selenium.server_path']
            os.environ['SELENIUM_SERVER_JAR'] = server_path
        else:
            server_path = None

        if server_path:
            if not os.path.exists(server_path):
                raise ValueError('Selenium server binary not found at "{0}".'.format(server_path))
            kwargs['server_path'] = server_path

        if DriverFactory.TYPE_REMOTE == driver_type and 'selenium.remote_url' in self._settings:
            kwargs['remote_url'] = self._settings['selenium.remote_url']

        return self._factory.create(driver_type, driver_name, **kwargs)

    def _reset_driver(self):
        logger.info('Resetting driver')
        try:
            logger.debug('Deleting cookies')
            self._driver.delete_all_cookies()
            self._driver.get('about:blank')
        except:
            logger.warn('Reset failed')
            try:
                if self._driver.is_online():
                    self.close_driver()
            except:
                logger.error('Could not reset nor close')

    def get_driver(self):
        logger.info('Getting driver')
        if self._driver is None:
            logger.debug('No driver found')
            self._driver = self._create_driver()
        return self._driver

    def close_driver(self):
        logger.info('Closing driver')

        if self._dont_close:
            logger.debug('Dont close')
            return

        if self._driver is None:
            logger.debug('No driver to close')
            return

        if self._reusebrowser:
            logger.debug('Re-use wanted, trying to only reset the driver')
            self._reset_driver()
        else:
            logger.debug('Trying to close/quit the driver')
            try:
                self._driver.close()
                self._driver.quit()
                logger.debug('Driver closed')
            except:
                logger.error('Could not close driver')
                raise
            del self._driver
            self._driver = None

driver_manager = DriverManager()

try:
    import atexit
    atexit.register(driver_manager.close_driver)
except:
    pass
