
from scrape_linkedin import JobScraper, ExperienceLevel, JobType, DatePosted
import json


from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless")
options.add_argument("--window-size=1600,1000")


with JobScraper(driver_options={'options':options}) as scraper:
    job_list = scraper.search_jobs_scrape(
        description='devops',
        location='belgium',
        experience_level=ExperienceLevel.ENTRY_LEVEL,
        job_type=JobType.FULLTIME,
        date_posted=DatePosted.PAST_WEEK,
        max_number_of_pages=2
    )

    job_list_json = json.dumps(job_list.to_dict(), indent=4, ensure_ascii=False)
    print(job_list_json)

