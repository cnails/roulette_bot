import PySimpleGUI as sg

from browser import Browser
from local_settings import PROXY

FIELDS = ['Останавливать игру при выигрыше более', 'Максимальная ставка',
          'Максимально возможный выигрыш', 'Крутизна использованной прогрессии',
          'Максимальное количество ОБРАБАТЫВАЕМЫХ чисел']
FIELDS_TO_EN = {
    'Останавливать игру при выигрыше более': 'stop_after_win',
    'Максимальная ставка': 'max_bet',
    'Максимально возможный выигрыш': 'max_possible_win',
    'Крутизна использованной прогрессии': 'steepness_of_regression',
    'Максимальное количество ОБРАБАТЫВАЕМЫХ чисел': 'max_num_of_processed_numbers',
    'Методика': 'method',
}
DEFAULTS = [5000, 20, 1000, 1, 5]
EXIT = 'Выйти'
LAUNCH = 'Запустить бота'
METHOD = 'method'


def run_interface():
    layout = [[sg.Text('○ Настройки бота', background_color='black', text_color='white')],
              [sg.Text('Сайт'), sg.InputOptionMenu(('pinnacle',), key='site')],
              [sg.Checkbox('Использовать встроенное прокси?', default=False, key='proxy')],
              [sg.Text('Количество столов'),
               sg.Spin(values=[i for i in range(1, 4)], initial_value=1, key='num_of_tables')],
              [sg.Checkbox('Играть на реальные деньги?', default=True, key='play_real')],
              [sg.Text('Количество повторных запусков бота'),
               sg.Spin(values=[i for i in range(0, 100000)], initial_value=1, key='num_of_repetitions')],
              [sg.Text('Первое правило останова'),
               sg.InputOptionMenu(
                   ('Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний', 'Нет'),
                   key='rule_break'
               ),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=50, key='rule_break_value_first')],
              [sg.Text('Последующие правила останова'),
               sg.InputOptionMenu(
                   ('Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний', 'Нет'),
                   key='rule_break_second'
               ),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=10, key='rule_break_value_second')],
              [sg.Checkbox('Строгое соблюдение правила останова?', default=False, key='rule_break_strict')],
              [sg.Text()],
              [sg.Button(LAUNCH), sg.Button(EXIT)]]

    window = sg.Window("Игрок в рулетки", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == EXIT:
            break
        elif event == LAUNCH:
            to_delete = []
            for value_key, value_value in values.items():
                if value_key in FIELDS_TO_EN:
                    to_delete.append(value_key)
            for elem in to_delete:
                values[FIELDS_TO_EN[elem]] = values[elem]
                del values[elem]
            print(f'values: {values}')
            if values['proxy']:
                values['proxy'] = PROXY
            else:
                values['proxy'] = None
            browser = Browser(**values)  # , hide=True
            browser.run_roulettes()
            break

    window.close()


def main():
    run_interface()


if __name__ == '__main__':
    main()
