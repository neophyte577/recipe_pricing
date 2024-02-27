from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon, QValidator, QDoubleValidator
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QDialog, QLabel, QCompleter, QComboBox, QLineEdit, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QSizePolicy, QScrollArea, QDialogButtonBox)
from string import capwords
import os
import numpy as np
import pandas as pd
import cost

DEFAULT_WEIGHT = 'oz'
DEFAULT_VOLUME = 'floz'
DEFAULT_COUNT = 'ea'

class InputValidator(QValidator):

    def __init__(self, stuff):

        super().__init__()
        self.stuff = [thing.lower() for thing in stuff]

    def validate(self, inputText, _):

        if inputText.lower() in self.stuff:
            return QValidator.Acceptable
        
        length = len(inputText)

        for thing in self.stuff:
            if thing[:length] == inputText.lower():
                return QValidator.Intermediate
            
        return QValidator.Invalid

class SuccessDialog(QDialog):

    def __init__(self, message='', parent=None):

        super().__init__(parent)

        self.setWindowTitle('You did it!')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/tick.png')))

        self.button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button.button(QDialogButtonBox.Ok).setText('Cool')
        self.button.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        if message == '':
            self.message = QLabel('Great success!')
        else:
            self.message = message
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

class InputErrorDialog(QDialog):

    def __init__(self, message, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Ruh Roh!')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/dummy.png')))

        self.button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button.button(QDialogButtonBox.Ok).setText('Mmk')
        self.button.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.message = QLabel(message)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)


class IngredientNameField(QComboBox):

    def __init__(self, parent=None, index=0):

        super().__init__(parent)

        self.parent_window = parent
        self.index = index

        ingredient_names = cost.ingr_dict.keys()
        self.addItems(sorted(ingredient_names))
        self.setEditable(True)
        self.setCompleter(QCompleter(ingredient_names))
        self.setValidator(InputValidator(ingredient_names))
        self.setCurrentIndex(-1)
        self.currentIndexChanged.connect(self.update_unit_field)

    def get_units(self, input):

        units = []

        if input in cost.ingr_dict.keys():

            ingredient = cost.ingr_dict[input]
            
            try:
                self.parent_window.unit_layout.itemAt(self.index).widget().clear()
            except AttributeError:
                pass
            
            if ingredient.density != np.pi:
                if ingredient.each_list != []:
                    units = cost.unit_list
                    return units
                else:
                    units = list(cost.weight_dict.keys()) + list(cost.vol_dict.keys())
                    return units
            else:
                if cost.ingr_dict[self.currentText()].unit in cost.weight_dict.keys():
                    units = list(cost.weight_dict.keys())
                    if ingredient.each_list != []:
                        units += list(cost.count_dict.keys())
                    return units
                elif cost.ingr_dict[self.currentText()].unit in cost.vol_dict.keys():
                    units = list(cost.vol_dict.keys())
                    if ingredient.each_list != []:
                        units += list(cost.count_dict.keys())
                    return units
                elif cost.ingr_dict[self.currentText()].unit in cost.count_dict.keys():
                    units = list(cost.count_dict.keys())
                    return units
                else:
                    print()
                    print('tf')
                    print()
        
        else:
            print(input)

    def update_unit_field(self):

        self.units = self.get_units(self.currentText().strip().lower())
        try:
            unit_field = self.parent_window.unit_layout.itemAt(self.index).widget()
            unit_field.addItems(self.units)
            unit_field.setEditable(True)
            unit_field.setCompleter(QCompleter(self.units))
            unit_field.setValidator(InputValidator(self.units))
            unit_field.setCurrentIndex(-1)
        except AttributeError:
            pass

