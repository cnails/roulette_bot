# SECRET CONSTANTS

PROXY = 'https://sansay:rfgrfgerf@179.61.188.91:45785/'

CREDENTIALS = {
    'pinnacle': {
        'site': 'https://www1.pinnacle.com/ru/casino/games/live/roulette',
        'login': 'https://www.pinnacle.com/ru/account/login/?appId=casino&returnPath=%2fru%2fcasino%2fgames%2flive%2froulette',
        'login_check': '.account-menu-container',
        'email': 'happypuffin7@gmail.com',
        'user': 'dr770149',
        # 'EG1245397'
        'password': 'Balbes!9896',  # '19821305aA'
        'current_balance': '[data-role="balance-label__value"]',
        'video_quality': '[data-role="select-option"]',
        'cross': '[data-role="cross"]',
        'first_stripe': '[data-role="first-stripe"]',
        'second_stripe': '[data-role="second-stripe"]',
        # {
        #     'american roulette': '[data-role="balance-label__value"]',
        #     'roulette russian': '[data-e2e="balance-value"]',
        # },
        'total_bet': '[data-role="total-bet-label__value"]',
        # {
        #     'american roulette': '[data-role="total-bet-label__value"]',
        #     'roulette russian': '[data-e2e="total-bet-amount"]',
        # },
        'recent_number': '[data-role="recent-number"] span',
        # {
        #     'american roulette': '[data-role="recent-number"] span',
        #     'roulette russian': '[data-name="previous-spins-stack"] div',
        # },
        'login_button': '.pull-right .button[id="loginButton"]',
        'manual_login': True,
        'tables': '.filtered-content a',
        'table_names': '.filtered-content a .name',
        'bet_spot': 'data-bet-spot-id',
        'live_roulette_lobby': 'live roulette lobby',
        'live_roulette_tables': 'div[data-role="table-name"]',
        'status_text': 'div[data-role="status-text"]',
        'radial_chips': '[class^="chips"] li[class^="chip"]',
    },
    'williamhill': {
        'site': 'https://livecasino.williamhill.com/en-gb/',
        'user': 'betviktor',  # 'chingizps'
        'password': '19821305aA',
        'current_balance': 'whgg-account-button__balance',
        'total_bet': '',
        'recent_number': '[data-role="recent-number"] span',
        'login_button': 'button.action-login__button',
        'manual_login': False,
        'tables': '',
        'table_names': '',
        'bet_spot': '',
        'live_roulette_lobby': '',
        'live_roulette_tables': '',
        'status_text': '',
        'radial_chips': '',
    }
}
