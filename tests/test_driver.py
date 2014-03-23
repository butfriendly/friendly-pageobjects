import pytest
from selenium import webdriver
from friendly.pageobjects.driver import DriverFactory


@pytest.fixture
def factory():
    return DriverFactory()


def test_supported():
    assert DriverFactory.is_supported_browser('fire fox') is False
    assert DriverFactory.is_supported_browser('firefox') is True


def test_create_local_safari(factory):
    driver = factory.create(DriverFactory.TYPE_LOCAL, DriverFactory.DRIVER_SAFARI,
                            executable_path='/Users/csc/selenium/selenium-server-standalone-2.39.0.jar')
    assert isinstance(driver, webdriver.Safari)
    driver.get('http://www.google.de')
    assert driver.current_url == 'https://www.google.de/'
    driver.quit()


def _test_create_local_phantomjs(factory):
    driver = factory.create(DriverFactory.TYPE_LOCAL, DriverFactory.DRIVER_PHANTOMJS)
    assert isinstance(driver, webdriver.PhantomJS)
    driver.get('http://www.google.de')
    assert driver.current_url == 'https://www.google.de/'
    driver.quit()


def test_create_local_chrome(factory):
    driver = factory.create(DriverFactory.TYPE_LOCAL, DriverFactory.DRIVER_CHROME)
    assert isinstance(driver, webdriver.Chrome)
    driver.get('http://www.google.de')
    assert driver.current_url == 'https://www.google.de/'
    driver.quit()


def test_create_remote_firefox_without_remoteurl(factory):
    with pytest.raises(ValueError):
        factory.create(DriverFactory.TYPE_REMOTE, DriverFactory.DRIVER_FIREFOX)


def test_create_remote_firefox(factory):
    driver = factory.create(DriverFactory.TYPE_REMOTE, DriverFactory.DRIVER_FIREFOX,
                            remote_url='http://127.0.0.1:4444/wd/hub')
    assert isinstance(driver, webdriver.Remote)
    driver.get('http://www.google.de')
    assert driver.current_url == 'http://www.google.de/'
    driver.quit()
