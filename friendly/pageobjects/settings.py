import logging
import os
import collections
import yaml


class Settings(object):
    """
    The settings for the page-objects framework are managed
    through this class.

    Settings can be accesses through a dict-like interface:

    >>> from friendly.pageobjects.settings import settings
    >>> settings['selenium.remote_url']
    'http://127.0.0.1:4444/wd/hub'

    You can also access them by a getter:

    >>> settings.get('selenium.remote_url')
    'http://127.0.0.1:4444/wd/hub'

    Non-existing settings raise a KeyError:

    >>> settings.get('tralala')
    Traceback (most recent call last):
      ...
    KeyError: 'The key "tralala" does not exist'

    For non-existing keys you may even give a default-value:

    >>> settings.get('non.existing.key', 'default value')
    'default value'

    You can override a setting from a config file by the appropriate
    environment variable, as long as it starts with 'selenium.':

    >>> import os
    >>> os.environ['SELENIUM_REMOTE_URL'] = 'Override'
    >>> settings['selenium.remote_url']
    'Override'

    >>> settings.get('selenium.remote_url')
    'Override'

    Non 'selenium.' keys can't be overridden:

    >>> settings['product.class']
    'pages.Homepage.GxProduct'
    >>> os.environ['PRODUCT_CLASS'] = 'Check12'
    >>> settings['product.class']
    'pages.Homepage.GxProduct'
    >>> settings['to_test.settings.username']
    'webmaster@example.com'
    >>> settings.get('to_test.settings.not_existing', 'jondoe@example.com')
    'jondoe@example.com'
    """
    def __init__(self, settings):
        self._settings = settings

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            pass
        return False

    def get(self, key, default_value=None):
        val = default_value

        if key in self._settings:
            val = self._settings[key]

        # Selenium vars can be overriden by ENV-vars
        if key.lower().startswith('selenium.'):
            env_varname = key.replace('.', '_').upper()
            if env_varname in os.environ:
                val = os.environ[env_varname]

        if val is None:
            raise KeyError('The key "{0}" does not exist'.format(key))

        return val

    @staticmethod
    def flatten(d, parent_key=''):
        items = []
        for k, v in d.items():
            new_key = parent_key + '.' + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(Settings.flatten(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @classmethod
    def from_yaml(cls, path=None):
        if 'USE_SETTINGS' in os.environ:
            path = os.environ['USE_SETTINGS']

        if not path:
            raise ValueError('No settings path given. Define one thought USE_SETTINGS at the env.')

        path = os.path.realpath(os.path.abspath(path))

        with open(path, 'r') as f:
            data = yaml.load(f)

        # @todo Check YAML format
        return cls(Settings.flatten(data))


settings = Settings.from_yaml()
