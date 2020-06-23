from .utils import *
from .ResultsObject import ResultsObject
from datetime import datetime
import re


class JobList(ResultsObject):
    """Linkedin Job offer Object"""

    attributes = ['jobs']

    @property
    def jobs(self):
        jobs = []
        carousels =  all_or_default(self.soup, 'ul.jobs-search-results__list')
        for carousel in carousels:
            cards = all_or_default(carousel, 'li.artdeco-list__item')
            for card in cards:
                job = {}
                incomplete = False
                url_elem = one_or_default(card, 'a.job-card-container__link.job-card-list__title')
                if url_elem is not None:
                    job_title = cleanup_text(url_elem.get_text())
                    raw_job_url = url_elem['href']
                    job['title'] = job_title
                    if raw_job_url is not None:
                        raw_job_url_matcher = re.match(r'(/jobs/view/\d{10}/).*', raw_job_url)
                        if raw_job_url_matcher is not None:
                            job_url = raw_job_url_matcher.group(1)
                            job['url'] = 'https://www.linkedin.com' + job_url
                else:
                    incomplete = True
                location_elem = one_or_default(card, 'div.artdeco-entity-lockup__caption')
                if location_elem is not None:
                    job_location = cleanup_text(location_elem.get_text())
                    job['location'] = job_location
                else:
                    incomplete = True
                date_elem = one_or_default(card, 'div.job-card-container__footer-wrapper > time', default=None)
                if date_elem is not None:
                    job['post_date'] = date_elem['datetime']
                else:
                    incomplete = True
                company_elem = one_or_default(card, '.job-card-container__company-name')
                if company_elem is not None:
                    job['company'] = cleanup_text(company_elem.get_text())
                    job['company_url'] = 'https://www.linkedin.com' + company_elem['href']
                if not incomplete:
                    jobs.append(job)
        return jobs