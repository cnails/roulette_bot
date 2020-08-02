import functools
import time
from abc import ABC, abstractmethod
from math import floor, log

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import _find_element

from calculator import Calculator, TABLES
from local_settings import CREDENTIALS
from py_files.chrome_driver import Driver

SITES = sorted(CREDENTIALS)
PLACE_YOUR_BETS = 'PLACE YOUR BETS'
PLACE_YOUR_BETS_RU = 'ДЕЛАЙТЕ ВАШИ СТАВКИ'
BETS_CLOSING = 'BETS CLOSING'
BETS_CLOSING_RU = 'СТАВКИ ЗАКРЫВАЮТСЯ'
RULE_BREAKS = [
    'Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний', 'Нет'
]
BREAK_RULES = ('Максимальное количество неудачных предсказаний', 'Нет')
CHIPS = ['0.20', '0.50', '1', '5', '25', '100']


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
    def __init__(self, locator, driver, text=(PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU)):
        self.locator = locator
        self.text = text
        self.driver = driver
        self.number = -1

    def __call__(self):
        # self.driver.wait_until(self.locator[-1])  # NB: check if there is a problem
        while True:
            try:
                actual_text = _find_element(self.driver.driver, self.locator).text
                break
            except Exception:
                pass
        # print(time.time(), actual_text, self.text)
        if actual_text.startswith(('0', '1', '2', '3')):
            self.number = int(actual_text[:2].strip())
        if actual_text not in self.text and actual_text in \
                [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU, BETS_CLOSING, BETS_CLOSING_RU] and \
                not (actual_text in [BETS_CLOSING, BETS_CLOSING_RU] and
                     self.text == [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU]):
            return True
        if actual_text in [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU]:
            self.text = [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU]
        elif actual_text in [BETS_CLOSING, BETS_CLOSING_RU]:
            self.text = [BETS_CLOSING, BETS_CLOSING_RU]
        else:
            self.text = (actual_text,)
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
            (By.CSS_SELECTOR, self.credentials['status_text']), self.driver, [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU]
        )

        # SET VIDEO SETTINGS
        self._set_video_settings()

        # CHIPS
        self.chip_num = CHIPS.index(kwargs['chip'])

        self.bet_spots = self._get_bet_spots()

        # CONDITIONS
        self.rule_break = kwargs['rule_break']
        self.rule_break_second = kwargs['rule_break_second']
        self.rule_break_value = kwargs['rule_break_value_first']
        self.rule_break_value_second = kwargs['rule_break_value_second']
        self.num_of_repetitions = kwargs['num_of_repetitions']
        self.play_real = kwargs['play_real']
        self.num_of_fails = 0
        self.prev_prediction = set()
        self.turn_on = True

        self.spins_for_red = kwargs['spins_for_red']
        self.spin = 0
        self.last_made_bet = 0

        with Iframe(self.driver):
            self.chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])

    @activate_tab
    def _set_video_settings(self):
        with Iframe(self.driver):
            self.driver.wait_until('[data-role="switch-layout-button-container"] [data-role="button-bordered"]')
            self.driver.find_element_by_css_selector(
                '[data-role="switch-layout-button-container"] [data-role="button-bordered"]').click()
            time.sleep(0.5)
            # self.driver.wait_until('[data-role="settings-button"]')
            # self.driver.find_element_by_css_selector('[data-role="settings-button"]').click()
            # time.sleep(0.5)
            # self.driver.wait_until('[data-role="tab-settings.video"]')
            # self.driver.find_element_by_css_selector('[data-role="tab-settings.video"]').click()
            # time.sleep(0.5)
            # self.driver.wait_until('[data-role="select-option"]')
            # self.driver.find_elements_by_css_selector('[data-role="select-option"]')[-1].click()
            # time.sleep(0.5)
            # self.driver.wait_until('[data-role="window-preferences_close"]')
            # self.driver.find_element_by_css_selector('[data-role="window-preferences_close"]').click()
            # time.sleep(0.5)
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
                "//*[contains(@class,'slingshot-wrapper') or contains(@class,'classicStandard-wrapper')]//*[@data-bet-spot-id]")
            bet_spots = {bet_spot.get_attribute(self.bet_spot_field): bet_spot for bet_spot in bet_spots}
        return bet_spots

    @activate_tab
    def get_current_balance(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['current_balance'])
            balance = self.driver.find_element_by_css_selector(self.credentials['current_balance'])
            balance = float(balance.text.replace(',', '.'))
        return balance

    @activate_tab
    def get_total_bet(self):
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['total_bet'])
            balance = self.driver.find_element_by_css_selector(self.credentials['total_bet'])
            balance = float(balance.text.replace(',', '.'))
        return balance

    @activate_tab
    def get_recent_number(self):
        """ returns recent number """
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['recent_number'])
            numbers = self.driver.find_elements_by_css_selector(self.credentials['recent_number'])
            return int(numbers[0].text)

    @activate_tab
    def get_recent_numbers(self):
        """ returns recent numbers """
        with Iframe(self.driver):
            self.driver.wait_until(self.credentials['recent_number'])
            # '[data-role="recent-number"] span'
            numbers = self.driver.find_elements_by_css_selector(self.credentials['recent_number'])
            numbers = [int(number.text) for number in numbers]
        return numbers

    @activate_tab
    def set_zero_and_undo(self):
        with Iframe(self.driver):
            chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
            self.driver.execute_script('arguments[0].click();', chips[self.chip_num])
            self.bet_spots['0'].click()
            self.driver.find_element_by_css_selector('[data-role="undo-button"]').click()

    @activate_tab
    def make_bets(self, run, tab_num):  # gui_window,
        self.driver.driver.switch_to.window(self.window_name)
        # self.set_radial_chips(num=0)  # WAITING HERE
        with Iframe(self.driver):
            if not self.text_to_change():
                return
            number = self.text_to_change.number
            self.text_to_change = TextToChange(
                (By.CSS_SELECTOR, self.credentials['status_text']), self.driver, [PLACE_YOUR_BETS, PLACE_YOUR_BETS_RU])
        if number == -1:
            number = self.get_recent_number()
        if number not in self.prev_prediction:
            if self.prev_prediction:
                self.num_of_fails += 1
                # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[4][-1].update(self.num_of_fails)
        else:
            if self.num_of_repetitions and self.rule_break != RULE_BREAKS[2]:
                if not self.turn_on:
                    self.rule_break_value = self.rule_break_value_second
                    self.rule_break = self.rule_break_second
                    # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[3][-1].update(
                    #     f"{BREAK_RULES.index(self.rule_break) + 1} ({self.rule_break_value})")
                    self.turn_on = True
                    # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[0][-1].update('ДА')
                    # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[0][-1].update(text_color='darkgreen')
                    self.num_of_repetitions -= 1
                    # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[2][-1].update(str(self.num_of_repetitions))
            self.num_of_fails = 0
            # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[4][-1].update(str(self.num_of_fails))

        self.calculator.set_number(number)
        self.spin += 1
        # self.set_zero_and_undo()

        # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[6][-1].update(
        #     str(self.spins_for_red - (self.spin - self.last_made_bet)))

        if (self.spin - self.last_made_bet) % self.spins_for_red == 0:
            with Iframe(self.driver):
                # chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
                # self.driver.execute_script('arguments[0].click();', self.chips[0])  #
                self.chips[0].click()

                self.last_made_bet = self.spin
                # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[6][-1].update(
                #     str(self.spins_for_red - (self.spin - self.last_made_bet)))

                self.bet_spots['red'].click()
                if not self.play_real:
                    undo_button = self.driver.find_element_by_css_selector('[data-role="undo-button"]')
                    undo_button.click()

        recommended_numbers = self.calculator.get_recommended_values()
        self.prev_prediction = set(recommended_numbers)

        # max_ = self.calculator.get_field_value('Max')
        # balance = self.calculator.get_field_value('Суммарный баланс')
        # if self.rule_break == RULE_BREAKS[0]:
        #     if max_ - balance >= self.rule_break_value:
        #         if number not in self.prev_prediction:
        #             self.turn_on = False
        if self.rule_break == RULE_BREAKS[1]:
            if self.num_of_fails >= self.rule_break_value:
                self.turn_on = False
        # else:  # self.rule_break == 'Нет'
        #     pass
        # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[5][-1].update(str(max_ - balance))
        if not self.turn_on:
            # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[0][-1].update('НЕТ')
            # gui_window.Element(key=f'-TABLE{tab_num}-').Rows[0][-1].update(text_color='darkred')
            # if not self.num_of_repetitions:
            #     gui_window.Element(key=f'-TABLE{tab_num}-').Rows[1][-1].update('ДА')
            #     gui_window.Element(key=f'-TABLE{tab_num}-').Rows[1][-1].update(text_color='darkgreen')
            return

        if not run:
            return

        bet = self.calculator.get_field_value('Ставка') or 1
        if tab_num == 1 and self.chip_num == 0:
            bet *= 2

        with Iframe(self.driver):
            print(f'recommended_numbers: {recommended_numbers}')

            # SET CHIPS
            # chips = self.driver.find_elements_by_css_selector(self.credentials['radial_chips'])
            self.chips[self.chip_num].click()
            # self.driver.execute_script('arguments[0].click();', self.chips[self.chip_num])  #

            if recommended_numbers:
                self.last_made_bet = self.spin

            for recommended_number in recommended_numbers:
                self.bet_spots[str(recommended_number)].click()

            num_of_doubles = int(floor(log(bet, 2)))
            if num_of_doubles:
                self.driver.wait_until('[data-role="double-button"]')
            for _ in range(num_of_doubles):
                self.driver.find_element_by_css_selector('[data-role="double-button"]').click()
            for _ in range(bet - 2 ** num_of_doubles):
                inner_bet_spots = self.driver.driver.find_elements_by_xpath(
                    "//*[contains(@class,'slingshot-wrapper') or contains(@class,'classicStandard-wrapper')]//*[@data-value != '0']//*[contains(@class,'text-background')]"
                )
                for inner_bet_spot in inner_bet_spots:
                    inner_bet_spot.click()

            if not self.play_real:
                undo_button = self.driver.find_element_by_css_selector('[data-role="undo-button"]')
                for _ in range(len(recommended_numbers) * bet):
                    undo_button.click()

    # def __del__(self):
    #     self.driver.driver.quit()
    #     self.calculator.app.kill()


