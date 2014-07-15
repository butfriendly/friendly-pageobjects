import os
import sys
from selenium.webdriver.common.by import By
from friendly.pageobjects.page import PageObject, PageObjectFactory
from friendly.pageobjects.product import Product, product_manager
from selenium.webdriver.support import expected_conditions as EC

parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)


class SearchResultPage(PageObject):
    """A search result page"""
    _first_hit = lambda self: self.driver.find_element_by_xpath('//ol[@id="rso"]//li[1]//a')

    def click_first_hit(self):
        self._first_hit().click()

    def get_page_load_condition(self):
        return EC.presence_of_element_located((By.ID, 'rcnt'))


class Homepage(PageObject):
    """The Google-search homepage"""
    url = '/'

    _search_input = lambda self: self.driver.find_element_by_css_selector('input[name="q"]')
    _start_search_button = lambda self: self.driver.find_element_by_id('gbqfb')

    def focus_search_input(self):
        self._search_input().click()
        return self

    def enter_searchterm(self, searchterm):
        self._search_input().send_keys(searchterm)
        return self

    def click_start_search_button(self):
        self._start_search_button().click()
        return self.create_page(SearchResultPage).visit(navigate=False)

    def get_page_load_condition(self):
        return EC.presence_of_element_located((By.ID, 'hplogo'))


class GoogleSearch(Product):
    """Our imaginary product we want to test"""
    def visit(self):
        self.driver.get(self._instance.base_url)

        page = PageObjectFactory.create(self.driver, Homepage)
        page.visit()

        return page

    def get_page_load_condition(self):
        return EC.presence_of_element_located((By.ID, 'mngb'))


def main():
    # Get the product to test
    product = product_manager.get_product()

    # Visit the homepage of the product
    homepage = product.visit()

    # Start search
    homepage.enter_searchterm('site:github.com friendly pageobjects')
    result_page = homepage.click_start_search_button()

    # Click at one of the results
    result_page.click_first_hit()

if __name__ == '__main__':
    main()