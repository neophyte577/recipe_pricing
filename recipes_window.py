from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon, QValidator, QDoubleValidator
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QDialog, QLabel, QCompleter, QComboBox, QLineEdit, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QScrollArea, QSizePolicy, QDialogButtonBox)
from string import capwords
from os import remove
import numpy as np
import pandas as pd
import cost
import output_window

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
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/tick.png')))

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
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/exclamation--frame.png')))

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
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/dummy.png')))

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
            
            if cost.ingr_dict[self.currentText()].density != np.pi:
                units = cost.unit_list
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

class AddRecipeWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Recipe')
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/cake--plus.png')))

        # Recipe Name Input Area

        self.recipe_name_header = QLabel('Recipe Name')
        self.recipe_name_field = QLineEdit()
        self.recipe_name_field.setFixedWidth(250)

        self.recipe_name_input_area = QWidget()
        recipe_name_layout = QVBoxLayout()
        recipe_name_layout.addWidget(self.recipe_name_header)
        recipe_name_layout.addWidget(self.recipe_name_field)
        self.recipe_name_input_area.setLayout(recipe_name_layout)

        # Ingredient Input Area

        self.ingr_name_column = QWidget()
        self.ingr_name_layout = QVBoxLayout()
        self.ingr_name_layout.addWidget(QLabel('Ingredient Name'))
        for k in range(1,11):
            self.ingr_name_layout.addWidget(IngredientNameField(parent=self, index=k))
        self.ingr_name_column.setLayout(self.ingr_name_layout)
        self.ingredient_index = 11

        self.qty_column = QWidget()
        self.qty_layout = QVBoxLayout()
        self.qty_layout.addWidget(QLabel('Quantity'))
        for k in range(10):
            self.qty_layout.addWidget(FloatField())
        self.qty_column.setLayout(self.qty_layout)

        self.unit_column = QWidget()
        self.unit_layout = QVBoxLayout()
        self.unit_layout.addWidget(QLabel('Unit'))
        for k in range(10):
            self.unit_layout.addWidget(UnitField(sorted(cost.unit_list)))
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
        self.add_ingr_row_button.setIcon(QIcon(cost.resolve_path('Icons/plus-button.png')))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_ingredient_input_row)

        self.ingredient_input_area = QWidget()
        ingredient_input_layout = QVBoxLayout()
        ingredient_input_layout.addWidget(self.ingredient_scroll_area)
        ingredient_input_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_area.setLayout(ingredient_input_layout)

        # Yield Input Area

        self.makes_column = QWidget()
        self.makes_layout = QVBoxLayout()
        self.makes_layout.addWidget(QLabel('Makes'))
        for k in range(3):
            self.makes_layout.addWidget(FloatField())
        for k in range(7):
            invisible_field = FloatField()
            retain = QSizePolicy()
            retain.setRetainSizeWhenHidden(True)
            invisible_field.setSizePolicy(retain)
            self.makes_layout.addWidget(invisible_field)
            invisible_field.hide()
        self.makes_column.setLayout(self.makes_layout)

        self.size_column = QWidget()
        self.size_layout = QVBoxLayout()
        self.size_layout.addWidget(QLabel('Size'))
        for k in range(3):
            self.size_layout.addWidget(UnitField(cost.size_list))
        for k in range(7):
            invisible_field = UnitField(cost.size_list)
            retain = QSizePolicy()
            retain.setRetainSizeWhenHidden(True)
            invisible_field.setSizePolicy(retain)
            self.size_layout.addWidget(invisible_field)
            invisible_field.hide()
        self.size_column.setLayout(self.size_layout)

        self.yield_input_fields_container_widget = QWidget()
        yield_input_layout = QHBoxLayout()
        yield_input_layout.addWidget(self.makes_column)
        yield_input_layout.addWidget(self.size_column)
        self.yield_input_fields_container_widget.setLayout(yield_input_layout)

        self.yield_scroll_area = QScrollArea()
        self.yield_scroll_area.setWidget(self.yield_input_fields_container_widget)
        self.yield_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.yield_scroll_area.setWidgetResizable(True)

        self.add_yield_row_button = QPushButton('Add Another Yield')
        self.add_yield_row_button.setIcon(QIcon(cost.resolve_path('Icons/plus-button.png')))
        self.add_yield_row_button.setFixedWidth(160)
        self.yield_insertion_index = 4
        self.add_yield_row_button.clicked.connect(self.add_yield_input_row)

        self.yield_input_area = QWidget()
        yield_input_layout = QVBoxLayout()
        yield_input_layout.addWidget(self.yield_scroll_area)
        yield_input_layout.addWidget(self.add_yield_row_button)
        self.yield_input_area.setLayout(yield_input_layout)

        # Combined Input Areas

        self.ingredient_input_with_header = QWidget()
        ingr_with_header_layout = QVBoxLayout()
        ingr_with_header_layout.addWidget(QLabel('Ingredients'))
        ingr_with_header_layout.addWidget(self.ingredient_input_area)
        self.ingredient_input_with_header.setLayout(ingr_with_header_layout)

        self.yield_input_with_header = QWidget()
        yield_with_header_layout = QVBoxLayout()
        yield_with_header_layout.addWidget(QLabel('Yield'))
        yield_with_header_layout.addWidget(self.yield_input_area)
        self.yield_input_with_header.setLayout(yield_with_header_layout)

        self.combined_input_widget = QWidget()
        combined_input_layout = QHBoxLayout()
        combined_input_layout.addWidget(self.ingredient_input_with_header)
        combined_input_layout.addWidget(self.yield_input_with_header)
        self.combined_input_widget.setLayout(combined_input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Add Recipe')
        self.add_ingr_button.clicked.connect(self.add_recipe)

        self.close_button = QPushButton('Adios')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.add_ingr_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.recipe_name_input_area)
        central_layout.addWidget(self.combined_input_widget)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_ingredient_input_row(self):

        self.ingr_name_layout.addWidget(IngredientNameField(parent=self, index=self.ingredient_index))
        self.ingredient_index += 1
        self.qty_layout.addWidget(FloatField())
        self.unit_layout.addWidget(UnitField(sorted(cost.unit_list)))

    def add_yield_input_row(self):

        if self.yield_insertion_index < 10:
            self.makes_layout.insertWidget(self.yield_insertion_index, FloatField())
            self.size_layout.insertWidget(self.yield_insertion_index, UnitField(cost.size_list))
            self.makes_layout.itemAt(self.yield_insertion_index+1).widget().setParent(None)
            self.size_layout.itemAt(self.yield_insertion_index+1).widget().setParent(None)
            self.yield_insertion_index += 1
        else:
            self.makes_layout.insertWidget(self.yield_insertion_index, FloatField())
            self.size_layout.insertWidget(self.yield_insertion_index, UnitField(cost.size_list))

    def add_recipe(self):

        input_df = pd.DataFrame()

        columns = []

        input_field_layouts = [self.ingr_name_layout, self.qty_layout, self.unit_layout, self.makes_layout, self.size_layout]

        for layout in input_field_layouts:
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

        if len(columns[0]) > len(columns[3]):
            for col in columns[3:]:
                col.extend( [np.nan] * (len(columns[0]) - len(col)) )
        elif len(columns[0]) < len(columns[3]):
             for col in columns[0:3]:
                col.extend( [np.nan] * (len(columns[3]) - len(col)) )
           
        headers = ['ingr','qty','unit','makes','size']

        for index, col in enumerate(columns):

            input_df.insert(index, headers[index], col)

        input_df.dropna(how='all')

        ingredient_input_df = input_df[['ingr','qty','unit']].dropna(how='all')

        ingredient_input_df.reset_index(inplace=True)

        yield_input_df = input_df[['makes','size']].dropna(how='all')

        yield_input_df.reset_index(inplace=True)

        new_rec_df = pd.DataFrame([ingredient_input_df['ingr'], ingredient_input_df['qty'], 
                                   ingredient_input_df['unit'], yield_input_df['makes'], yield_input_df['size']]).T

        recipe_name = self.recipe_name_field.text().lower().strip()

        if recipe_name == '':
        
            self.no_name_dialog = InputErrorDialog('WRONG! Needs name.')
            self.no_name_dialog.exec()
            return

        elif recipe_name in cost.rec_dict.keys():

            self.taken_name_dialog = InputErrorDialog('WRONG! The recipe name ' + self.recipe_name_field.text() + ' is taken Try another.')
            self.taken_name_dialog.exec()
            return

        elif input_df.isnull().values.all():

            self.empty_recipe_dialog = InputErrorDialog('WRONG! Empty of input.')
            self.empty_recipe_dialog.exec()
            return
    
        elif ingredient_input_df.isnull().values.all():

            self.empty_ingredients_dialog = InputErrorDialog('WRONG! Empty of ingredients.')
            self.empty_ingredients_dialog.exec()
            return
        
        elif yield_input_df.isnull().values.all():

            self.empty_yield_dialog = InputErrorDialog('WRONG! Empty of yield.')
            self.empty_yield_dialog.exec()
            return
        
        elif ingredient_input_df.isnull().values.any():

            self.missing_ingr_input_dialog = InputErrorDialog('WRONG! Missing input(s) in Ingredients.')
            self.missing_ingr_input_dialog.exec()
            return
        
        elif yield_input_df.isnull().values.any():

            self.missing_yield_input_dialog = InputErrorDialog('WRONG! Missing input(s) in Yield.')
            self.missing_yield_input_dialog.exec()
            return

        else:

            new_rec_df.to_csv(cost.resolve_path('Recipes') + '/' + recipe_name + '.csv', mode='w', index=False)

            for layout in input_field_layouts:
                input_fields = (layout.itemAt(index) for index in range(1,layout.count()))
                for field in input_fields:
                    field.widget().clear()
            
            self.recipe_name_field.clear()

            cost.main()

            self.success_dialog = SuccessDialog()
            self.success_dialog.exec()

            return
        
    def close_window(self):

        self.close()