class Browser:
    def __init__(self, site=SITES[0], driver=None, **kwargs):  # gui_window,
        assert site in SITES, "site should be either of " + str(SITES)
        self.credentials = CREDENTIALS[site]
        # self.gui_window = gui_window

        if driver is None:
            self.driver = Driver(**kwargs)
        else:
            self.driver = driver
        self.login()
        self.num_of_tables = kwargs.get('num_of_tables')
        self.is_max_balance = kwargs.get('is_max_balance')
        self.max_balance = kwargs.get('max_balance')
        self.is_min_balance = kwargs.get('is_min_balance')
        self.min_balance = kwargs.get('min_balance')
        self.tabs = self._get_tabs(**kwargs)
        self.run_roulettes()

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
                self.sleep(5)
                table.click()
                with Iframe(self.driver):
                    self.driver.wait_until(self.credentials['live_roulette_tables'])
                    self.sleep(0.5)
                    inner_tables = self.driver.find_elements_by_css_selector(
                        self.credentials['live_roulette_tables'])
                    inner_tables_titles = [inner_table.text for inner_table in inner_tables]
                for inner_i, inner_table in enumerate(inner_tables):
                    if self.num_of_tables:
                        if inner_tables_titles[inner_i] not in ['Auto-Roulette', 'Auto-Roulette VIP',
                                                                'Auto-Roulette La Partage']:
                            continue
                        self.num_of_tables -= 1
                    else:
                        continue

                    self.driver.execute_script(f"window.open('{self.credentials['site']}', '{j}');")
                    self.driver.driver.switch_to.window(f'{j}')
                    self.sleep(0.5)
                    self.driver.wait_until(self.credentials['tables'])

                    tables_inner = self.driver.find_elements_by_css_selector(self.credentials['tables'])
                    self.driver.execute_script("arguments[0].scrollIntoView();", tables_inner[0])
                    self.sleep(1)

                    table_names_inner = self.driver.find_elements_by_css_selector(self.credentials['table_names'])
                    table_names_inner = [table_name.text.strip().lower() for table_name in table_names_inner]
                    tables_inner[table_names_inner.index(self.credentials['live_roulette_lobby'])].click()

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
            else:
                continue
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
        self.driver.driver.switch_to.window(self.tabs[0].window_name)
        start_balance = self.tabs[0].get_current_balance()
        max_balance = start_balance
        # self.gui_window.Element(key='-VARS-').Rows[0][-1].update(str(start_balance))
        # self.gui_window.Element(key='-VARS-').Rows[2][-1].update(str(max_balance))
        run = True
        while True:
            for i, tab in enumerate(self.tabs):
                current_balance = tab.get_current_balance()
                if current_balance > max_balance:
                    max_balance = current_balance
                #     self.gui_window.Element(key='-VARS-').Rows[2][-1].update(str(max_balance))
                # self.gui_window.Element(key='-VARS-').Rows[1][-1].update(str(current_balance))
                if self.is_max_balance and current_balance - start_balance >= self.max_balance or \
                        self.is_min_balance and current_balance - max_balance <= -self.min_balance:
                    # self.gui_window.Element(key=f'-TABLE{i + 1}-').Rows[1][-1].update('ДА')
                    # self.gui_window.Element(key=f'-TABLE{i + 1}-').Rows[1][-1].update(text_color='darkgreen')
                    run = False
                # time.sleep(0.1)  # ?
                # print(tab.num_of_fails, tab.prev_prediction, tab.turn_on)
                tab.make_bets(run, i + 1)  # self.gui_window,


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
