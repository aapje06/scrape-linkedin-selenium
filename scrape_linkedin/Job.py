from .utils import *
from .ResultsObject import ResultsObject
from datetime import datetime
import re


class Job(ResultsObject):
    """Linkedin Job offer Object"""

    attributes = ['summary', 'company',
                  'similar_jobs', 'poster', 'date_scraped']

    @property
    def date_scraped(self):
        """Returns the date that this object is created"""
        return datetime.now().strftime('%Y-%m-%d, %H:%M:%S')

    @property
    def summary(self):
        """ Returns the summary overview of the job posting """
        job_info_elem = one_or_default(self.soup, 'div.jobs-top-card')
        summary = get_info(job_info_elem, {
            'title': 'h1.jobs-top-card__job-title',
            'post_date': 'h3.jobs-top-card__company-info + p > span:not([class])',
            'description': 'div.jobs-description-content__text'
        })
        detailed_job_info_elem = one_or_default(job_info_elem, 'div.jobs-description-details')
        job_details_elems = all_or_default(detailed_job_info_elem, 'div.jobs-box__group')
        for job_details_elem in job_details_elems:
            detail_title = text_or_default(job_details_elem, '.jobs-box__sub-title')
            detail_title = detail_title.lower().replace(' ', '_')
            detail_value = text_or_default(job_details_elem, '.jobs-box__body')
            detail_value_list = all_or_default(job_details_elem, 'li.jobs-box__list-item', None)
            if detail_value_list is not None:
                detail_value = [cleanup_text(x.get_text()) for x in detail_value_list]

            summary[detail_title] = detail_value

        return summary


    @property
    def company(self):
        """ Returns the overview of the company that posted the job opening """
        company = {}
        job_title_elem = one_or_default(self.soup, 'div.jobs-top-card')

        possbile_location_elem = all_or_default(job_title_elem, 'span.a11y-text + *')[1]
        if possbile_location_elem.name == 'span':
            company['location'] = cleanup_text(possbile_location_elem.get_text())
        else:
            company['location'] = cleanup_text(one_or_default(job_title_elem, 'h3.jobs-top-card__company-info a.jobs-top-card__exact-location').get_text())

        h3_elem = one_or_default(job_title_elem, 'h3.jobs-top-card__company-info')
        company_info = re.search(r'Company Name(.*)Company Location(.*)', h3_elem.get_text(), re.S)
        company['name'] = cleanup_text(company_info.group(1))
        company['location'] = cleanup_text(company_info.group(2))

        company_url_elem = one_or_default(job_title_elem, 'h3.jobs-top-card__company-info > a[data-control-name="company_link"]')
        if company_url_elem is not None:
            company['url'] = 'www.linkedin.com' + company_url_elem['href']

        company_elem = one_or_default(self.soup, 'div.jobs-company')
        if company_elem is not None:
            company['about'] = text_or_default(company_elem, '.jobs-company__description')
            company_sector_elem = one_or_default(company_elem, '.jobs-company-information__follow')
            company['sector'] = cleanup_text(company_sector_elem.find(text=True, recursive=False))
            company['followers'] = text_or_default(company_elem, '.jobs-company-information__follow-count').replace(' followers','').replace(',', '')

        return company


    @property
    def poster(self):
        """ Returns the overview of the Person that created the job posting if available """
        poster = {}
        poster_elem = one_or_default(self.soup, '.jobs-poster')
        if poster_elem is not None:
            poster['name'] = text_or_default_no_children(poster_elem, '.jobs-poster__name')
            poster['connected'] = text_or_default(poster_elem, '.jobs-poster__name > span')
            poster['headline'] = text_or_default(poster_elem, '.jobs-poster__headline')
            poster_head_elem = one_or_default(poster_elem, 'a[data-control-name="jobdetails_profile_poster"]')
            poster['url'] = 'www.linkedin.com' + poster_head_elem['href']
            poster['img'] = one_or_default(poster_head_elem, 'img')['src']
        return poster

    @property
    def similar_jobs(self):
        """ Returns a list of similar jobs to the scraped job opening """
        similar_jobs = []
        jobs_elem = one_or_default(self.soup, '.jobs-similar-jobs')

        job_elems = all_or_default(jobs_elem, 'ul li.jobs-similar-jobs__list-item')
        for job_elem in job_elems:
            similar_job = {}
            similar_job['title'] = text_or_default(job_elem, '.job-card__title')
            similar_job['company'] = text_or_default(job_elem, '.job-card__company-name')
            similar_job['location'] = text_or_default_no_children(job_elem, 'h5.job-card__location')
            similar_job['date_posted'] = text_or_default(job_elem, '.job-card__time-badge')
            raw_job_url = one_or_default(job_elem, 'a.job-card__link-wrapper')['href']
            raw_job_url_matcher = re.match(r'(/jobs/view/\d{10}/).*', raw_job_url)
            job_url = raw_job_url_matcher.group(1)
            similar_job['url'] = 'www.linkedin.com' + job_url
            similar_jobs.append(similar_job)

        return similar_jobs