class RecipeField(QComboBox):

    def __init__(self, parent=None, index=0):

        super().__init__(parent)

        self.parent_window = parent
        self.index = index

        recipes = list(cost.rec_dict.keys())
        self.addItems(sorted(recipes))
        self.setEditable(True)
        self.setCompleter(QCompleter(recipes))
        self.setValidator(InputValidator(recipes))
        self.setCurrentIndex(-1)
        self.currentIndexChanged.connect(self.update_unit_field)

    def get_yield_units(self, input):

        if input in cost.rec_dict.keys():

            recipe = cost.rec_dict[input]

            try:
                self.parent_window.unit_layout.itemAt(self.index).widget().clear()
            except AttributeError:
                pass

            return list(recipe.makes.keys())
        
        else:
            print(input)

    def update_unit_field(self):

        self.yield_units = self.get_yield_units(self.currentText().strip().lower())
        try:
            unit_field = self.parent_window.unit_layout.itemAt(self.index).widget()
            unit_field.addItems(self.yield_units)
            unit_field.setEditable(True)
            unit_field.setCompleter(QCompleter(self.yield_units))
            unit_field.setValidator(InputValidator(self.yield_units))
            unit_field.setCurrentIndex(-1)
        except AttributeError:
            pass

class UnitField(QComboBox):

    def __init__(self, units, index=0):

        super().__init__()

        self.index = index

        self.addItems(units)
        self.setEditable(True)
        self.setCompleter(QCompleter(units))
        self.setValidator(InputValidator(units))
        self.setCurrentIndex(-1) 

class FloatField(QLineEdit):

    def __init__(self):

        super().__init__()

        self.setValidator(QDoubleValidator())

