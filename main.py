from py_files import chrome_driver


SITES = ['pinnacle', 'williamhill']


class Program:
    def __init__(self):
        pass

    def set_number(self, number):
        pass

    def get_move(self):
        pass


class Data:
    def __init__(self, site='pinnacle'):
        assert site in SITES, "site should be either of " + SITES
        self.site = site
        self.driver = chrome_driver.return_driver()
        self.max_minus = 150
        self.prg = Program()

    def get_current_balance(self):
        if self.site == SITES[1]:
            return self.driver.find_element_by_css_selector("whgg-account-button__balance").text()
        else:
            return self.driver.find_element_by_css_selector("whgg-account-button__balance").text()

    def get_recent_number(self):
        """ returns recent number """
        return self.driver.find_element_by_css_selector('[data-role="recent-number"] span').text()        
    
    def get_recent_numbers(self):
        """ returns recent numbers """
        return [elem.text() for elem in self.driver.find_elements_by_css_selector('[data-role="recent-number"] span')]        

    def make_move(self, numbers):
        # number - int or it can be str ?
        # static amount for move ?
        ''' request number for new move and make a move on roulette '''
        pass

    def set_number(self):
        ''' get last move number and set it in program '''
        self.prg.set_number(self.get_recent_number())

    def get_move(self):
        ''' get instruction from program and make a move '''
        numbers = self.prg.get_move()
        # здесь надо проверять какой ход был получен
        self.make_move(numbers)

    def play(self):
        self.balance = self.get_current_balance()

        # numbers = self.get_recent_numbers()

        # [data-role="recent-number"] span
        # path[data-bet-spot-id="$ID"]

    def login(self):
        chrome_driver.get(self.driver, "https://livecasino.williamhill.com/en-gb/")
        self.driver.find_element_by_css_selector("button.action-login__button").click()
        self.driver.find_element_by_css_selector('[name="username"]').send_keys("betviktor")
        self.driver.find_element_by_css_selector('[name="password"]').send_keys("19821305aA")
        self.driver.find_element_by_css_selector('[type="submit"]').click()
        # тут явно таймслип нужен и проверка на то, что зашлось в акк


def main():
    # driver.execute_script("""Object.defineProperty(navigator, 'webdriver', {
    #   get: () => undefined,
    # });""")
    # driver = chrome_driver.return_driver()
    data = Data()
    data.login()
    # driver.execute_async_script("""
        
    # """)


if __name__ == "__main__":
    main()
