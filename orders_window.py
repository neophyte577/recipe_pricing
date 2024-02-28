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

class ConfirmationDialog(QDialog):

    def __init__(self, parent=None, message='Are you sure you finna buss it?'):

        super().__init__(parent)

        self.setWindowTitle('No Cap?')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/exclamation--frame.png')))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText('frfr ong')
        self.buttons.button(QDialogButtonBox.Cancel).setText('Nah')
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.message = QLabel(message)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttons)
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

    def __init__(self, units, index=0, parent=None):

        super().__init__()

        self.index = index
        self.parent_window = parent

        if parent:

            self.ingredient = cost.ingr_dict[self.parent_window.ingr_name_layout.itemAt(self.index).widget().currentText()]
            self.qty_field = self.parent_window.qty_layout.itemAt(self.index).widget()

            unit_list = self.parent_window.ingr_name_layout.itemAt(index).widget().get_units(self.ingredient.name)
            self.addItems(sorted(unit_list))
            self.setCompleter(QCompleter(unit_list))
            self.setValidator(InputValidator(unit_list))
            self.setCurrentIndex(sorted(unit_list).index(self.parent_window.shopping_list_df['unit'][index-1]))

            try:
                self.cost = self.parent_window.cost_layout.itemAt(self.index).widget().text()
            except AttributeError:
                pass

            self.unit = self.currentText()
            self.currentTextChanged.connect(self.update_associated_qty)

        else:

            self.addItems(units)
            self.setEditable(True)
            self.setCompleter(QCompleter(units))
            self.setValidator(InputValidator(units))
            self.setCurrentIndex(-1) 

    def update_associated_qty(self):

        if self.currentText() in cost.unit_list:

            new_unit = self.currentText()

            old_qty = float(self.qty_field.text())

            new_qty = cost.unit_converter(old_qty, self.unit, new_unit)

            self.qty_field.setText(str(new_qty))

            self.unit = new_unit
        

class FloatField(QLineEdit):

    def __init__(self, initial_value=None, index=None, parent=None):

        super().__init__()

        self.setValidator(QDoubleValidator())

