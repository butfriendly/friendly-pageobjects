from abc import abstractmethod, ABCMeta
import logging
import os
import urlparse

logger = logging.getLogger(__name__)


class ProductInstance(object):
    """
    Configuration object for a product's instance.
    """

    def __init__(self, instance_id, base_url):
        """
        Constructor.

        @type instance_id: str
        @param instance_id: Instance id to use
        @type base_url: str
        @param base_url: Base URL of the instance
        """
        self.instance_id = instance_id
        self.base_url = base_url


class Product(object):
    """
    Product to test.
    """
    __metaclass__ = ABCMeta

    def __init__(self, driver_manager, instance):
        """
        Constructor.

        @type driver_manager: DriverManager
        @type instance: ProductInstance
        @param instance: Settings for the instance
        """
        self._driver_manager = driver_manager
        self._instance = instance

    @property
    def driver(self):
        return self._driver_manager.get_driver()

    @abstractmethod
    def visit(self):
        pass


class ProductManager(object):
    """
    Instantiate a product object from a given class.
    """
    def __init__(self, driver_manager=None, settings=None):
        if driver_manager:
            self._driver_manager = driver_manager
        else:
            from friendly.pageobjects.driver import driver_manager
            self._driver_manager = driver_manager

        if settings:
            self._settings = settings
        else:
            from friendly.pageobjects.settings import settings
            self._settings = settings

        self._instances = {}

    def get_instance(self, *args, **kwargs):
        """
        @deprecated
        """
        return self.get_product(*args, **kwargs)

    def get_product(self, instance_id=None):
        # Use default instance id if we didn't get one
        if not instance_id:
            instance_id = self._settings['to_test.id']

        # Check for existing instance
        try:
            return self._instances[instance_id]
        except KeyError:
            pass

        # Look-up instance data from settings
        for i in self._settings['instances']:
            if i['instance']['id'] == instance_id:
                instance_data = i['instance']
                break

        if not instance_data:
            raise ValueError('Product-instance {0} not found in settings.'.format(instance_id))

        # Load product class
        product_classname = instance_data['product']['class']
        klass = self._get_product_class(product_classname)

        # Look-up instance_url override at the ENV
        instance_url = instance_data['url']
        instance_url_envvar = (instance_id + '_url').upper()
        if instance_url_envvar in os.environ:
            instance_url = os.environ[instance_url_envvar]

        # Compose base_url
        url = urlparse.urlparse(instance_url)
        base_url = '%(scheme)s://%(netloc)s' % dict((s, getattr(url, s)) for s in url._fields)

        instance = klass(self._driver_manager, ProductInstance(instance_id, base_url))

        self._instances[instance_id] = instance

        return instance

    def _get_product_class(self, class_path):
        module_name, class_name = class_path.rsplit('.', 1)
        mod = __import__(module_name, fromlist=[class_name])
        return getattr(mod, class_name)


product_manager = ProductManager()