class RecipeEditor(QMainWindow):

    def __init__(self, recipe, parent=None):

        super().__init__(parent)

        self.recipe_name = recipe.name
        self.rec_df = recipe.rec_df
        self.parent_window = parent

        self.setWindowTitle('Edit ' + capwords(self.recipe_name))
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/cake--pencil.png')))

        # Recipe Name Input Area

        self.recipe_name_header = QLabel('Change Recipe Name')
        self.recipe_name_field = QLineEdit()
        self.recipe_name_field.setFixedWidth(250)
        self.recipe_name_field.setText(capwords(self.recipe_name))

        self.recipe_name_input_area = QWidget()
        recipe_name_layout = QVBoxLayout()
        recipe_name_layout.addWidget(self.recipe_name_header)
        recipe_name_layout.addWidget(self.recipe_name_field)
        self.recipe_name_input_area.setLayout(recipe_name_layout)

        # Recipe Deletion Button

        self.delete_recipe_button = QPushButton('delet this')
        self.delete_recipe_button.setIcon(QIcon(cost.resolve_path('Icons/fire-big.png')))
        self.delete_recipe_button.clicked.connect(self.delete_recipe)

        # Combined Name Input and Deletion Area

        self.name_input_and_deletion_button_container_widget = QWidget()
        recipe_name_and_deletion_layout = QHBoxLayout()
        recipe_name_and_deletion_layout.addWidget(self.recipe_name_input_area)
        recipe_name_and_deletion_layout.addWidget(self.delete_recipe_button)
        self.name_input_and_deletion_button_container_widget.setLayout(recipe_name_and_deletion_layout)

        # Ingredient Edit Area

        try:
            self.ingr_name_column = QWidget()
            self.ingr_name_layout = QVBoxLayout()
            self.ingr_name_layout.addWidget(QLabel('Ingredient Name'))
            for k in range(1,len(self.rec_df['ingr']) + 1):
                self.ingr_name_layout.addWidget(IngredientNameField(parent=self, index=k))
            self.ingredient_index = len(self.rec_df['ingr']) + 1
            ingr_name_fields = (self.ingr_name_layout.itemAt(index) for index in range(1,self.ingr_name_layout.count())) 
            for index, field in enumerate(ingr_name_fields):
                field.widget().setCurrentIndex(list(sorted(cost.ingr_dict.keys())).index(self.rec_df['ingr'][index]))
            if len(self.rec_df['ingr']) < 10:
                for k in range(10-len(self.rec_df['ingr'])):
                    invisible_field = IngredientNameField()
                    retain = QSizePolicy()
                    retain.setRetainSizeWhenHidden(True)
                    invisible_field.setSizePolicy(retain)
                    self.ingr_name_layout.addWidget(invisible_field)
                    invisible_field.hide()
            self.ingr_name_column.setLayout(self.ingr_name_layout) 
        except Exception as error:
            print('gotcha', error) 

        self.qty_column = QWidget()
        self.qty_layout = QVBoxLayout()
        self.qty_layout.addWidget(QLabel('Quantity'))
        for k in range(len(self.rec_df['qty'])):
            self.qty_layout.addWidget(FloatField())
        qty_fields = (self.qty_layout.itemAt(index) for index in range(1,self.qty_layout.count())) 
        for index, field in enumerate(qty_fields):
            field.widget().setText(str(self.rec_df['qty'][index]))
        if len(self.rec_df['qty']) < 10:
            for k in range(10-len(self.rec_df['qty'])):
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
        for k in range(len(self.rec_df['unit'])):
            self.unit_layout.addWidget(UnitField(sorted(cost.unit_list)))
        unit_fields = (self.unit_layout.itemAt(index) for index in range(1,self.unit_layout.count())) 
        for index, field in enumerate(unit_fields, start=1):
            ingredient_input = self.ingr_name_layout.itemAt(index).widget().currentText()
            unit_list = self.ingr_name_layout.itemAt(index).widget().get_units(ingredient_input)
            field.widget().clear()
            field.widget().addItems(sorted(unit_list))
            field.widget().setCompleter(QCompleter(unit_list))
            field.widget().setValidator(InputValidator(unit_list))
            field.widget().setCurrentIndex(sorted(unit_list).index(self.rec_df['unit'][index-1]))
        if len(self.rec_df['unit']) < 10:
            for k in range(10-len(self.rec_df['unit'])):
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
        self.add_ingr_row_button.setIcon(QIcon(cost.resolve_path('Icons/plus-button.png')))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_ingredient_input_row)
        self.ingredient_insertion_index = len(self.rec_df['ingr']) + 1

        self.ingredient_input_area = QWidget()
        ingredient_input_layout = QVBoxLayout()
        ingredient_input_layout.addWidget(self.ingredient_scroll_area)
        ingredient_input_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_area.setLayout(ingredient_input_layout)

        # Yield Edit Area

        self.makes_column = QWidget()
        self.makes_layout = QVBoxLayout()
        self.makes_layout.addWidget(QLabel('Makes'))
        makes_data = self.rec_df['makes'].dropna()
        for k in range(len(makes_data)):
            self.makes_layout.addWidget(FloatField())
        makes_fields = (self.makes_layout.itemAt(index) for index in range(1,self.makes_layout.count())) 
        for index, field in enumerate(makes_fields):
            field.widget().setText(str(makes_data[index]))
        if len(makes_data) < 10:
            for k in range(10-len(makes_data)):
                invisible_field = FloatField()
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.makes_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.makes_column.setLayout(self.makes_layout)

        self.size_column = QWidget()
        self.size_layout = QVBoxLayout()
        self.size_layout.addWidget(QLabel('Size'))
        size_data = self.rec_df['size'].dropna()
        for k in range(len(size_data)):
            self.size_layout.addWidget(UnitField(cost.size_list))
        size_fields = (self.size_layout.itemAt(index) for index in range(1,self.size_layout.count())) 
        for index, field in enumerate(size_fields):
            field.widget().setCurrentIndex(cost.size_list.index(size_data[index]))
        if len(size_data) < 10:
            for k in range(10-len(size_data)):
                invisible_field = UnitField(cost.size_list)
                retain = QSizePolicy()
                retain.setRetainSizeWhenHidden(True)
                invisible_field.setSizePolicy(retain)
                self.size_layout.addWidget(invisible_field)
                invisible_field.hide()
        self.size_column.setLayout(self.size_layout)

        self.yield_input_fields_container_widget = QWidget()
        yield_input_layout = QHBoxLayout()
        yield_input_layout.addWidget(self.makes_column)
        yield_input_layout.addWidget(self.size_column)
        self.yield_input_fields_container_widget.setLayout(yield_input_layout)

        self.yield_scroll_area = QScrollArea()
        self.yield_scroll_area.setWidget(self.yield_input_fields_container_widget)
        self.yield_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.yield_scroll_area.setWidgetResizable(True)

        self.add_yield_row_button = QPushButton('Add Another Yield')
        self.add_yield_row_button.setIcon(QIcon(cost.resolve_path('Icons/plus-button.png')))
        self.add_yield_row_button.setFixedWidth(160)
        self.yield_insertion_index = len(makes_data) + 1
        self.add_yield_row_button.clicked.connect(self.add_yield_input_row)

        self.yield_input_area = QWidget()
        yield_input_layout = QVBoxLayout()
        yield_input_layout.addWidget(self.yield_scroll_area)
        yield_input_layout.addWidget(self.add_yield_row_button)
        self.yield_input_area.setLayout(yield_input_layout)

        # Combined Edit Areas

        self.ingredient_input_with_header = QWidget()
        ingr_with_header_layout = QVBoxLayout()
        ingr_with_header_layout.addWidget(QLabel('Ingredients'))
        ingr_with_header_layout.addWidget(self.ingredient_input_area)
        self.ingredient_input_with_header.setLayout(ingr_with_header_layout)

        self.yield_input_with_header = QWidget()
        yield_with_header_layout = QVBoxLayout()
        yield_with_header_layout.addWidget(QLabel('Yield'))
        yield_with_header_layout.addWidget(self.yield_input_area)
        self.yield_input_with_header.setLayout(yield_with_header_layout)

        self.combined_input_widget = QWidget()
        combined_input_layout = QHBoxLayout()
        combined_input_layout.addWidget(self.ingredient_input_with_header)
        combined_input_layout.addWidget(self.yield_input_with_header)
        self.combined_input_widget.setLayout(combined_input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Save Changes')
        self.add_ingr_button.clicked.connect(self.save_recipe)

        self.close_button = QPushButton('Au Revoir')
        self.close_button.clicked.connect(self.close_window)

        self.main_button_row = QWidget()
        main_button_layout.addWidget(self.add_ingr_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()

        central_layout.addWidget(self.name_input_and_deletion_button_container_widget)
        central_layout.addWidget(self.combined_input_widget)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def delete_recipe(self):

        if ConfirmationDialog(parent=self).exec():
            remove(cost.resolve_path('Recipes') + '/' + self.recipe_name + '.csv')
            cost.main()
            print(sorted(list(cost.rec_dict.keys())))
            SuccessDialog(parent=self).exec()
            rec_list = list(cost.rec_dict.keys())
            self.parent_window.recipe_selector.clear()
            self.parent_window.recipe_selector.addItems(sorted(rec_list))
            self.parent_window.recipe_selector.setCompleter(QCompleter(rec_list))
            self.parent_window.recipe_selector.setValidator(InputValidator(rec_list))
            self.parent_window.recipe_selector.setCurrentIndex(-1)
            self.close()
        else:
            return

    def add_ingredient_input_row(self):

        if self.ingredient_insertion_index < 10:
            self.ingr_name_layout.insertWidget(self.ingredient_insertion_index, IngredientNameField(parent=self, index=self.ingredient_index))
            self.ingredient_index += 1
            self.qty_layout.insertWidget(self.ingredient_insertion_index, FloatField())
            self.unit_layout.insertWidget(self.ingredient_insertion_index, UnitField(cost.unit_list))
            self.ingr_name_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.qty_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.unit_layout.itemAt(self.ingredient_insertion_index+1).widget().setParent(None)
            self.ingredient_insertion_index += 1
        else:
            self.ingr_name_layout.insertWidget(self.ingredient_insertion_index, IngredientNameField())
            self.qty_layout.insertWidget(self.ingredient_insertion_index, FloatField())
            self.unit_layout.insertWidget(self.ingredient_insertion_index, UnitField(cost.unit_list))

    def add_yield_input_row(self):

        if self.yield_insertion_index < 10:
            self.makes_layout.insertWidget(self.yield_insertion_index, FloatField())
            self.size_layout.insertWidget(self.yield_insertion_index, UnitField(cost.size_list))
            self.makes_layout.itemAt(self.yield_insertion_index+1).widget().setParent(None)
            self.size_layout.itemAt(self.yield_insertion_index+1).widget().setParent(None)
            self.yield_insertion_index += 1
        else:
            self.makes_layout.insertWidget(self.yield_insertion_index, FloatField())
            self.size_layout.insertWidget(self.yield_insertion_index, UnitField(cost.size_list))
    
    def save_recipe(self):

        input_df = pd.DataFrame()

        columns = []

        input_field_layouts = [self.ingr_name_layout, self.qty_layout, self.unit_layout, self.makes_layout, self.size_layout]

        for layout in input_field_layouts:
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

        if len(columns[0]) > len(columns[3]):
            for col in columns[3:]:
                col.extend( [np.nan] * (len(columns[0]) - len(col)) )
        elif len(columns[0]) < len(columns[3]):
             for col in columns[0:3]:
                col.extend( [np.nan] * (len(columns[3]) - len(col)) )

        headers = ['ingr','qty','unit','makes','size']

        for index, col in enumerate(columns):

            input_df.insert(index, headers[index], col)

        input_df.dropna(how='all')

        ingredient_input_df = input_df[['ingr','qty','unit']].dropna(how='all')

        ingredient_input_df.reset_index(inplace=True)

        yield_input_df = input_df[['makes','size']].dropna(how='all')

        yield_input_df.reset_index(inplace=True)

        new_rec_df = pd.DataFrame([ingredient_input_df['ingr'], ingredient_input_df['qty'], 
                                   ingredient_input_df['unit'], yield_input_df['makes'], yield_input_df['size']]).T

        new_recipe_name = self.recipe_name_field.text().lower().strip()

        if new_recipe_name == '':
        
            self.no_name_dialog = InputErrorDialog('WRONG! Needs name.')
            self.no_name_dialog.exec()
            return

        elif input_df.isnull().values.all():

            self.empty_recipe_dialog = InputErrorDialog('WRONG! Empty of input.')
            self.empty_recipe_dialog.exec()
            return
    
        elif ingredient_input_df.isnull().values.all():

            self.empty_ingredients_dialog = InputErrorDialog('WRONG! Empty of ingredients.')
            self.empty_ingredients_dialog.exec()
            return
        
        elif yield_input_df.isnull().values.all():

            self.empty_yield_dialog = InputErrorDialog('WRONG! Empty of yield.')
            self.empty_yield_dialog.exec()
            return
        
        elif ingredient_input_df.isnull().values.any():

            self.missing_ingr_input_dialog = InputErrorDialog('WRONG! Missing input(s) in Ingredients.')
            self.missing_ingr_input_dialog.exec()
            return
        
        elif yield_input_df.isnull().values.any():

            self.missing_yield_input_dialog = InputErrorDialog('WRONG! Missing input(s) in Yield.')
            self.missing_yield_input_dialog.exec()
            return

        else:

            try:
                remove(cost.resolve_path('Recipes') + '/' + self.recipe_name + '.csv')
            except OSError as error:
                print(error)

            new_rec_df.to_csv(cost.resolve_path('Recipes') + '/' + new_recipe_name + '.csv', mode='w', index=False)

            cost.main()
            rec_list = list(cost.rec_dict.keys())
            self.parent_window.recipe_selector.clear()
            self.parent_window.recipe_selector.addItems(sorted(rec_list))
            self.parent_window.recipe_selector.setCompleter(QCompleter(rec_list))
            self.parent_window.recipe_selector.setValidator(InputValidator(rec_list))
            self.parent_window.recipe_selector.setCurrentIndex(-1)
            self.success_dialog = SuccessDialog()
            self.success_dialog.exec()
            self.close()

            return
        
    def close_window(self):

        self.close()


class EditRecipesWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.recipe_editor = None

        self.setWindowTitle('Edit Recipes')
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/cake--pencil.png')))
        self.setFixedWidth(275)

        self.recipe_selector = QComboBox()
        self.recipe_selector.addItems(sorted(cost.rec_dict.keys()))
        self.recipe_selector.setEditable(True)
        self.recipe_selector.setCompleter(QCompleter(cost.rec_dict.keys()))
        self.recipe_selector.setValidator(InputValidator(cost.rec_dict.keys()))
        self.recipe_selector.setCurrentIndex(-1)

        self.main_button_row = QWidget()
        main_button_layout = QHBoxLayout()

        self.edit_recipe_button = QPushButton('Edit Recipe')
        self.edit_recipe_button.clicked.connect(self.edit_recipe)

        self.close_button = QPushButton('Sayonara')
        self.close_button.clicked.connect(self.close_window)

        main_button_layout.addWidget(self.edit_recipe_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.recipe_selector)
        central_layout.addWidget(self.main_button_row)
        self.central_container_widget.setLayout(central_layout)

        self.setCentralWidget(self.central_container_widget)

    def edit_recipe(self):

        selected_recipe = cost.rec_dict[self.recipe_selector.currentText()]

        self.recipe_editor = RecipeEditor(recipe=selected_recipe, parent=self)
        self.recipe_editor.show()

    def close_window(self):

        self.close()

    def closeEvent(self, event):

        if self.recipe_editor:

            self.recipe_editor.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.add_recipe_window, self.edit_recipes_window, self.output_window = None, None, None

        self.setWindowTitle('Recipes')
        self.setWindowIcon(QIcon(cost.resolve_path('Icons/cake.png')))
        self.setFixedSize(275,120)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()
        
        self.add_recipe_button = QPushButton('Add Recipe')
        self.add_recipe_button.clicked.connect(self.generate_add_recipe_window)

        self.edit_recipes_button = QPushButton('Edit Recipes')
        self.edit_recipes_button.clicked.connect(self.generate_edit_recipes_window)

        self.price_recipe_button = QPushButton('Price Recipe')
        self.price_recipe_button.clicked.connect(self.generate_output_window)

        vlayout.addWidget(self.add_recipe_button)
        vlayout.addWidget(self.edit_recipes_button)
        vlayout.addWidget(self.price_recipe_button)

        icon = QLabel()
        icon.setPixmap(QPixmap(cost.resolve_path('Icons/recipe_icon.png')))
               
        container_widget = QWidget()
        container_widget.setLayout(vlayout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    def generate_add_recipe_window(self):

        cost.main()
        self.add_recipe_window = AddRecipeWindow()
        self.add_recipe_window.show()

    def generate_edit_recipes_window(self):
        
        cost.main()
        self.edit_recipes_window = EditRecipesWindow()
        self.edit_recipes_window.show()        

    def generate_output_window(self):

        cost.main()
        self.output_window = output_window.SelectionWindow()
        self.output_window.show()

    def closeEvent(self, event):

        for w in [self.add_recipe_window, self.edit_recipes_window, self.output_window]:
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
    