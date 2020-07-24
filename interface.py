import threading

import PySimpleGUI as sg

from browser import Browser

# from local_settings import PROXY

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
BREAK_RULES = ('Максимальное отклонение от значения Max', 'Максимальное количество неудачных предсказаний', 'Нет')
DEFAULTS = [5000, 20, 1000, 1, 5]
EXIT = 'Выйти'
LAUNCH = 'Запустить бота'
NUM_OF_TABLES = 'num_of_tables'
METHOD = 'method'

WINDOW_SIZE = (1280, 960)
FRAME_ROW_SIZE = (32, 1)
FRAME_ROW_TEXT_SIZE = (10, 1)
FRAME_ROW_ALIGN = 'r'
FRAME_ROW_COLOR = 'black'

CHIPS = ['0.20', '0.50', '1', '5', '25', '100']


def run_interface():
    layout = [[sg.Text('○ Настройки бота', background_color='black', text_color='white', justification='center', size=(WINDOW_SIZE[0], 1))],
              [sg.Text('Сайт'), sg.InputOptionMenu(('pinnacle',), key='site')],
              [sg.Text('Количество столов'),
               sg.Spin(values=[i for i in range(1, 4)], initial_value=1, key='num_of_tables')],
              [sg.Checkbox('Играть на реальные деньги?', default=True, key='play_real')],
              [sg.Text('Фишки на столах'), sg.InputOptionMenu(CHIPS, key='chip')],
              [sg.Text('Количество повторных запусков бота'),
               sg.Spin(values=[i for i in range(0, 100000)], initial_value=1, key='num_of_repetitions')],
              [sg.Text('Первое правило останова'),
               sg.InputOptionMenu(BREAK_RULES, key='rule_break'),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=50, key='rule_break_value_first')],
              [sg.Text('Последующие правила останова'),
               sg.InputOptionMenu(BREAK_RULES, key='rule_break_second'),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=10, key='rule_break_value_second')],
              [sg.Checkbox('Максимальное значение баланса', default=True, key='is_max_balance'),
               sg.Spin(values=[i for i in range(1, 100000)], initial_value=60, key='max_balance')],
              [sg.Text('Ставить на красное каждые N спинов'),
               sg.Spin(values=[i for i in range(1, 1000)], initial_value=30, key='spins_for_red')],
              [sg.Text('○ Столы', background_color='black', text_color='white', justification='center', size=(WINDOW_SIZE[0], 1))],
              [sg.Frame(layout=[
                  [sg.Text('Начальное значение баланса', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Нынешнее значение баланса', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Количество столов', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Играет на реальные деньги?', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Фишки на столах', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Количество повторных запусков бота', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Первое правило останова', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Последующие правила останова', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Максимальное значение баланса', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Ставить на красное каждые N спинов', size=FRAME_ROW_SIZE, justification=FRAME_ROW_ALIGN),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
              ], title='Переменные', title_color='black', relief=sg.RELIEF_SUNKEN, key='-VARS-', size=(WINDOW_SIZE[0], 200),
                  element_justification='center')],
              [*[sg.Frame(layout=[
                  [sg.Text('Бот работает?', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Бот остановился окончательно?', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Осталось повторных запусков бота', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Действующее правило останова', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Количество неудач подряд', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Отклонение от значения Max', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
                  [sg.Text('Спинов до ставки на красное', justification=FRAME_ROW_ALIGN, size=FRAME_ROW_SIZE),
                   sg.Text('', text_color=FRAME_ROW_COLOR, size=FRAME_ROW_TEXT_SIZE)],
              ], title=f'Стол {i + 1}', title_color='black', relief=sg.RELIEF_SUNKEN, key=f'-TABLE{i + 1}-')
                  for i in range(3)]  # HARDCODE
               ],
              [sg.Button(LAUNCH), sg.Button(EXIT)]]

    window = sg.Window("Игрок в рулетки", layout, size=WINDOW_SIZE)

    while True:
        event, values = window.read(timeout=1000000)
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
            values['proxy'] = None
            ### SETTING VARS
            window.Element(key='-VARS-').Rows[2][-1].update(values['num_of_tables'])
            if values['play_real']:
                window.Element(key='-VARS-').Rows[3][-1].update('ДА')
                window.Element(key='-VARS-').Rows[3][-1].update(text_color='darkgreen')
            else:
                window.Element(key='-VARS-').Rows[3][-1].update('НЕТ')
                window.Element(key='-VARS-').Rows[3][-1].update(text_color='darkred')
            window.Element(key='-VARS-').Rows[4][-1].update(values['chip'])
            window.Element(key='-VARS-').Rows[5][-1].update(str(values['num_of_repetitions']))
            window.Element(key='-VARS-').Rows[6][-1].update(f"{BREAK_RULES.index(values['rule_break']) + 1} ({values['rule_break_value_first']})")
            window.Element(key='-VARS-').Rows[7][-1].update(f"{BREAK_RULES.index(values['rule_break_second']) + 1} ({values['rule_break_value_second']})")
            if values['is_max_balance']:
                window.Element(key='-VARS-').Rows[8][-1].update(f"ДА ({values['max_balance']})")
                window.Element(key='-VARS-').Rows[8][-1].update(text_color='darkgreen')
            else:
                window.Element(key='-VARS-').Rows[8][-1].update(f"НЕТ")
                window.Element(key='-VARS-').Rows[8][-1].update(text_color='darkred')
            window.Element(key='-VARS-').Rows[9][-1].update(str(values['spins_for_red']))
            for i in range(values['num_of_tables']):
                window.Element(key=f'-TABLE{i + 1}-').Rows[0][-1].update('ДА')
                window.Element(key=f'-TABLE{i + 1}-').Rows[0][-1].update(text_color='darkgreen')
                window.Element(key=f'-TABLE{i + 1}-').Rows[1][-1].update('НЕТ')
                window.Element(key=f'-TABLE{i + 1}-').Rows[1][-1].update(text_color='darkred')
                window.Element(key=f'-TABLE{i + 1}-').Rows[2][-1].update(str(values['num_of_repetitions']))
                window.Element(key=f'-TABLE{i + 1}-').Rows[3][-1].update(f"{BREAK_RULES.index(values['rule_break']) + 1} ({values['rule_break_value_first']})")
                window.Element(key=f'-TABLE{i + 1}-').Rows[4][-1].update('0')
                window.Element(key=f'-TABLE{i + 1}-').Rows[5][-1].update('0')
                window.Element(key=f'-TABLE{i + 1}-').Rows[6][-1].update(str(values['spins_for_red']))

            threading.Thread(target=Browser, args=(window,), kwargs=values, daemon=True).start()
        elif event == NUM_OF_TABLES:
            pass

    window.close()


def main():
    run_interface()


if __name__ == '__main__':
    main()
