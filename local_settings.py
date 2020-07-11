CREDENTIALS = {
    'pinnacle': {
        'site': 'https://www1.pinnacle.com/en/casino/games/live/roulette',
        'email': 'happypuffin7@gmail.com',
        'user': 'EG1245397',
        'password': '19821305aA',
        'current_balance': {
            'american roulette': '[data-role="balance-label__value"]',
            'roulette russian': '[data-e2e="balance-value"]',
        },
        'total_bet': {
            'american roulette': '[data-role="total-bet-label__value"]',
            'roulette russian': '[data-e2e="total-bet-amount"]',
        },
        'recent_number': {
            'american roulette': '[data-role="recent-number"] span',
            'roulette russian': '[data-name="previous-spins-stack"] div',
        },
        'login_button': '.pull-right .button[id="loginButton"]',
        'manual_login': True,
        'tables': '.filtered-content a',
        'table_names': '.filtered-content a .name',
        'bet_spot': 'data-bet-spot-id',
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
    }
}
