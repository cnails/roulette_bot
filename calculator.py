import functools
import os
import time

import win32gui, win32com.client

from pywinauto.application import Application
from pywinauto.controls.common_controls import TabControlWrapper

PATH_TO_EXE = os.path.join("lazy-z.com", "winnings", "winnings.exe")
BUTTON = 'TBitBtn'
RADIOBUTTON = 'TRadioButton'
CHECKBOX = 'TCheckBox'
EDIT = 'TMemo'
TABSHEET = 'TTabSheet'
PAGE_CONTROL = 'TPageControl'
INPUT_FIELDS = ['Max', 'Min', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']
FIELDS = ['Останавливать игру при выигрыше более', 'Максимальная ставка',
          'Максимально возможный выигрыш', 'Крутизна использованной прогрессии',
          'Максимальное количество ОБРАБАТЫВАЕМЫХ чисел']

TABLES = 0
SETTINGS = 1
METHODS = 2
NUM_OF_TABS = 4


def activate_window(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # shell = win32com.client.Dispatch("WScript.Shell")
        # shell.SendKeys('%')
        # win32gui.SetForegroundWindow(args[0].window_int)
        window = args[0].app.top_window()
        window.set_focus()
        value = func(*args, **kwargs)
        # args[0].app.top_window().minimize()
        return value

    return wrapper_decorator


def activate_tab(num):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            args[0].change_tab(num)
            value = func(*args, **kwargs)
            # args[0].app.top_window().minimize()
            return value

        return wrapper_decorator

    return decorator


class Calculator:
    def __init__(self, path=PATH_TO_EXE, **kwargs):
        self.app = Application().start(path, timeout=60)
        self.path = path
        self.window = self.app.window(title="WINNINGS - 8")
        self.window_int = win32gui.GetForegroundWindow()
        self.page_control = self.window.child_window(class_name=PAGE_CONTROL).wrapper_object()
        self.name_to_child, self.fell_dict, self.recommended_dict, self.radio_buttons, self.checkboxes = self.parse_children()
        # self._init_parameters(**kwargs)

    # @activate_window
    # def _init_parameters(self, method='Игра с выборкой', stop_after_win=5000, max_bet=20,
    #                      max_possible_win=1000, steepness_of_regression=1,
    #                      max_num_of_processed_numbers=5, **kwargs):
    #     assert method in self.radio_buttons
    #     self.change_tab(METHODS)
    #     self.radio_buttons[method].click()
    #
    #     self.change_tab(SETTINGS)
    #     for field, num in zip(
    #             FIELDS,
    #             [stop_after_win, max_bet, max_possible_win, steepness_of_regression, max_num_of_processed_numbers]):
    #         self.name_to_child[field].set_edit_text(num)

    @activate_window
    def change_tab(self, num):
        TabControlWrapper(self.page_control).select(num)

    @activate_window
    def parse_children(self):
        name_to_child, fell_dict, recommended_dict, radio_buttons, checkboxes = [{} for _ in range(5)]

        names = INPUT_FIELDS[:]
        recommended = 37

        for child in self.window.children():
            element_info = child.element_info
            name = element_info.name
            class_name = element_info.class_name
            if class_name == BUTTON:
                try:
                    fell_dict[int(name)] = child
                    continue
                except ValueError:
                    pass
                if name.strip() == 'Отменить спин':
                    name_to_child['Отменить спин'] = child
                if name == '' and recommended > 0:
                    recommended_dict[recommended] = child
                    recommended -= 1
            elif class_name == EDIT:
                if names and ((not name) or (name == '0')) and child.is_visible():
                    name = names.pop(0)
                    name_to_child[name.strip()] = child

        recommended_dict[0] = recommended_dict[37]
        del recommended_dict[37]

        for j in range(NUM_OF_TABS):
            self.change_tab(j)
            time.sleep(0.5)

        self.change_tab(METHODS)
        was_first_500 = False
        for child in self.window.children():
            element_info = child.element_info
            name = element_info.name
            class_name = element_info.class_name
            # print(f'{element_info.id}, "{name}", "{class_name}"')
            if class_name == EDIT:
                # HARDCODE
                if not was_first_500 and name in ['500', '5000']:
                    name_to_child[FIELDS[0]] = child
                    was_first_500 = True
                elif name == '20':
                    name_to_child[FIELDS[1]] = child
                elif name in ['500', '1000']:
                    name_to_child[FIELDS[2]] = child
                elif name in ['10', '1']:
                    name_to_child[FIELDS[3]] = child
                elif name in ['24', '4']:
                    name_to_child[FIELDS[4]] = child
            elif class_name == RADIOBUTTON:
                radio_buttons[name.strip()] = child
            elif class_name == CHECKBOX:
                checkboxes[name.strip()] = child

        return name_to_child, fell_dict, recommended_dict, radio_buttons, checkboxes

    @activate_window
    @activate_tab(TABLES)
    def set_number(self, num):
        assert 0 <= num <= 36
        self.fell_dict[num].click()

    @activate_window
    @activate_tab(TABLES)
    def insert_number(self, field, num):
        """
        field: one of ['Min', 'Max', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']
        """
        assert field in INPUT_FIELDS, "should be one of " + str(INPUT_FIELDS)
        self.name_to_child[field].set_edit_text(num)

    @activate_window
    def focus_cell(self, elem):
        elem.set_focus()

    @activate_window
    @activate_tab(TABLES)
    def get_field_value(self, field):
        """
        One of ['Min', 'Max', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']
        """
        assert field in INPUT_FIELDS, "should be one of " + str(INPUT_FIELDS)
        return int(self.name_to_child[field].element_info.name or 0)

    @activate_window
    @activate_tab(TABLES)
    def undo_spin(self):
        self.name_to_child['Отменить спин'].click()

    @activate_window
    @activate_tab(TABLES)
    def get_recommended_values(self):
        values = []
        for i in range(0, 36 + 1):
            if self.recommended_dict[i].element_info.name:
                values.append(i)
        return values

    # def __del__(self):
    #     self.window.close()
    #     self.app.kill()


def main():
    app = Calculator()
    app.change_tab(TABLES)
    app.set_number(5)
    app.set_number(16)
    app.set_number(0)
    app.set_number(36)
    app.undo_spin()

    time.sleep(10000)

    for name in INPUT_FIELDS:
        app.insert_number(name, 150)
    print(app.get_recommended_values())
    # print(app.name_to_child)
    # app.focus_cell(app.name_to_child['Min'])
    # time.sleep(2)
    # app.focus_cell(app.name_to_child['Max'])


# type_keys()


if __name__ == '__main__':
    main()
