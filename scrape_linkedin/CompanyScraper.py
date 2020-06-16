from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
from .Company import Company
from .utils import AnyEC


class CompanyScraper(Scraper):
    def scrape(self, company=None, url=None, overview=True, jobs=False, life=False, insights=False, people=True):
        # checking if or company or url is provided to construct the url
        if company is None and url is None:
            raise ValueError("Both company and URL argument are None when trying to scrape company.")
        elif company is not None:
            self.url = 'https://www.linkedin.com/company/{}'.format(str(company).lower())
        else:
            self.url = url
        # Get Overview
        self.load_initial(self.url)

        jobs_html = life_html = insights_html = overview_html = people_html = ''

        if overview:
            overview_html = self.get_overview()
        if life:
            life_html = self.get_life()
        if jobs:
            jobs_html = self.get_jobs()
        if insights:
            insights_html = self.get_insights()
        if people:
            people_html = self.get_people()
        #print("JOBS", jobs_html, "\n\n\n\n\nLIFE", life_html)
        return Company(overview_html, jobs_html, life_html, insights_html, people_html)

    def load_initial(self, url):
        self.driver.get(url)
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.organization-outlet')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")
        try:
            self.driver.find_element_by_css_selector('.organization-outlet')
        except:
            raise ValueError(
                'Company Unavailable: Company link does not match any companies on LinkedIn')

    def get_overview(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_about_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_about_tab"].active')
            return self.driver.find_element_by_css_selector(
                '.organization-outlet').get_attribute('outerHTML')
        except:
            return ''

    def get_life(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_life_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_life_tab"].active')
            return self.driver.find_element_by_css_selector('.org-life').get_attribute('outerHTML')
        except:
            return ''

    def get_jobs(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_jobs_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_jobs_tab"].active')
            return self.driver.find_element_by_css_selector('.org-jobs-container').get_attribute('outerHTML')
        except:
            return ''


    def get_people(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_people_tab"]')
            tab_link.click()
            # triggering on the carousel element itself to wait when the page is lazy loaded.
            self.wait_for_el('ul.artdeco-carousel__slider')
            self.wait_for_el('li.artdeco-carousel__item')
            self.wait_for_el('div.artdeco-carousel__item-container')
            return self.driver.find_element_by_css_selector('.org-people__insights-container').get_attribute('outerHTML')
        except Exception as ex:
            print('Error: Could not get people html:\n{}'.format(ex))
            return ''

    def get_insights(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_insights_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_insights_tab"].active')
            return self.driver.find_element_by_css_selector('.org-premium-insights-module').get_attribute('outerHTML')
        except:
            return ''
