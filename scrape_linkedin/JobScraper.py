from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

import time
from .Job import Job
from .utils import AnyEC


class JobScraper(Scraper):
    """
    Scraper for Job pages. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.core-rail'
    ERROR_SELECTOR = '.not-found-404'

    def scrape(self, url=''):
        self.load_job_page(url)
        return self.get_job()

    def load_job_page(self, url=''):
        """Load job page and all async content

        Params:
            - url {str}: url of the job page to be loaded
        Raises:
            ValueError: If link doesn't match a typical jobs url
        """
        if 'com/jobs/view/' not in url:
            raise ValueError(
                "Url must look like... linkedin.com/jobs/view/<JOB_ID_CONTENT>")

        self.driver.get(url)
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
