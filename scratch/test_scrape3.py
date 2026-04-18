from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

url = "https://www.whoscored.com/regions/81/tournaments/3/seasons/10720/stages/24478/fixtures/germany-bundesliga-2025-2026"
chrome_options = Options()

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(url)
    time.sleep(15)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    accordions = soup.find_all("div", class_=lambda x: x and "TournamentFixtures-module_accordion__" in x)
    
    if accordions:
        acc = accordions[0]
        # Just grab the children inside the accordion content
        for child in acc.descendants:
            if child.name in ['div', 'span', 'a'] and child.string:
                text = child.string.strip()
                if text:
                    with open("scratch/acc_texts.txt", "a", encoding="utf-8") as f:
                        f.write(text + "\n")
except Exception as e:
    print(e)
finally:
    driver.quit()
