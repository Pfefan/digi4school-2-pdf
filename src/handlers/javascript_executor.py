from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .authentication import AuthAndTokenHandler


class Executor():
    LOGIN_URL = "https://digi4school.at/"
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--silent")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.minimize_window()
        self.login()

    def login(self):
        config_data = AuthAndTokenHandler().get_data()
        self.driver.get(self.LOGIN_URL)
        self.driver.find_element(By.ID, 'email').send_keys(config_data["email"])
        self.driver.find_element(By.ID, 'password').send_keys(config_data["password"])
        self.driver.find_element(By.CSS_SELECTOR, 'form#login button').click()

    def execute_js(self, url, js_code):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'shelf')))
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        result = self.driver.execute_script(js_code)
        self.driver.quit()
        return result

    def find_first_non_titlepage(self, url):
        js_query = """
        for (var pageNumber = 1; isNaN(encodePageNumber(pageNumber)); pageNumber++);
        return pageNumber;
        """
        return self.execute_js(url, js_query)
