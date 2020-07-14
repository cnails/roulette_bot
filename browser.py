import time
from abc import ABC, abstractmethod

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.wait import WebDriverWait

from calculator import Calculator, TABLES
from local_settings import CREDENTIALS
from py_files.chrome_driver import Driver

SITES = sorted(CREDENTIALS)
PLACE_YOUR_BETS = 'PLACE YOUR BETS'
RULE_BREAKS = [
    'Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний',
]


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
    def __init__(self, locator, driver, text=PLACE_YOUR_BETS):
        self.locator = locator
        self.text = text
        self.driver = driver

    def __call__(self):
        actual_text = _find_element(self.driver, self.locator).text
        if actual_text != self.text and actual_text == PLACE_YOUR_BETS:
            return True
        self.text = actual_text
        return False


class Tab(AbstractTab):
    def __init__(self, window_name, driver, credentials, **kwargs):
        self.driver = driver
        self.window_name = window_name
        self.credentials = credentials
        self.bet_spots = self._get_bet_spots()
        self.calculator = Calculator(**kwargs)
        self.calculator.change_tab(TABLES)
        self.text_to_change = TextToChange(
            (By.CSS_SELECTOR, self.credentials['status_text']), self.driver.driver, PLACE_YOUR_BETS)

        # SET VIDEO SETTINGS
        self._set_video_settings()

        # CONDITIONS
        self.rule_break = kwargs['rule_break']
        self.rule_break_value = kwargs['rule_break_value']
        self.num_of_fails = 0
        self.prev_prediction = set()
        self.turn_on = True

    def _set_video_settings(self):
        with Iframe(self.driver):
            self.driver.find_element_by_css_selector('[data-role="settings-button"]').click()
            time.sleep(0.5)
            self.driver.find_element_by_css_selector('[data-role="tab-settings.video"]').click()
            time.sleep(0.5)
            self.driver.find_elements_by_css_selector('[data-role="select-option"]')[-1].click()
            time.sleep(0.5)
            self.driver.find_element_by_css_selector('[data-role="window-preferences_close"]').click()
            time.sleep(0.5)
            for cross in self.driver.find_elements_by_css_selector(self.credentials['cross']):
                self.driver.execute_script(
                    "arguments[0].setAttribute('opacity', '1')", cross
                )
            for first_stripe in self.driver.find_elements_by_css_selector(self.credentials['first_stripe']):
                self.driver.execute_script(
                    "arguments[0].setAttribute('opacity', '0')", first_stripe
                )
            for second_stripe in self.driver.find_elements_by_css_selector(self.credentials['second_stripe']):
                self.driver.execute_script(
                    "arguments[0].setAttribute('opacity', '0')", second_stripe
                )

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
            # WebDriverWait(self.driver.driver, 60).until(
            #
            # )
            chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
            self.driver.execute_script('arguments[0].click();', chips[num])

    def make_bets(self):
        print(self.window_name)
        self.driver.driver.switch_to.window(self.window_name)
        # self.set_radial_chips(num=0)  # WAITING HERE
        with Iframe(self.driver):
            if not self.text_to_change():
                return
            self.text_to_change = TextToChange(
                (By.CSS_SELECTOR, self.credentials['status_text']), self.driver.driver, PLACE_YOUR_BETS)
        number = self.get_recent_number()
        if self.prev_prediction and number not in self.prev_prediction:
            self.num_of_fails += 1
        else:
            self.turn_on = True
            self.num_of_fails = 0
        self.calculator.set_number(number)
        recommended_numbers = self.calculator.get_recommended_values()
        # if not recommended_numbers:
        #     continue
        print(f'recommended_numbers: {recommended_numbers}')

        if self.rule_break == RULE_BREAKS[0]:
            max_ = self.calculator.get_field_value('Max')
            min_ = self.calculator.get_field_value('Min')
            if max_ - min_ >= self.rule_break_value:
                self.turn_on = False
        elif self.rule_break == RULE_BREAKS[1]:
            if self.num_of_fails >= self.rule_break_value:
                self.turn_on = False
        if not self.turn_on:
            return
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
        self.tabs = self._get_tabs(**kwargs)

    def sleep(self, quantity):
        time.sleep(quantity)

    def _get_tabs(self, tables=None, **kwargs):
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
                self.sleep(0.5)
                self.driver.execute_script("arguments[0].scrollIntoView();", table)
                self.sleep(0.5)
                table.click()
                with Iframe(self.driver):
                    self.driver.wait_until(self.credentials['live_roulette_tables'])
                    self.sleep(0.5)
                    inner_tables = self.driver.find_elements_by_css_selector(
                        self.credentials['live_roulette_tables'])
                for inner_i, inner_table in enumerate(inner_tables):
                    # TODO: remove later
                    if inner_i not in [8]:  # , 9, 10
                        continue

                    self.driver.execute_script(f"window.open('{self.credentials['site']}', '{j}');")
                    self.driver.driver.switch_to.window(f'{j}')
                    self.sleep(0.5)

                    tables_inner = self.driver.find_elements_by_css_selector(self.credentials['tables'])
                    self.driver.execute_script("arguments[0].scrollIntoView();", tables_inner[0])
                    self.sleep(1)
                    tables_inner[0].click()
                    self.sleep(0.5)

                    with Iframe(self.driver):
                        self.driver.wait_until(self.credentials['live_roulette_tables'])
                        inner_inner_tables = self.driver.find_elements_by_css_selector(
                            self.credentials['live_roulette_tables'])
                        self.driver.execute_script("arguments[0].scrollIntoView();", inner_inner_tables[inner_i])
                        self.sleep(1.5)
                        inner_inner_tables[inner_i].click()
                        roulette_type = table_names[i].lower()
                    tabs.append(Tab(f'{j}', self.driver, self.credentials, **kwargs))
                    self.sleep(1)
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
        if self.driver.find_element_by_css_selector(self.credentials['login_check']) is None:
            self.driver.get(self.credentials['login'])
            if self.credentials['manual_login']:
                self.driver.wait_until(self.credentials['login_check'], timeout=180)
                self.driver.cookie.save_cookie()
            else:
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

    def run_roulettes(self):
        while True:
            for tab in self.tabs:
                tab.make_bets()


def main():
    browser = Browser(site='pinnacle')
    browser.run_roulettes()


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
