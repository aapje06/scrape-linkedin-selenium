from .utils import *
from .ResultsObject import ResultsObject
from .JobList import JobList
from bs4 import BeautifulSoup
import re


class Company(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['overview', 'jobs', 'life', 'insights', 'people']
    # KD adds insights attribute

    def __init__(self, overview, jobs, life, insights, people):
        # KD fixed attributes making jobs and life undefined as they are defined in CompanyScraper, and this allows insights to work
        self.overview_soup = BeautifulSoup(overview, 'html.parser')
        self.jobs_soup = BeautifulSoup(jobs, 'html.parser')
        self.life_soup = BeautifulSoup(life, 'html.parser')
        self.insights_soup = BeautifulSoup(insights, 'html.parser')
        self.people_soup = BeautifulSoup(people, 'html.parser')
        # KD adds insights soup

    @property
    def overview(self):
        """Return dict of the overview section of the Linkedin Page"""

        # Banner containing company Name + Location
        banner = one_or_default(
            self.overview_soup, '.org-top-card')

        # Main container with company overview info
        container = one_or_default(
            self.overview_soup, '.org-grid__core-rail--wide')

        overview = {}
        description_element = container.select_one('section > p')
        if description_element is not None:
            overview['description'] = cleanup_text(
                description_element.get_text().strip())


        metadata_keys = container.select('.org-page-details__definition-term')
        # print(metadata_keys)
        metadata_keys = [x for x in metadata_keys if "Company size" not in x.get_text()]
        # print(metadata_keys)
        metadata_values = container.select(
            '.org-page-details__definition-text')
        overview.update(
            get_info(banner, {'name': '.org-top-card-summary__title'})) # A fix to the name selector
        overview.update(
            get_info(container, {'company_size': '.org-about-company-module__company-size-definition-text'})) # Manually added Company size

        for key, val in zip(metadata_keys, metadata_values):
            dict_key = key.get_text().strip().lower().replace(" ", "_")
            dict_val = val.get_text().strip()
            if "company_size" not in dict_key:
                overview[dict_key] = dict_val
        # print(overview)

        all_employees_links = all_or_default(
            banner, '.mt2 > a > span') # A fix to locate "See all ### employees on LinkedIn"

        if all_employees_links:
            all_employees_text = all_employees_links[-1].text
        else:
            all_employees_text = ''

        match = re.search(r'((\d+?,?)+)', all_employees_text)
        if match:
            overview['num_employees'] = int(match.group(1).replace(',', ''))
        else:
            overview['num_employees'] = None

        logo_image_tag = one_or_default(
            banner, '.org-top-card-primary-content__logo')
        overview['image'] = logo_image_tag['src'] if logo_image_tag else ''


        if 'specialties' in overview:
            overview['specialties'] = overview['specialties'].split(', ')
            overview['specialties'][-1] = overview['specialties'][-1].replace('and ', '')
        

        return overview

    @property
    def jobs(self):
        job_list = JobList('')
        job_list.soup = self.jobs_soup
        return job_list.jobs

    @property
    def life(self):
        return None

    # KD added property for Insights
    @property
    def insights(self):

        # summary table containing the Insights data for % change in headcount at 6m, 1y and 2y
        table = one_or_default(
            self.insights_soup, '.org-insights-module__summary-table')

        insights = {}

        insights.update(get_info(table, {
            '6m change': 'td:nth-of-type(2) span:nth-of-type(3)',
            '1y change': 'td:nth-of-type(3) span:nth-of-type(3)',
            '2y change': 'td:nth-of-type(4) span:nth-of-type(3)'

        }))
        return insights


    @property
    def people(self):
        people = {}
        people['statistics'] = []

        carrousel_tag = '.artdeco-carousel__item'

        carousels = all_or_default(self.people_soup, carrousel_tag)

        for carousel in carousels:
            statistics = {}
            carousel_text = cleanup_text(one_or_default(carousel, 'h4').get_text().strip())
            statistics['statistic'] = carousel_text
            statistics['data'] = []

            elems = all_or_default(carousel, '.mt4')

            for elem in elems:
                elem_data = one_or_default(elem, '.mt2')
                elem_number = one_or_default(elem_data, 'strong').get_text().strip().replace(',','')
                elem_text = one_or_default(elem_data, 'span').get_text().strip()
                data = {
                    'label': elem_text,
                    'amount': elem_number
                }
                statistics['data'].append(data)
            people['statistics'].append(statistics)

        return people
