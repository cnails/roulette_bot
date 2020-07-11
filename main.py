from abc import ABC, abstractmethod

from local_settings import CREDENTIALS
from py_files.chrome_driver import Driver

SITES = sorted(CREDENTIALS)
PINNACLE_ROULETTE_TYPE_TO_DEPTH = {
    'roulette russian': 2,
    'american roulette': None,
}


class Iframe:
    def __init__(self, driver, roulette_type):
        self.driver = driver
        self.depth = PINNACLE_ROULETTE_TYPE_TO_DEPTH[roulette_type]

    def __enter__(self):
        # ENTERING IFRAMES
        iframes = self.driver.find_elements_by_css_selector('iframe')
        i = 0
        while iframes and (self.depth is None or i < self.depth):
            self.driver.switch_to.frame(iframes[-1])
            iframes = self.driver.find_elements_by_css_selector('iframe')
            i += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.default_content()  # switch back to the main window


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


class Tab(AbstractTab):
    def __init__(self, driver, roulette_type, credentials):
        assert roulette_type in PINNACLE_ROULETTE_TYPE_TO_DEPTH, \
            "roulette_type should be either of " + str(list(SITES))
        self.driver = driver
        self.roulette_type = roulette_type
        self.credentials = credentials
        self.bet_spots = self._get_bet_spots()

    def _get_bet_spots(self):
        bet_spot_field = self.credentials["bet_spot"]
        with Iframe(self.driver.driver, self.roulette_type):
            bet_spots = self.driver.driver.find_elements_by_xpath(f'//*[@{bet_spot_field}]')
        return [bet_spot.get_attribute(bet_spot_field) for bet_spot in bet_spots]

    def get_current_balance(self):
        with Iframe(self.driver.driver, self.roulette_type):
            balance = self.driver.find_element_by_css_selector(
                self.credentials['current_balance'][self.roulette_type])
            # balance = float(balance.text)
        return balance

    def get_total_bet(self):
        with Iframe(self.driver.driver, self.roulette_type):
            balance = self.driver.find_element_by_css_selector(
                self.credentials['total_bet'][self.roulette_type])
            # balance = float(balance.text)
        return balance

    def get_recent_number(self):
        """ returns recent number """
        return self.get_recent_number()[0]

    def get_recent_numbers(self):
        """ returns recent numbers """
        with Iframe(self.driver.driver, self.roulette_type):
            numbers = self.driver.find_elements_by_css_selector(
                self.credentials['recent_number'][self.roulette_type])
        numbers = [int(number.text) for number in numbers]
        return numbers


class Browser:
    def __init__(self, site=SITES[0], **kwargs):
        assert site in SITES, "site should be either of " + str(SITES)
        self.credentials = CREDENTIALS[site]
        self.driver = Driver(**kwargs)
        self.tabs = self._get_tabs()

    def _get_tabs(self, tables=None):
        tabs = []

        if tables is None:
            tables = self.driver.find_elements_by_css_selector(self.credentials['tables'])
            table_names = self.driver.find_elements_by_css_selector(self.credentials['table_names'])
            table_names = [table_name.text for table_name in table_names]
        else:
            raise NotImplemented
        assert len(tables) == len(table_names)
        for i, table in enumerate(tables):
            self.driver.execute_script(f"window.open('{self.credentials['site']}', '{i}');")
            self.driver.switch_to_window(f'{i}')
            inner_tables = self.driver.find_elements_by_css_selector(self.credentials['tables'])
            self.driver.execute_script("arguments[0].scrollIntoView();", inner_tables[i])
            inner_tables[i].click()
            roulette_type = table_names[i].lower()
            tabs.append(Tab(self.driver, roulette_type, self.credentials))

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
        else:
            input('Please, press ENTER when logged in: ')

        self.driver.get(self.credentials['site'])
        # input("STOP: ")
        # тут явно таймслип нужен и проверка на то, что зашлось в акк

    def run_roulettes(self):
        for i, tab in enumerate(self.tabs):
            self.driver.switch_to_window(f'{i}')
            # actions here


# class Common:
#     # def play(self):
#     #     self.balance = self.get_current_balance()
#     #
#     #     numbers = self.get_recent_numbers()
#     #
#     #     [data-role="recent-number"] span
#     #     path[data-bet-spot-id="$ID"]
#     pass


def main():
    browser = Browser(site='pinnacle')
    browser.login()
    browser.run_roulettes()

    # driver.execute_async_script("""
    #
    # """)


if __name__ == "__main__":
    main()
