import functools
import time
from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import _find_element

from calculator import Calculator, TABLES
from local_settings import CREDENTIALS
from py_files.chrome_driver import Driver

SITES = sorted(CREDENTIALS)
PLACE_YOUR_BETS = 'PLACE YOUR BETS'
BETS_CLOSING = 'BETS CLOSING'
RULE_BREAKS = [
    'Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний', 'Нет'
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
        # self.driver.wait_until(self.locator[-1])  # NB: check if there is a problem
        while True:
            try:
                actual_text = _find_element(self.driver.driver, self.locator).text
                break
            except Exception:
                pass
        if actual_text != self.text and actual_text in [PLACE_YOUR_BETS, BETS_CLOSING] \
                and not (actual_text == BETS_CLOSING and self.text == PLACE_YOUR_BETS):
            return True
        self.text = actual_text
        return False


def activate_tab(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        args[0].driver.driver.switch_to.window(args[0].window_name)
        value = func(*args, **kwargs)
        return value

    return wrapper_decorator


class Tab(AbstractTab):
    def __init__(self, window_name, driver, credentials, **kwargs):
        self.driver = driver
        self.window_name = window_name
        self.credentials = credentials
        self.calculator = Calculator(**kwargs)
        self.calculator.change_tab(TABLES)
        self.text_to_change = TextToChange(
            (By.CSS_SELECTOR, self.credentials['status_text']), self.driver, PLACE_YOUR_BETS)

        # SET VIDEO SETTINGS
        self._set_video_settings()

        self.bet_spots = self._get_bet_spots()

        # CONDITIONS
        self.rule_break = kwargs['rule_break']
        self.rule_break_second = kwargs['rule_break_second']
        self.rule_break_value = kwargs['rule_break_value_first']
        self.rule_break_value_second = kwargs['rule_break_value_second']
        self.rule_break_strict = kwargs['rule_break_strict']
        self.num_of_repetitions = kwargs['num_of_repetitions']
        self.play_real = kwargs['play_real']
        self.num_of_fails = 0
        self.prev_prediction = set()
        self.turn_on = True

    @activate_tab
    def _set_video_settings(self):
        with Iframe(self.driver):
            self.driver.wait_until('[data-role="settings-button"]')
            self.driver.find_element_by_css_selector('[data-role="settings-button"]').click()
            time.sleep(0.5)
            self.driver.wait_until('[data-role="tab-settings.video"]')
            self.driver.find_element_by_css_selector('[data-role="tab-settings.video"]').click()
            time.sleep(0.5)
            self.driver.wait_until('[data-role="select-option"]')
            self.driver.find_elements_by_css_selector('[data-role="select-option"]')[-1].click()
            time.sleep(0.5)
            self.driver.wait_until('[data-role="window-preferences_close"]')
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

    @activate_tab
    def _get_bet_spots(self):
        self.bet_spot_field = self.credentials["bet_spot"]
        with Iframe(self.driver):
            bet_spots = self.driver.driver.find_elements_by_xpath(
                "//*[@class='slingshot-wrapper']//*[@data-bet-spot-id]")
            bet_spots = {bet_spot.get_attribute(self.bet_spot_field): bet_spot for bet_spot in bet_spots}
        return bet_spots

    @activate_tab
    def get_current_balance(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['current_balance'])
            balance = self.driver.find_element_by_css_selector(self.credentials['current_balance'])
            # balance = float(balance.text)
        return balance

    @activate_tab
    def get_total_bet(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['total_bet'])
            balance = self.driver.find_element_by_css_selector(self.credentials['total_bet'])
            # balance = float(balance.text)
        return balance

    @activate_tab
    def get_recent_number(self):
        """ returns recent number """
        return self.get_recent_numbers()[0]

    @activate_tab
    def get_recent_numbers(self):
        """ returns recent numbers """
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['recent_number'])
            numbers = self.driver.find_elements_by_css_selector(self.credentials['recent_number'])
            numbers = [int(number.text) for number in numbers]
        return numbers

    @activate_tab
    def make_bets(self):
        self.driver.driver.switch_to.window(self.window_name)
        # self.set_radial_chips(num=0)  # WAITING HERE
        with Iframe(self.driver):
            if not self.text_to_change():
                return
            self.text_to_change = TextToChange(
                (By.CSS_SELECTOR, self.credentials['status_text']), self.driver, PLACE_YOUR_BETS)
        number = self.get_recent_number()
        if number not in self.prev_prediction:
            self.num_of_fails += 1
        else:
            if self.num_of_repetitions and self.rule_break != RULE_BREAKS[2]:
                self.rule_break_value = self.rule_break_value_second
                self.rule_break = self.rule_break_second
                self.turn_on = True
                self.num_of_fails = 0
                self.num_of_repetitions -= 1

        self.calculator.set_number(number)

        recommended_numbers = self.calculator.get_recommended_values()
        self.prev_prediction = set(recommended_numbers)

        if self.rule_break == RULE_BREAKS[0]:
            max_ = self.calculator.get_field_value('Max')
            balance = self.calculator.get_field_value('Суммарный баланс')
            if max_ - balance >= self.rule_break_value:
                if not self.rule_break_strict:
                    if number not in self.prev_prediction:
                        self.turn_on = False
                else:
                    self.turn_on = False
        elif self.rule_break == RULE_BREAKS[1]:
            if self.num_of_fails >= self.rule_break_value:
                self.turn_on = False
        else:  # self.rule_break == 'Нет'
            pass
        if not self.turn_on:
            return

        bet = self.calculator.get_field_value('Ставка')  # NB (with double)
        with Iframe(self.driver):
            print(f'recommended_numbers: {recommended_numbers}')
            # SET CHIPS
            chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
            self.driver.execute_script('arguments[0].click();', chips[0])  # HARDCODE HERE

            for recommended_number in recommended_numbers:
                self.bet_spots[str(recommended_number)].click()
                # self.driver.find_elements_by_css_selector(
                #     f'[{self.bet_spot_field}="{}"]').click()
                if False:  # NEED TO DOUBLE?
                    self.driver.find_elements_by_css_selector('[data-role="repeat-button"]').click()
            if not self.play_real:
                undo_button = self.driver.find_element_by_css_selector('[data-role="undo-button"]')
                for _ in range(len(recommended_numbers)):
                    undo_button.click()

    # def __del__(self):
    #     self.calculator.app.kill()


class Browser:
    def __init__(self, site=SITES[0], driver=None, **kwargs):
        assert site in SITES, "site should be either of " + str(SITES)
        self.credentials = CREDENTIALS[site]
        if driver is None:
            self.driver = Driver(**kwargs)
        else:
            self.driver = driver
        self.login()
        self.num_of_tables = kwargs.get('num_of_tables')
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
            self.driver.driver.maximize_window()
            if self.credentials['live_roulette_lobby'] == table_names[i]:
                self.sleep(2.5)
                self.driver.execute_script("arguments[0].scrollIntoView();", table)
                self.sleep(1.5)
                table.click()
                with Iframe(self.driver):
                    self.driver.wait_until(self.credentials['live_roulette_tables'])
                    self.sleep(0.5)
                    inner_tables = self.driver.find_elements_by_css_selector(
                        self.credentials['live_roulette_tables'])
                for inner_i, inner_table in enumerate(inner_tables):
                    # TODO: remove later
                    if inner_i not in [8, 9, 10][:self.num_of_tables]:
                        continue

                    self.driver.execute_script(f"window.open('{self.credentials['site']}', '{j}');")
                    self.driver.driver.switch_to.window(f'{j}')
                    self.sleep(0.5)
                    self.driver.wait_until(self.credentials['tables'])

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
                self.driver.wait_until(self.credentials['login_check'], timeout=300)
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
                time.sleep(0.2)
                # print(tab.num_of_fails, tab.prev_prediction, tab.turn_on)
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