class AddOrderWindow(QMainWindow):

    def __init__(self, parent):

        self.select_units_window = None

        super().__init__()

        self.setWindowTitle('Create Order')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/service-bell--plus.png')))
        
        self.parent_window = parent

        self.orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

        self.order_list = []

        for file in os.listdir(self.orders_directory):
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
        self.insertion_index = 11

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

        self.select_units_button = QPushButton('Generate Shopping List')
        self.select_units_button.clicked.connect(self.generate_unit_selection_window)

        self.close_button = QPushButton('Bye Felicia')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.save_order_button)
        main_button_layout.addWidget(self.select_units_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.filename_input_area)
        central_layout.addWidget(self.input_area)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_input_row(self):

        self.recipe_layout.addWidget(RecipeField(parent=self, index=self.insertion_index))
        self.insertion_index += 1
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

        if order_df.isnull().values.all():

            InputErrorDialog('WRONG! Empty of input.').exec()
            return
    
        elif order_df.isnull().values.any():

            InputErrorDialog('WRONG! Missing input(s).').exec()
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

        shopping_list_df.dropna(how='all', inplace=True)

        shopping_list_df = shopping_list_df.astype({'qty':'float64'})

        shopping_list_df['qty'] = shopping_list_df['qty'].round(3)

        shopping_list_df['cost'] = pd.Series()

        for k, row in shopping_list_df.iterrows():

            ingredient = cost.ingr_dict[row['ingr']]

            shopping_list_df['cost'][k] = round(ingredient.cost(qty=row['qty'], target_unit=row['unit'])[0], 2)

        print('in slc:', shopping_list_df.head())

        return shopping_list_df

    def save_order(self):

        order_df = self.order_df_constructor()

        order_name = self.filename_field.text().strip().lower()

        if order_name == '':
            
            InputErrorDialog('WRONG! Needs a name.').exec()
            return

        elif order_name in self.order_list:

            InputErrorDialog('WRONG! The recipe name ' + self.filename_field.text() + ' is taken Try another.').exec()
            return
        
        else:

            order_df.to_csv(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv', mode='w', index=False)

            for layout in [self.recipe_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            self.order_list = []

            for file in os.listdir(self.orders_directory):
                filename = os.fsdecode(file)
                if filename.endswith('csv'):
                    order_name = filename.replace('.csv','')
                    self.order_list.append(order_name)

            self.parent_window.order_selector.clear()
            self.parent_window.order_selector.addItems(sorted(self.order_list))
            self.parent_window.order_selector.setEditable(True)
            self.parent_window.order_selector.setCompleter(QCompleter(self.order_list))
            self.parent_window.order_selector.setValidator(InputValidator(self.order_list))
            self.parent_window.order_selector.setCurrentIndex(-1)

            self.success_dialog = SuccessDialog()
            self.success_dialog.exec()

            return

    def generate_unit_selection_window(self, order_df):

        order_df = self.order_df_constructor()

        order_name = self.filename_field.text().strip().lower()

        if order_name == '':
            
            InputErrorDialog('WRONG! Needs a name.').exec()
            return

        elif order_name in self.order_list:

            InputErrorDialog('WRONG! The recipe name ' + self.filename_field.text() + ' is taken Try another.').exec()
            return
        
        else:

            order_df.to_csv(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv', mode='w', index=False)

            for layout in [self.recipe_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            self.order_list = []

            for file in os.listdir(self.orders_directory):
                filename = os.fsdecode(file)
                if filename.endswith('csv'):
                    order_name = filename.replace('.csv','')
                    self.order_list.append(order_name)

            self.parent_window.order_selector.clear()
            self.parent_window.order_selector.addItems(sorted(self.order_list))
            self.parent_window.order_selector.setEditable(True)
            self.parent_window.order_selector.setCompleter(QCompleter(self.order_list))
            self.parent_window.order_selector.setValidator(InputValidator(self.order_list))
            self.parent_window.order_selector.setCurrentIndex(-1)

        shopping_list_df = self.shopping_list_constructor(order_df)

        print('in gusw', shopping_list_df)

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
        for k in range(1,len(self.shopping_list_df['qty'])+1):
            self.qty_layout.addWidget(FloatField())
        qty_fields = (self.qty_layout.itemAt(index) for index in range(1,self.qty_layout.count())) 
        for index, field in enumerate(qty_fields):
            field.widget().setText(str(self.shopping_list_df['qty'][index]))
            field.widget().setEnabled(False)
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
        for k in range(1,len(self.shopping_list_df['unit'])+1):
            self.unit_layout.addWidget(UnitField(units=[], index=k, parent=self))           
        if len(self.shopping_list_df['unit']) < 10:
            for k in range(10-len(self.shopping_list_df['unit'])):
                invisible_field = UnitField([])
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.unit_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.unit_column.setLayout(self.unit_layout) 
        
        self.cost_column = QWidget()
        self.cost_layout = QVBoxLayout()
        self.cost_layout.addWidget(QLabel('Cost'))
        for k in range(1,len(self.shopping_list_df['cost'])+1):
            self.cost_layout.addWidget(FloatField())
        cost_fields = (self.cost_layout.itemAt(index) for index in range(1,self.cost_layout.count())) 
        for index, field in enumerate(cost_fields):
            field.widget().setText(str(self.shopping_list_df['cost'][index]))
            field.widget().setEnabled(False)
        if len(self.shopping_list_df['cost']) < 10:
            for k in range(10-len(self.shopping_list_df['cost'])):
                invisible_field = FloatField()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.cost_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.cost_column.setLayout(self.cost_layout)  

        self.input_fields_container_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.ingr_name_column)
        input_layout.addWidget(self.qty_column)
        input_layout.addWidget(self.unit_column)
        input_layout.addWidget(self.cost_column)
        self.input_fields_container_widget.setLayout(input_layout)

        self.input_scroll_area = QScrollArea()
        self.input_scroll_area.setWidget(self.input_fields_container_widget)
        self.input_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.input_scroll_area.setWidgetResizable(True)

        self.add_ingr_row_button = QPushButton('Add Another Ingredient')
        self.add_ingr_row_button.setIcon(QIcon(cost.resolve_path('dep/Icons/plus-button.png')))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_input_row)
        self.insertion_index = len(self.shopping_list_df['ingr']) + 1

        self.ingredient_input_area = QWidget()
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_scroll_area)
        input_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_area.setLayout(input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.save_shopping_list_button = QPushButton('Save Shopping List')
        self.save_shopping_list_button.clicked.connect(self.save_shopping_list)

        self.close_button = QPushButton('Sike')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.save_shopping_list_button)
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

    def add_input_row(self):

        if self.insertion_index < 10:
            self.ingr_name_layout.insertWidget(self.insertion_index, IngredientNameField(parent=self, index=self.insertion_index))
            self.qty_layout.insertWidget(self.insertion_index, FloatField())
            self.unit_layout.insertWidget(self.insertion_index, UnitField([]))
            self.ingr_name_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.qty_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.unit_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.insertion_index += 1
        else:
            self.ingr_name_layout.insertWidget(self.insertion_index, IngredientNameField(parent=self, index=self.insertion_index))
            self.qty_layout.insertWidget(self.insertion_index, FloatField())
            self.unit_layout.insertWidget(self.insertion_index, UnitField([]))
            self.insertion_index += 1

    def shopping_list_updator(self):

        new_list_df = pd.DataFrame()

        columns = []

        input_layouts = [self.ingr_name_layout, self.qty_layout, self.unit_layout]

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

        headers = ['ingr','qty','unit']
        
        for index, col in enumerate(columns):

            new_list_df.insert(index, headers[index], col)

        new_list_df.dropna(how='all', inplace=True)

        new_list_df['qty'] = new_list_df['qty'].astype({'qty':'float64'})

        new_list_df['qty'] = new_list_df['qty'].round(3)

        new_list_df['cost'] = pd.Series()

        for k, row in new_list_df.iterrows():

            ingredient = cost.ingr_dict[row['ingr']]

            new_list_df['cost'][k] = round(ingredient.cost(qty=row['qty'], target_unit=row['unit'])[0], 2)

        new_list_df.reset_index(drop=True, inplace=True)

        if new_list_df.isnull().values.all():

            InputErrorDialog('WRONG! Empty of input.').exec()
            return
    
        elif new_list_df.isnull().values.any():

            InputErrorDialog('WRONG! Missing input(s).').exec()
            return
        
        else:
            
            return new_list_df
        
    def save_shopping_list(self):

        new_list_df = self.shopping_list_updator()

        list_name = self.filename_field.text().strip().lower()

        shopping_lists = []

        shopping_lists_directory = os.fsencode(cost.resolve_path('dep/ShoppingLists'))

        for file in os.listdir(shopping_lists_directory):
            filename = os.fsdecode(file)
            if filename.endswith('csv'):
                list_name = filename.replace('.csv','')
                shopping_lists.append(list_name)

        if list_name == '':
            
            InputErrorDialog('WRONG! Needs a name.').exec()
            return

        elif list_name in shopping_lists:

            InputErrorDialog('WRONG! The recipe name ' + self.filename_field.text() + ' is taken Try another.').exec()
            return
        
        else:

            new_list_df.to_csv(cost.resolve_path('dep/ShoppingLists') + '/' + list_name + '.csv', mode='w', index=False)

            for layout in [self.ingr_name_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            SuccessDialog().exec()

            self.parent_window.close()
            self.close()

            return
        
    def close_window(self):

        self.close()


class EditOrderWindow(QMainWindow):

    def __init__(self, order_name, parent):

        self.select_units_window = None

        super().__init__()

        self.setWindowTitle('Edit Order')
        self.setWindowIcon(QIcon('dep/Icons/notebook--pencil.png'))

        self.parent_window = parent
        self.order_df = pd.read_csv(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv')

        self.orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

        self.order_list = []

        for file in os.listdir(self.orders_directory):
            filename = os.fsdecode(file)
            if filename.endswith('csv'):
                order_name = filename.replace('.csv','')
                self.order_list.append(order_name)

        # Fileame Input & Delete Order Area

        self.filename_header = QLabel('Order Name')
        self.filename_field = QLineEdit()
        self.filename_field.setText(capwords(order_name))
        self.filename_field.setFixedWidth(250)

        self.filename_input_area = QWidget()
        filename_layout = QVBoxLayout()
        filename_layout.addWidget(self.filename_header)
        filename_layout.addWidget(self.filename_field)
        self.filename_input_area.setLayout(filename_layout)

        # Order Deletion Button

        self.delete_order_button = QPushButton('delet this')
        self.delete_order_button.setIcon(QIcon(cost.resolve_path('dep/Icons/fire-big.png')))
        self.delete_order_button.clicked.connect(self.delete_order)

        # Combined Name Input and Deletion Area

        self.name_input_and_deletion_button_container_widget = QWidget()
        recipe_name_and_deletion_layout = QHBoxLayout()
        recipe_name_and_deletion_layout.addWidget(self.filename_input_area)
        recipe_name_and_deletion_layout.addWidget(self.delete_order_button)
        self.name_input_and_deletion_button_container_widget.setLayout(recipe_name_and_deletion_layout)

        # Recipe Input Area

        self.recipe_column = QWidget()
        self.recipe_layout = QVBoxLayout()
        self.recipe_layout.addWidget(QLabel('Recipe'))
        for k in range(1,len(self.order_df['rec']) + 1):
            self.recipe_layout.addWidget(RecipeField(parent=self, index=k))
        recipe_fields = (self.recipe_layout.itemAt(index) for index in range(1,self.recipe_layout.count())) 
        for index, field in enumerate(recipe_fields):
            field.widget().setCurrentIndex(list(cost.rec_dict.keys()).index(self.order_df['rec'][index]))
        if len(self.order_df['rec']) < 10:
            for k in range(10-len(self.order_df['rec'])):
                invisible_field = RecipeField()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.recipe_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.recipe_column.setLayout(self.recipe_layout)
        self.insertion_index = len(self.order_df['rec']) + 1

        self.qty_column = QWidget()
        self.qty_layout = QVBoxLayout()
        self.qty_layout.addWidget(QLabel('Quantity'))
        for k in range(1,len(self.order_df['qty']) + 1):
            self.qty_layout.addWidget(FloatField())
        qty_fields = (self.qty_layout.itemAt(index) for index in range(1,self.qty_layout.count())) 
        for index, field in enumerate(qty_fields):
            field.widget().setText(str(self.order_df['qty'][index]))
        if len(self.order_df['qty']) < 10:
            for k in range(10-len(self.order_df['qty'])):
                invisible_field = FloatField()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.qty_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.qty_column.setLayout(self.qty_layout)

        self.unit_column = QWidget()
        self.unit_layout = QVBoxLayout()
        self.unit_layout.addWidget(QLabel('Yield Unit'))
        for k in range(1,len(self.order_df['unit']) + 1):
            self.unit_layout.addWidget(UnitField([]))
        unit_fields = (self.unit_layout.itemAt(index) for index in range(1,self.unit_layout.count())) 
        for index, field in enumerate(unit_fields, start=1):
            yield_unit_list = list(cost.rec_dict[self.recipe_layout.itemAt(index).widget().currentText()].makes.keys())
            field.widget().addItems(yield_unit_list)
            field.widget().setCurrentIndex(yield_unit_list.index(self.order_df['unit'][index-1]))
        if len(self.order_df['unit']) < 10:
            for k in range(10-len(self.order_df['unit'])):
                invisible_field = UnitField([])
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.unit_layout.addWidget(invisible_field)
                invisible_field.hide()
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

        self.select_units_button = QPushButton('Generate Shopping List')
        self.select_units_button.clicked.connect(self.generate_unit_selection_window)

        self.close_button = QPushButton('Bye Felicia')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.save_order_button)
        main_button_layout.addWidget(self.select_units_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.filename_input_area)
        central_layout.addWidget(self.input_area)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_input_row(self):

        if self.insertion_index < 10:
            self.recipe_layout.insertWidget(self.insertion_index, RecipeField(parent=self, index=self.insertion_index))
            self.qty_layout.insertWidget(self.insertion_index, FloatField())
            self.unit_layout.insertWidget(self.insertion_index, UnitField([]))
            self.recipe_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.qty_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.unit_layout.itemAt(self.insertion_index+1).widget().setParent(None)
            self.insertion_index += 1
        else:
            self.recipe_layout.insertWidget(self.insertion_index, RecipeField(parent=self, index=self.insertion_index))
            self.qty_layout.insertWidget(self.insertion_index, FloatField())
            self.unit_layout.insertWidget(self.insertion_index, UnitField([]))
            self.insertion_index += 1

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

        if order_df.isnull().values.all():

            InputErrorDialog('WRONG! Empty of input.').exec()
            return
    
        elif order_df.isnull().values.any():

            InputErrorDialog('WRONG! Missing input(s).').exec()
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

        shopping_list_df.dropna(how='all', inplace=True)

        shopping_list_df = shopping_list_df.astype({'qty':'float64'})

        shopping_list_df['qty'] = shopping_list_df['qty'].round(3)

        shopping_list_df['cost'] = pd.Series()

        for k, row in shopping_list_df.iterrows():

            ingredient = cost.ingr_dict[row['ingr']]

            shopping_list_df['cost'][k] = round(ingredient.cost(qty=row['qty'], target_unit=row['unit'])[0], 2)

        print('in slc:', shopping_list_df.head())

        return shopping_list_df

    def save_order(self):

        order_df = self.order_df_constructor()

        order_name = self.filename_field.text().strip().lower()

        if order_name == '':
            
            InputErrorDialog('WRONG! Needs a name.').exec()
            return
        
        else:

            try:
                os.remove(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv')
            except OSError as error:
                print(error)

            order_df.to_csv(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv', mode='w', index=False)

            for layout in [self.recipe_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            self.order_list = []

            for file in os.listdir(self.orders_directory):
                filename = os.fsdecode(file)
                if filename.endswith('csv'):
                    order_name = filename.replace('.csv','')
                    self.order_list.append(order_name)

            self.parent_window.order_selector.clear()
            self.parent_window.order_selector.addItems(sorted(self.order_list))
            self.parent_window.order_selector.setEditable(True)
            self.parent_window.order_selector.setCompleter(QCompleter(self.order_list))
            self.parent_window.order_selector.setValidator(InputValidator(self.order_list))
            self.parent_window.order_selector.setCurrentIndex(-1)

            self.success_dialog = SuccessDialog()
            self.success_dialog.exec()

            return

    def generate_unit_selection_window(self, order_df):

        order_df = self.order_df_constructor()

        order_name = self.filename_field.text().strip().lower()

        if order_name == '':
            
            InputErrorDialog('WRONG! Needs a name.').exec()
            return
        
        else:

            try:
                os.remove(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv')
            except OSError as error:
                print(error)

            order_df.to_csv(cost.resolve_path('dep/Orders') + '/' + order_name + '.csv', mode='w', index=False)

            for layout in [self.recipe_layout, self.qty_layout, self.unit_layout]:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.filename_field.clear()

            self.order_list = []

            self.orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

            for file in os.listdir(self.orders_directory):
                filename = os.fsdecode(file)
                if filename.endswith('csv'):
                    order_name = filename.replace('.csv','')
                    self.order_list.append(order_name)

            self.parent_window.order_selector.clear()
            self.parent_window.order_selector.addItems(sorted(self.order_list))
            self.parent_window.order_selector.setEditable(True)
            self.parent_window.order_selector.setCompleter(QCompleter(self.order_list))
            self.parent_window.order_selector.setValidator(InputValidator(self.order_list))
            self.parent_window.order_selector.setCurrentIndex(-1)

        shopping_list_df = self.shopping_list_constructor(order_df)

        print('in gusw', shopping_list_df)

        self.select_units_window = SelectUnitsWindow(shopping_list_df, parent=self)
        self.select_units_window.show()

    def delete_order(self):

        if ConfirmationDialog(parent=self).exec():
                os.remove(cost.resolve_path('dep/Recipes') + '/' + self.recipe_name + '.csv')
                cost.main()
                SuccessDialog(parent=self).exec()
                self.parent_window.order_list = []
                orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))
                for file in os.listdir(orders_directory):
                    filename = os.fsdecode(file)
                    if filename.endswith('csv'):
                        order_name = filename.replace('.csv','')
                        self.parent_window.order_list.append(order_name)
                self.parent_window.recipe_selector.clear()
                self.parent_window.recipe_selector.addItems(self.parent_window.order_list)
                self.parent_window.recipe_selector.setCompleter(QCompleter(self.parent_window.order_list))
                self.parent_window.recipe_selector.setValidator(InputValidator(self.parent_window.order_list))
                self.parent_window.recipe_selector.setCurrentIndex(-1)
                self.close()
        else:
            return


    def close_window(self):

        self.close()

    def closeEvent(self, event):

        if self.select_units_window:
            self.select_units_window.close()

class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.add_order_window, self.edit_orders_window = None, None

        self.setWindowTitle('Orders')
        self.setWindowIcon(QIcon(cost.resolve_path('dep/Icons/service-bell.png')))
        self.setFixedWidth(300)

        self.orders_directory = os.fsencode(cost.resolve_path('dep/Orders'))

        self.order_list = []

        for file in os.listdir(self.orders_directory):
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

        vlayout.addWidget(self.order_selector)
        vlayout.addWidget(self.open_order_button)
        vlayout.addWidget(self.add_recipe_button)

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
        self.add_order_window = AddOrderWindow(parent=self)
        self.add_order_window.show()

    def generate_edit_order_window(self):
        
        order_name = self.order_selector.currentText()
        if order_name in self.order_list:
            cost.main()
            self.edit_orders_window = EditOrderWindow(order_name=order_name, parent=self)
            self.edit_orders_window.show()        

    def closeEvent(self, event):

        for w in [self.add_order_window, self.edit_orders_window]:
            if w:
                w.close()

def main():

    cost.main()

    app = QApplication()

    window = NavigationWindow()
    window.show()

    app.exec()

if __name__ == '__main__':

    main()

