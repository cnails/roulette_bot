import PySimpleGUI as sg

from browser import Browser

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
              [sg.Text('Правило останова'),
               sg.InputOptionMenu(
                   ('Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний'),
                   key='rule_break'
               ),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=10, key='rule_break_value')],
              [sg.Text()],
              [sg.Text('○ Настройки winnings-а', background_color='black', text_color='white')],
              *[[sg.Text(name),
                 sg.Spin(values=[i for i in range(0, 100000)], initial_value=default_value, key=name)]
                for name, default_value in zip(FIELDS, DEFAULTS)],
              [sg.Text('Методика'),
               sg.InputOptionMenu((
                   'Игра с выборкой', 'Игра без выборки', 'Система PEER', 'Игра на сикслайны',
                   'Выжидание', 'Сектора', 'Epocal Storm Dinamic', 'Любимые номера',
                   'Система анти review', 'Использовать собственную систему',
                   'Без ставок, только ввести статистику'
               ), key='Методика')],
              [sg.Text()],
              [sg.Button(LAUNCH), sg.Button(EXIT)]]

    # Create the Window
    window = sg.Window("Игрок в рулетки", layout)
    # Event Loop to process "events" and get the "values" of the inputs

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
            browser = Browser(**values)
            browser.run_roulettes()

    window.close()


def main():
    run_interface()


if __name__ == '__main__':
    main()
