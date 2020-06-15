from scrape_linkedin import ProfileScraper
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1200,800")


import json

with ProfileScraper(driver_options={'chrome_options':options}) as scraper:
    profile = scraper.scrape(user='mathias-de-roover')

data = profile.to_dict()
# print(data)

data_json = json.dumps(data)

print(data_json)
