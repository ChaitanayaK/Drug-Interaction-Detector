from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

class Interaction:
    def __init__(self):
        self.url = 'https://go.drugbank.com/drug-interaction-checker'
        self.options = Options()
        self.options.add_argument('--disable-features=SameSiteByDefaultCookies')
        # self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')

    def check(self, drugs:list):
        try:
            # self.driver = webdriver.Chrome()
            self.driver = webdriver.Chrome( options=self.options)
            self.driver.maximize_window()
            self.driver.set_window_rect(width=1200, height=900)
            self.driver.get(url=self.url)
            search_field = self.driver.find_element(By.CLASS_NAME, 'select2-search__field')

            for drug in drugs:
                search_field.send_keys(drug)
                sleep(2)
                search_field.send_keys(Keys.RETURN)

            button = self.driver.find_element(By.ID, 'search')
            button.click()

            try:
                parent_div = self.driver.find_element(By.CLASS_NAME, "drug-interactions")
                child_divs = parent_div.find_elements(By.XPATH, "./div")
                results = []
                for i, div in enumerate (child_divs):
                    new = div.text.split('\n')
                    label = {'drugs': [new[0], new[1]], 'severity': new[3], 'description': new[5], 'extended_discription': new[7]}
                    results.append(label)
                return results
            except:
                return None
        except Exception as e:
            print(e)
            return None
        finally:
            try:
                self.driver.quit()
            except:
                pass

if __name__ == "__main__":
    drugs = ['Doxycycline', 'Isotretinoin', 'calcium carbonate', 'Amoxycillin']

    interaction = Interaction()
    output = interaction.check(drugs)
    print('\n\n')
    for interactions in output:
        print(f'{interactions}\n')