class AddOrderWindow(QMainWindow):

    def __init__(self):

        self.select_units_window = None

        super().__init__()

        self.setWindowTitle('Shopping List Generator')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/notebook--pencil.png')))
        
        orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

        self.order_list = []

        for file in os.listdir(orders_directory):
            filename = os.fsdecode(file)
            if filename.endswith('csv'):
                order_name = filename.replace('.csv','')
                self.order_list.append(order_name)

        # Fileame Input Area

        self.filename_header = QLabel('Order Name')
        self.filename_field = QLineEdit()
        self.filename_field.setFixedWidth(250)

        self.filename_input_area = QWidget()
        filename_layout = QVBoxLayout()
        filename_layout.addWidget(self.filename_header)
        filename_layout.addWidget(self.filename_field)
        self.filename_input_area.setLayout(filename_layout)

        # Recipe Input Area

        self.recipe_column = QWidget()
        self.recipe_layout = QVBoxLayout()
        self.recipe_layout.addWidget(QLabel('Recipe'))
        for k in range(1,11):
            self.recipe_layout.addWidget(RecipeField(parent=self, index=k))
        self.recipe_column.setLayout(self.recipe_layout)
        self.ingredient_index = 11

        self.qty_column = QWidget()
        self.qty_layout = QVBoxLayout()
        self.qty_layout.addWidget(QLabel('Quantity'))
        for k in range(10):
            self.qty_layout.addWidget(FloatField())
        self.qty_column.setLayout(self.qty_layout)

        self.unit_column = QWidget()
        self.unit_layout = QVBoxLayout()
        self.unit_layout.addWidget(QLabel('Yield Unit'))
        for k in range(10):
            self.unit_layout.addWidget(UnitField([]))
        self.unit_column.setLayout(self.unit_layout)

        self.input_fields_container_widget = QWidget()
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.recipe_column)
        self.input_layout.addWidget(self.qty_column)
        self.input_layout.addWidget(self.unit_column)
        self.input_fields_container_widget.setLayout(self.input_layout)

        self.recipe_scroll_area = QScrollArea()
        self.recipe_scroll_area.setWidget(self.input_fields_container_widget)
        self.recipe_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.recipe_scroll_area.setWidgetResizable(True)

        self.add_input_row_button = QPushButton('Add Another Recipe')
        self.add_input_row_button.setIcon(QIcon(cost.resolve_path('dep/Icons/plus-button.png')))
        self.add_input_row_button.setFixedWidth(160)
        self.add_input_row_button.clicked.connect(self.add_input_row)

        self.input_area = QWidget()
        self.input_layout = QVBoxLayout()
        self.input_layout.addWidget(self.recipe_scroll_area)
        self.input_layout.addWidget(self.add_input_row_button)
        self.input_area.setLayout(self.input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.save_order_button = QPushButton('Save Order')
        self.save_order_button.clicked.connect(self.save_order)

        self.select_units_button = QPushButton('Save and Generate List')
        self.select_units_button.clicked.connect(self.generate_unit_selection_window)

        self.close_button = QPushButton('Bye Felicia')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.select_units_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.input_area)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_input_row(self):

        self.recipe_layout.addWidget(RecipeField(parent=self, index=self.ingredient_index))
        self.ingredient_index += 1
        self.qty_layout.addWidget(FloatField())
        self.unit_layout.addWidget(UnitField([]))

    def order_df_constructor(self):

        order_df = pd.DataFrame()

        columns = []

        input_layouts = [self.recipe_layout, self.qty_layout, self.unit_layout]

        for layout in input_layouts:
            input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
            col = []
            for field in input_fields:
                if isinstance(field.widget(), QLineEdit):
                    if field.widget().text().strip() != '':
                        col.append(field.widget().text())
                    else:
                        col.append(np.nan)
                elif isinstance(field.widget(), QComboBox):
                    if field.widget().currentText().strip() != '':
                        col.append(field.widget().currentText())
                    else:
                        col.append(np.nan)
            columns.append(col)

        headers = ['rec','qty','unit']
        
        for index, col in enumerate(columns):

            order_df.insert(index, headers[index], col)

        order_df.dropna(how='all', inplace=True)

        order_df.reset_index(drop=True, inplace=True)

        print(order_df.head())

        if order_df.isnull().values.all():

            self.empty_recipe_dialog = InputErrorDialog('WRONG! Empty of input.')
            self.empty_recipe_dialog.exec()
            return
    
        elif order_df.isnull().values.any():

            self.missing_ingr_input_dialog = InputErrorDialog('WRONG! Missing input(s).')
            self.missing_ingr_input_dialog.exec()
            return
        
        else:
        
            return order_df
        
    def shopping_list_constructor(self, order_df):

        shopping_list_dict = {}

        for k, row in order_df.iterrows():

            recipe = cost.rec_dict[row['rec']]

            qty_dict = recipe.qty_dict_constructor()

            for ingredient in qty_dict:

                if ingredient not in shopping_list_dict:

                    shopping_list_dict[ingredient] = qty_dict[ingredient]
                
                else:

                    shopping_list_dict[ingredient][0] += qty_dict[ingredient][0]

        shopping_list_df = pd.DataFrame(columns=['ingr','qty','unit'])

        for ingr in shopping_list_dict:

            base_unit = cost.get_base_unit(ingr.unit)

            if base_unit == 'g':
                unit = DEFAULT_WEIGHT
            elif base_unit == 'c':
                unit = DEFAULT_VOLUME
            elif base_unit == 'ea': 
                unit = DEFAULT_COUNT

            qty = cost.unit_converter(shopping_list_dict[ingr][0], shopping_list_dict[ingr][1], unit, ingr.name)

            shopping_list_df.loc[len(shopping_list_df.index)] = [ingr.name, qty, unit]

        return shopping_list_df

    def save_order(self):

        order_df = self.order_df_constructor()

        order_name = self.filename_field.text().strip().lower()

        if order_name == '':

            InputErrorDialog('WRONG! Needs a name.')
            return

        elif order_name in self.order_list:

            InputErrorDialog('WRONG! The recipe name ' + self.filename_field.text() + ' is taken Try another.')
            return
        
        else:

            order_df.to_csv(cost.resolve_path('dep/Recipes') + '/' + order_name + '.csv', mode='w', index=False)

            for layout in [self.recipe_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            self.success_dialog = SuccessDialog()
            self.success_dialog.exec()

            return

    def generate_unit_selection_window(self, order_df):

        shopping_list_df = self.shopping_list_constructor(order_df)

        self.select_units_window = SelectUnitsWindow(shopping_list_df, parent=self)
        self.select_units_window.show()

    def close_window(self):

        self.close()

    def closeEvent(self, event):

        if self.select_units_window:
            self.select_units_window.close()

class SelectUnitsWindow(QMainWindow):

    def __init__(self, shopping_list_df, parent=None):

        super().__init__()

        self.setWindowTitle('Select Ingredient Units')
        self.setWindowIcon(QIcon('dep/Icons/weight.png'))

        self.parent_window = parent
        self.shopping_list_df = shopping_list_df

        # Fileame Input Area

        self.filename_header = QLabel('List Name')
        self.filename_field = QLineEdit()
        self.filename_field.setFixedWidth(250)

        self.filename_input_area = QWidget()
        filename_layout = QVBoxLayout()
        filename_layout.addWidget(self.filename_header)
        filename_layout.addWidget(self.filename_field)
        self.filename_input_area.setLayout(filename_layout)

        # Ingredient Edit Area

        self.ingr_name_column = QWidget()
        self.ingr_name_layout = QVBoxLayout()
        self.ingr_name_layout.addWidget(QLabel('Ingredient'))
        for k in range(1,len(self.shopping_list_df['ingr']) + 1):
            self.ingr_name_layout.addWidget(IngredientNameField(parent=self, index=k))
        ingr_name_fields = (self.ingr_name_layout.itemAt(index) for index in range(1,self.ingr_name_layout.count())) 
        for index, field in enumerate(ingr_name_fields):
            field.widget().setCurrentIndex(list(sorted(cost.ingr_dict.keys())).index(self.shopping_list_df['ingr'][index]))
            field.widget().setEnabled(False)
        if len(self.shopping_list_df['ingr']) < 10:
            for k in range(10-len(self.shopping_list_df['ingr'])):
                invisible_field = QComboBox()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.ingr_name_layout.addWidget(invisible_field)
                invisible_field.hide()   
        self.ingr_name_column.setLayout(self.ingr_name_layout)

        self.qty_column = QWidget()
        self.qty_layout = QVBoxLayout()
        self.qty_layout.addWidget(QLabel('Quantity'))
        for k in range(len(self.shopping_list_df['qty'])):
            self.qty_layout.addWidget(FloatField())
        qty_fields = (self.qty_layout.itemAt(index) for index in range(1,self.qty_layout.count())) 
        for index, field in enumerate(qty_fields):
            field.widget().setText(str(self.shopping_list_df['qty'][index]))
        if len(self.shopping_list_df['qty']) < 10:
            for k in range(10-len(self.shopping_list_df['qty'])):
                invisible_field = FloatField()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.qty_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.qty_column.setLayout(self.qty_layout)

        self.unit_column = QWidget()
        self.unit_layout = QVBoxLayout()
        self.unit_layout.addWidget(QLabel('Unit'))
        for k in range(len(self.shopping_list_df['unit'])):
            self.unit_layout.addWidget(UnitField(sorted(cost.unit_list)))
        unit_fields = (self.unit_layout.itemAt(index) for index in range(1,self.unit_layout.count())) 
        for index, field in enumerate(unit_fields, start=1):
            ingredient_input = self.ingr_name_layout.itemAt(index).widget().currentText()
            unit_list = self.ingr_name_layout.itemAt(index).widget().get_units(ingredient_input)
            field.widget().clear()
            field.widget().addItems(sorted(unit_list))
            field.widget().setCompleter(QCompleter(unit_list))
            field.widget().setValidator(InputValidator(unit_list))
            field.widget().setCurrentIndex(sorted(unit_list).index(self.shopping_list_df['unit'][index-1]))
        if len(self.shopping_list_df['unit']) < 10:
            for k in range(10-len(self.shopping_list_df['unit'])):
                invisible_field = UnitField(sorted(cost.unit_list))
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.unit_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.unit_column.setLayout(self.unit_layout)   

        self.ingr_input_fields_container_widget = QWidget()
        ingredient_input_layout = QHBoxLayout()
        ingredient_input_layout.addWidget(self.ingr_name_column)
        ingredient_input_layout.addWidget(self.qty_column)
        ingredient_input_layout.addWidget(self.unit_column)
        self.ingr_input_fields_container_widget.setLayout(ingredient_input_layout)

        self.ingredient_scroll_area = QScrollArea()
        self.ingredient_scroll_area.setWidget(self.ingr_input_fields_container_widget)
        self.ingredient_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ingredient_scroll_area.setWidgetResizable(True)

        self.add_ingr_row_button = QPushButton('Add Another Ingredient')
        self.add_ingr_row_button.setIcon(QIcon(cost.resolve_path('dep/Icons/plus-button.png')))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_ingredient_input_row)
        self.ingredient_insertion_index = len(self.shopping_list_df['ingr']) + 1

        self.ingredient_input_area = QWidget()
        ingredient_input_layout = QVBoxLayout()
        ingredient_input_layout.addWidget(self.ingredient_scroll_area)
        ingredient_input_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_area.setLayout(ingredient_input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.generate_shopping_list_button = QPushButton('Generate Shopping List')
        self.generate_shopping_list_button.clicked.connect(self.generate_shopping_list)

        self.close_button = QPushButton('Sike')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.save_order_button)
        main_button_layout.addWidget(self.generate_shopping_list_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.filename_input_area)
        central_layout.addWidget(self.ingredient_input_area)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_ingredient_input_row(self):

        if self.ingredient_insertion_index < 10:
            self.ingr_name_layout.insertWidget(self.ingredient_insertion_index, IngredientNameField(parent=self, index=self.ingredient_insertion_index))
            self.qty_layout.insertWidget(self.ingredient_insertion_index, FloatField())
            self.unit_layout.insertWidget(self.ingredient_insertion_index, UnitField([]))
            self.ingr_name_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.qty_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.unit_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.ingredient_insertion_index += 1
        else:
            self.ingr_name_layout.insertWidget(self.ingredient_insertion_index, IngredientNameField(parent=self, index=self.ingredient_insertion_index))
            self.qty_layout.insertWidget(self.ingredient_insertion_index, FloatField())
            self.unit_layout.insertWidget(self.ingredient_insertion_index, UnitField([]))
            self.ingredient_insertion_index += 1

    def generate_shopping_list(self):

        pass

    def close_window(self):

        self.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.add_order_window, self.edit_orders_window, self.output_window = None, None, None

        self.setWindowTitle('Orders')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/service-bell.png')))
        self.setFixedWidth(300)

        orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

        self.order_list = []

        for file in os.listdir(orders_directory):
            filename = os.fsdecode(file)
            if filename.endswith('csv'):
                order_name = filename.replace('.csv','')
                self.order_list.append(order_name)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()
        
        self.order_selector = QComboBox()
        self.order_selector.addItems(sorted(self.order_list))
        self.order_selector.setEditable(True)
        self.order_selector.setCompleter(QCompleter(self.order_list))
        self.order_selector.setValidator(InputValidator(self.order_list))
        self.order_selector.setCurrentIndex(-1)

        self.open_order_button = QPushButton('Open Order')
        self.open_order_button.clicked.connect(self.generate_edit_order_window)

        self.add_recipe_button = QPushButton('Create Order')
        self.add_recipe_button.clicked.connect(self.generate_add_order_window)

        self.shopping_list_button = QPushButton('Shopping Lists')
        self.shopping_list_button.clicked.connect(self.generate_shopping_list_window)

        vlayout.addWidget(self.order_selector)
        vlayout.addWidget(self.open_order_button)
        vlayout.addWidget(self.add_recipe_button)
        vlayout.addWidget(self.shopping_list_button)

        icon = QLabel()
        icon.setPixmap(QPixmap(cost.resolve_path('dep/Icons/service_bell_icon.png')))
               
        container_widget = QWidget()
        container_widget.setLayout(vlayout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    def generate_add_order_window(self):

        cost.main()
        self.add_order_window = AddOrderWindow()
        self.add_order_window.show()

    def generate_edit_order_window(self):
        
        order_name = self.order_selector.currentText()
        if order_name in self.order_list:
            cost.main()
            self.edit_orders_window = EditOrderWindow(order_name)
            self.edit_orders_window.show()        

    def generate_shopping_list_window(self):

        cost.main()
        self.shopping_list_window = ShoppingListWindow()
        self.shopping_list_window.show()

    def closeEvent(self, event):

        for w in [self.add_order_window, self.edit_orders_window, self.shopping_list_window]:
            if w:
                w.close()


class EditOrderWindow(QMainWindow):

    def __init__(self, order_name):

        super().__init__()

        order_df = pd.read_csv(cost.resolve_path('dep/Orders') + '/' + order_name)


class ShoppingListWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Shopping List')
        self.setWindowIcon(QIcon('dep/Icons/notebook--pencil.png'))

        shopping_list_path = cost.resolve_path('dep/ShoppingLists')

        self.shopping_list_selector = QComboBox()
        self.shopping_list_selector

def main():

    cost.main()

    app = QApplication()

    window = NavigationWindow()
    window.show()

    app.exec()

if __name__ == '__main__':

    main()

