from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

medicines = ['crocin advance', 'allegra']

class DrugStore:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--disable-features=SameSiteByDefaultCookies')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=self.options)
    
    def fetch(self, medicines):
        data = []
        for medicine in medicines:
            try:
                self.url = f"https://www.google.com/search?q={medicine.replace(' ', '+')+'+1mg'}"
                self.driver.get(self.url)

                div = self.driver.find_element(By.ID, "search")
                links = div.find_elements(By.TAG_NAME, "a")
                href = links[0].get_attribute("href")
                self.driver.get(href)

                try:
                    cancel_button = self.driver.find_element(By.CLASS_NAME, "UpdateCityModal__cancel-btn___2jWwS")
                    cancel_button.click()
                except:
                    pass

                drug_header = self.driver.find_element(By.ID, "drug-main-header")
                data.append(drug_header.text)
                # print(drug_header.text)
            except:
                pass
        return data

if __name__ == "__main__":
    drugstore = DrugStore()
    data = drugstore.fetch(medicines)

    print(data)
