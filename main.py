from abc import ABC, abstractmethod

from joblib import Parallel, delayed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.ui import WebDriverWait

from calculator import Calculator
from local_settings import CREDENTIALS
from py_files.chrome_driver import Driver

SITES = sorted(CREDENTIALS)
PLACE_YOUR_BETS = 'PLACE YOUR BETS'


class Iframe:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        """ ENTERING IFRAMES """
        self.driver.wait_until('[id^="GameflexWidget"]')
        iframes = self.driver.driver.find_elements_by_tag_name('iframe[id^="GameflexWidget"]')
        self.driver.driver.switch_to.frame(iframes[-1])

        self.driver.wait_until('[id="GameObjectContainer"]')
        iframes = self.driver.driver.find_elements_by_tag_name('iframe[id="GameObjectContainer"]')
        self.driver.driver.switch_to.frame(iframes[-1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.driver.switch_to.default_content()  # switch back to the main window


class AbstractTab(ABC):
    @abstractmethod
    def _get_bet_spots(self):
        pass

    @abstractmethod
    def get_current_balance(self):
        pass

    @abstractmethod
    def get_total_bet(self):
        pass

    @abstractmethod
    def get_recent_number(self):
        pass

    @abstractmethod
    def get_recent_numbers(self):
        pass


class TextToChange:
    def __init__(self, locator, text=PLACE_YOUR_BETS):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        actual_text = _find_element(driver, self.locator).text
        if actual_text != self.text and actual_text == PLACE_YOUR_BETS:
            return True
        self.text = actual_text
        return False


class Tab(AbstractTab):
    def __init__(self, window_name, driver, roulette_type, credentials):
        self.driver = driver
        self.window_name = window_name
        self.credentials = credentials
        self.bet_spots = self._get_bet_spots()
        self.calculator = Calculator()

    def _get_bet_spots(self):
        self.bet_spot_field = self.credentials["bet_spot"]
        with Iframe(self.driver):
            # self.driver.wait_until(f'//*[@{self.bet_spot_field}]', selector_type='xpath')  # NB: doesn't work
            bet_spots = self.driver.driver.find_elements_by_xpath(f'//*[@{self.bet_spot_field}]')
            bet_spots = [bet_spot.get_attribute(self.bet_spot_field) for bet_spot in bet_spots]
        return bet_spots

    def get_current_balance(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['current_balance'])
            balance = self.driver.find_element_by_css_selector(self.credentials['current_balance'])
            # balance = float(balance.text)
        return balance

    def get_total_bet(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['total_bet'])
            balance = self.driver.find_element_by_css_selector(self.credentials['total_bet'])
            # balance = float(balance.text)
        return balance

    def get_recent_number(self):
        """ returns recent number """
        return self.get_recent_numbers()[0]

    def get_recent_numbers(self):
        """ returns recent numbers """
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['recent_number'])
            numbers = self.driver.find_elements_by_css_selector(self.credentials['recent_number'])
            numbers = [int(number.text) for number in numbers]
        return numbers

    def set_radial_chips(self, num=0):
        with Iframe(self.driver):
            WebDriverWait(self.driver.driver, 60).until(
                TextToChange((By.CSS_SELECTOR, self.credentials['status_text']), PLACE_YOUR_BETS)
            )
            chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
            self.driver.execute_script('arguments[0].click();', chips[num])

    def make_bets(self):
        while True:
            print(self.window_name)
            self.driver.driver.switch_to.window(self.window_name)
            self.set_radial_chips(num=0)  # WAITING HERE
            number = self.get_recent_number()
            self.calculator.set_number(number)
            recommended_numbers = self.calculator.get_recommended_values()
            if not recommended_numbers:
                continue
            print(f'recommended_numbers: {recommended_numbers}')
            # with Iframe(self.driver):
            #     for recommended_number in recommended_numbers:
            #         self.driver.find_elements_by_css_selector(
            #             f'[{self.bet_spot_field}={recommended_number}]')

    def __del__(self):
        self.calculator.app.kill()


class Browser:
    def __init__(self, site=SITES[0], driver=None, **kwargs):
        assert site in SITES, "site should be either of " + str(SITES)
        self.credentials = CREDENTIALS[site]
        if driver is None:
            self.driver = Driver(**kwargs)
        else:
            self.driver = driver
        self.login()
        self.tabs = self._get_tabs()

    def _get_tabs(self, tables=None):
        if tables is None:
            self.driver.wait_until(self.credentials['tables'])
            tables = self.driver.find_elements_by_css_selector(self.credentials['tables'])
            table_names = self.driver.find_elements_by_css_selector(self.credentials['table_names'])
            table_names = [table_name.text.strip().lower() for table_name in table_names]
        else:
            raise NotImplemented
        assert len(tables) == len(table_names)
        tabs = []
        j = 0
        for i, table in enumerate(tables):
            if self.credentials['live_roulette_lobby'] == table_names[i]:
                self.driver.execute_script("arguments[0].scrollIntoView();", table)
                table.click()
                with Iframe(self.driver):
                    self.driver.wait_until(self.credentials['live_roulette_tables'])
                    inner_tables = self.driver.find_elements_by_css_selector(
                        self.credentials['live_roulette_tables'])
                for inner_i, inner_table in enumerate(inner_tables):
                    # TODO: remove later
                    if inner_i not in [8, 9]:
                        continue

                    self.driver.execute_script(f"window.open('{self.credentials['site']}', '{j}');")
                    self.driver.driver.switch_to.window(f'{j}')

                    tables_inner = self.driver.find_elements_by_css_selector(self.credentials['tables'])
                    tables_inner[0].click()

                    with Iframe(self.driver):
                        self.driver.wait_until(self.credentials['live_roulette_tables'])
                        inner_inner_tables = self.driver.find_elements_by_css_selector(
                            self.credentials['live_roulette_tables'])
                        inner_inner_tables[inner_i].click()
                        roulette_type = table_names[i].lower()
                    tabs.append(Tab(f'{j}', self.driver, roulette_type, self.credentials))
                    j += 1
            # TODO: remove later
            break
            # else:
            #     self.driver.execute_script(f"window.open('{self.credentials['site']}', '{j}');")
            #     self.driver.switch_to_window(f'{j}')
            #     inner_tables = self.driver.find_elements_by_css_selector(self.credentials['tables'])
            #     self.driver.execute_script("arguments[0].scrollIntoView();", inner_tables[i])
            #     inner_tables[i].click()
            #     roulette_type = table_names[i].lower()
            #     tabs.append(Tab(self.driver, roulette_type, self.credentials))
            #     j += 1

        return tabs

    def login(self, auto_captcha_bypassing=False):
        self.driver.get(self.credentials['site'])

        if not self.credentials['manual_login']:
            # self.driver.wait_until(self.credentials['login_button'])
            login_button = self.driver.find_element_by_css_selector(self.credentials['login_button'])
            if login_button is not None:
                login_button.click()

            self.driver.wait_until('[name="username"]')
            self.driver.find_element_by_css_selector('[name="username"]').send_keys(self.credentials['user'])
            self.driver.find_element_by_css_selector('[name="password"]').send_keys(self.credentials['password'])

            # automatic CAPTCHA bypassing
            if auto_captcha_bypassing:
                self.driver.wait_until(
                    "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']",
                    selector_type='css', captcha=True,
                )
                self.driver.wait_until(
                    "//span[@id='recaptcha-anchor']",
                    selector_type='xpath', captcha=True,
                )
            self.driver.find_element_by_css_selector('[type="submit"]').click()
        # else:
        #     input('Please, press ENTER when logged in: ')

        self.driver.cookie.save_cookie()

        self.driver.get(self.credentials['site'])
        # input("STOP: ")
        # тут явно таймслип нужен и проверка на то, что зашлось в акк

    def run_roulettes(self):
        Parallel(n_jobs=-1)(delayed(tab.make_bets)() for tab in self.tabs)


def main():
    browser = Browser(site='pinnacle')
    browser.run_roulettes()
    # browser.run_roulettes()


if __name__ == "__main__":
    main()

# from main import *; from selenium import webdriver; from py_files.cookie import Cookie; from local_settings import CREDENTIALS
# driver = webdriver.Chrome('chromedriver.exe', options=webdriver.ChromeOptions())
# driver.get('https://www.google.com')
# cookie = Cookie(driver, 'cookie.txt')
# cookie.load_cookie()
# driver.get('https://www1.pinnacle.com/en/casino/games/live/roulette')
# class self:
#     driver = driver
#     credentials = CREDENTIALS['pinnacle']
#
# tables = self.driver.find_elements_by_css_selector(self.credentials['tables'])
# table_names = self.driver.find_elements_by_css_selector(self.credentials['table_names'])
# table_names = [table_name.text.strip().lower() for table_name in table_names]
