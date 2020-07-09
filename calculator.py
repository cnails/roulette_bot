import os
import time

from pywinauto.application import Application

PATH_TO_EXE = os.path.join("lazy-z.com", "winnings", "winnings.exe")
BUTTON = 'TBitBtn'
EDIT = 'TMemo'
INPUT_FIELDS = ['Max', 'Min', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']


class Calculator:
    def __init__(self, path=PATH_TO_EXE):
        self.app = Application().start(path)
        self.path = path
        self.window = self.app.window(title="WINNINGS - 8")
        self.children = self.window.children()
        self.name_to_index, self.fell_dict, self.recommended_dict = self.parse_children()
        # self.max_minus = -150

    def parse_children(self):
        name_to_index = {}
        fell_dict = {}
        recommended_dict = {}

        names = INPUT_FIELDS[:]
        recommended = 37

        for i, child in enumerate(self.children):
            element_info = child.element_info
            name = element_info.name
            class_name = element_info.class_name
            if class_name == BUTTON:
                try:
                    fell_dict[int(name)] = i
                    continue
                except ValueError:
                    pass
                if name.strip() == 'Отменить спин':
                    name_to_index['Отменить спин'] = i
                if name == '' and recommended > 0:
                    recommended_dict[recommended] = i
                    recommended -= 1
            elif class_name == EDIT:
                if names and ((not name) or (name == '0')) and child.is_visible():
                    name = names.pop(0)
                    name_to_index[name] = i
        recommended_dict[0] = recommended_dict[37]
        del recommended_dict[37]
        return name_to_index, fell_dict, recommended_dict

    def set_number(self, num):
        assert 0 <= num <= 36
        self.children[self.fell_dict[num]].click()

    def insert_number(self, field, num):
        """
        field: one of ['Min', 'Max', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']
        """
        assert field in INPUT_FIELDS, "should be one of " + INPUT_FIELDS
        self.children[self.name_to_index[field]].set_edit_text(num)

    def focus_cell(self, num):
        self.children[num].set_focus()

    def get_field_value(self, field):
        """
        One of ['Min', 'Max', 'Стоит на поле', 'Суммарный баланс', 'Баланс в этой игре', 'Ставка']
        """
        assert field in INPUT_FIELDS, "should be one of " + INPUT_FIELDS
        return int(self.children[self.name_to_index[field]].element_info.name or 0)

    def undo_spin(self):
        self.children[self.name_to_index['Отменить спин']].click()

    def get_recommended_values(self):
        values = []
        for i in range(0, 36 + 1):
            if self.children[self.recommended_dict[i]].element_info.name:
                values.append(i)
        return values

    def __del__(self):
        self.app.kill()


def main():
    app = Calculator()
    app.set_number(5)
    app.set_number(16)
    app.set_number(0)
    app.set_number(36)
    app.undo_spin()

    time.sleep(5)
    for name in INPUT_FIELDS:
        app.insert_number(name, 150)
        print(f'{name}: {app.get_field_value(name)}')
    print(app.get_recommended_values())
    # print(app.name_to_index)
    # app.focus_cell(app.name_to_index['Min'])
    # time.sleep(2)
    # app.focus_cell(app.name_to_index['Max'])


# type_keys()


if __name__ == '__main__':
    main()
