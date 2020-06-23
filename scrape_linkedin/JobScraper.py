from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

import time
from .Job import Job
from .JobList import JobList
from .utils import *

from enum import Enum

class ExperienceLevel(Enum):
    INTERNSHIP = 'Internship'
    ENTRY_LEVEL = 'Entry level'
    ASSOCIATE = 'Associate'
    MID_SENIOR_LEVEL = 'Mid-Senior level'
    DIRECTOR = 'Director'
    EXECUTIVE = 'Executive'

class JobType(Enum):
    FULLTIME='Full-time'
    TEMPORARY='Temporary'
    CONTRACT='Contract'

class DatePosted(Enum):
    PAST_DAY='Past 24 hours'
    PAST_WEEK='Past Week'
    PAST_MONTH='Past Month'
    ANY_TIME='Any Time'

class JobScraper(Scraper):
    """
    Scraper for Job pages. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.core-rail'
    ERROR_SELECTOR = '.not-found-404'

    def search_jobs_scrape(self, description, location=None, experience_level=None, job_type=None, date_posted=None, max_number_of_pages=5):
        self.max_job_pages_to_scrape = max_number_of_pages
        self.load_job_search_page()
        # Fill in details here

        keyword_search_box = self.driver.find_element_by_css_selector('input[id*="jobs-search-box-keyword"]')
        keyword_search_box.send_keys(description)
        if location is not None:
            location_search_box = self.driver.find_element_by_css_selector('input[id*="jobs-search-box-location"]')
            location_search_box.clear()
            location_search_box.send_keys(location)
            location_search_box.send_keys(Keys.ENTER)
        
        # Applying other filters:
        self.wait_for_el('button[data-control-name="all_filters"]').click()


        # setting the experience level
        if experience_level is not None:
            experience_level_list = None
            try:
                self.wait_for_el('ul.search-advanced-facets__facets-list')
                self.wait_for_el('li legend[aria-label="Filter by: Experience Level"] + ol li.search-s-facet-value')
                experience_level_list = self.wait_for_el('li legend[aria-label="Filter by: Experience Level"] + ol')
            except:
                print('ERROR: could not find experience list element')

            if experience_level_list is not None:
                level_elems = experience_level_list.find_elements_by_css_selector('li.search-s-facet-value')
                for level_elem in level_elems:
                    level_text = level_elem.find_element_by_css_selector('span.search-s-facet-value__name').get_attribute('innerHTML')
                    if experience_level.value in level_text:
                        print('clicked: {}'.format(experience_level.value))
                        level_elem.click()

        # Setting the job type
        if job_type is not None:
            job_type_list = None
            try:
                self.wait_for_el('ul.search-advanced-facets__facets-list')
                self.wait_for_el('li legend[aria-label="Filter by: Job Type"] + ol li.search-s-facet-value')
                job_type_list = self.wait_for_el('li legend[aria-label="Filter by: Job Type"] + ol')
            except:
                print('ERROR: could not find job type list element')

            if experience_level is not None and job_type_list is not None:
                job_type_elems = job_type_list.find_elements_by_css_selector('li.search-s-facet-value')
                for job_type_elem in job_type_elems:
                    level_text = job_type_elem.find_element_by_css_selector('span.search-s-facet-value__name').get_attribute('innerHTML')
                    if job_type.value in level_text:
                        print('clicked: {}'.format(job_type.value))
                        job_type_elem.click()

        # Setting the Date posted
        if date_posted is not None:
            date_posted_list = None
            try:
                self.wait_for_el('ul.search-advanced-facets__facets-list')
                self.wait_for_el('li legend[aria-label="Filter by: Date Posted"] + ol li.search-s-facet-value')
                date_posted_list = self.wait_for_el('li legend[aria-label="Filter by: Date Posted"] + ol')
            except:
                print('ERROR: could not find job type list element')

            if experience_level is not None and date_posted_list is not None:
                date_posted_elems = date_posted_list.find_elements_by_css_selector('li.search-s-facet-value')
                for date_posted_elem in date_posted_elems:
                    level_text = date_posted_elem.find_element_by_css_selector('span.search-s-facet-value__name').get_attribute('innerHTML')
                    if date_posted.value in level_text:
                        print('clicked: {}'.format(date_posted.value))
                        date_posted_elem.click()

        try:
            apply_button = self.driver.find_element_by_css_selector('button.search-advanced-facets__button--apply')
            apply_button.click()

            search_button = self.driver.find_element_by_css_selector('button.jobs-search-box__submit-button')
            search_button.click()
        except Exception as ex:
            raise Exception('Something when wrong while setting job search options: Could not click apply or find button...: {}'.format(ex))
        

        return self.get_job_list()

    def scrape(self, url=''):
        """
        Loads the requested URL and will scrape all the data on the page

        Params:
            - URL: {str}: The url of the job page to be scraped
        Returns:
            - HTML {str}: The HTML code of that page
        """
        self.load_job_page(url)
        return self.get_job()

    def load_job_search_page(self):
        """
        Loads the job search page

        Raises:
            ValueError: If the page cannot be reached.
        """
        job_search_url = 'https://www.linkedin.com/jobs/search'
        try:
            self.driver.get(job_search_url)
        except WebDriverException as webEx:
            raise ValueError("Could not fetch the job search page [{}] Error: {}".format(job_search_url, webEx))

        # Wait for page to load dynamically via javascript
        try:
            self.wait_for_el('.jobs-search-two-pane__wrapper')
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load job search page.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the time out parameter in the Scraper
                   constructor
                """)

    def load_job_page(self, url=''):
        """Load job page and all async content

        Params:
            - url {str}: url of the job page to be loaded
        Raises:
            ValueError: If link doesn't match a typical jobs url
        """
        if 'com/jobs/view/' not in url:
            raise ValueError(
                "Url must look like... https://www.linkedin.com/jobs/view/<JOB_ID_CONTENT>")

        try:
            self.driver.get(url)
        except WebDriverException as webEx:
            raise ValueError("Could not fetch the requred page with the URL [{}] Probably wrong formatted URL. Error: {}".format(url, webEx))

        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.ERROR_SELECTOR))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load job page.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the time out parameter in the Scraper
                   constructor
                3. Make sure the provided URL is working
                """)

        # Check if we got the 'Job unavailable' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            raise ValueError(
                'Profile Unavailable: Job link does not match any current Job Profiles')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    

    def get_job(self):
        try:
            profile = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
        except:
            raise Exception(
                "Could not find job wrapper html. This sometimes happens for exceptionally long Jobs.  Try decreasing scroll-increment.")
        job = Job(profile)
        return job

    def get_job_list(self):
        # First check if there are any available results
        try:
            self.wait_for_el('div.jobs-search-two-pane__no-results-banner--expand', timeout=5)
        except Exception as ex:
            pass
        else:
            # raise Exception('No jobs found matching the criteria...')
            return JobList('')

        output = ''
        counter = 1
        try:
            while True:
                self.wait_for_el('li.artdeco-list__item')
                self.wait_for_el('a.job-card-list__title')

                retry_counter = 0
                while retry_counter < 5:
                    try:
                        job_list = self.wait_for_el('div.jobs-search-results')
                        self.scroll_to_bottom_element(job_list)
                        break
                    except StaleElementReferenceException as ex:
                        retry_counter += 1
                        if retry_counter >= 5:
                            raise Exception("could not scroll to the bottom of the element: {}".format(job_list))

                job_elems = job_list.find_elements_by_css_selector('li.artdeco-list__item')
                try:
                    self.wait(lambda d: job_elems[-1].find_element_by_css_selector('a.job-card-container__link'))
                except:
                    time.sleep(1)

                output += job_list.get_attribute('outerHTML')
                counter += 1
                if counter > self.max_job_pages_to_scrape:
                    break
                try:
                    next_button_list_elem = self.driver.find_element_by_css_selector('ul.artdeco-pagination__pages')
                    next_button_elem = next_button_list_elem.find_element_by_css_selector('li[data-test-pagination-page-btn="{}"'.format(counter))
                except:
                    break
                next_button_elem.click()
        except Exception as ex:
            raise Exception(
                "Could not fetch the list of found jobs.: {}".format(ex))
        job_list = JobList(output)
        return job_list