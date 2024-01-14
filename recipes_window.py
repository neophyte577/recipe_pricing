
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon, QDoubleValidator
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QLabel, QCompleter, QComboBox, QLineEdit, QPushButton, QVBoxLayout, 
                               QGridLayout, QHBoxLayout, QStackedLayout, QScrollArea, QSizePolicy)
import pandas as pd
import cost
import output_window


class IngredientInputRow(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QHBoxLayout()

        self.ingr_name_field = QLineEdit()
        ingredients_list = cost.ingr_dict.keys()
        self.ingr_name_field.setCompleter(QCompleter(ingredients_list))

        self.qty_field = QLineEdit()
        self.qty_field.setValidator(QDoubleValidator())

        self.unit_field = QComboBox()
        self.unit_field.addItems(cost.unit_list)
        self.unit_field.setEditable(True)
        self.unit_field.setCompleter(QCompleter(cost.unit_list))
        self.unit_field.setCurrentIndex(-1)

        self.edits = [self.ingr_name_field, self.qty_field, self.unit_field]

        self.layout.addWidget(self.ingr_name_field)
        self.layout.addWidget(self.qty_field)
        self.layout.addWidget(self.unit_field)

        self.setLayout(self.layout)
        

class YieldInputRow(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QHBoxLayout()

        self.makes_field = QLineEdit()
        self.makes_field.setValidator(QDoubleValidator())

        self.size_field = QComboBox()
        self.size_field.addItems(cost.size_list)
        self.size_field.setEditable(True)
        self.size_field.setCompleter(QCompleter(cost.size_list))
        self.size_field.setCurrentIndex(-1)

        self.edits = [self.makes_field, self.size_field]

        self.layout.addWidget(self.makes_field)
        self.layout.addWidget(self.size_field)

        self.setLayout(self.layout)


class AddRecipeWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Recipe')
        self.setWindowIcon(QIcon('cake--plus.png'))

        self.ingredient_header = QWidget()
        self.yield_header = QWidget()
        self.ingredient_input_widget = QWidget()
        self.yield_input_widget = QWidget()
        self.combined_input_widget = QWidget()
        self.addition_button_row = QWidget()
        self.main_button_row = QWidget()
        self.central_container_widget = QWidget()

        # Ingredient Column

        ingredient_header_layout = QHBoxLayout()
        ingredient_header_layout.addWidget(QLabel('Ingredient'))
        ingredient_header_layout.addWidget(QLabel('Quantity'))
        ingredient_header_layout.addWidget(QLabel('Unit'))
    
        self.ingredient_header.setLayout(ingredient_header_layout)

        self.add_ingr_row_button = QPushButton('Add Another Ingredient')
        self.add_ingr_row_button.setIcon(QIcon('Icons/plus-button.png'))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_ingredient_input_row)

        ingredient_layout = QVBoxLayout()
        self.ingredient_input_layout = QVBoxLayout()
        self.ingredient_input_container_widget = QWidget()
        self.ingredient_input_container_widget.setLayout(self.ingredient_input_layout)
        for k in range(10):
            self.ingredient_input_layout.addWidget(IngredientInputRow())
        self.ingredient_input_layout.addStretch()

        self.ingredient_scroll_area = QScrollArea()
        self.ingredient_scroll_area.setWidget(self.ingredient_input_container_widget)
        self.ingredient_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ingredient_scroll_area.setWidgetResizable(True)

        ingredient_layout.addWidget(self.ingredient_header)
        ingredient_layout.addWidget(self.ingredient_scroll_area)
        ingredient_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_widget.setLayout(ingredient_layout)

        # Yield Column

        yield_header_layout = QHBoxLayout()
        yield_header_layout.addWidget(QLabel('Makes'))
        yield_header_layout.addWidget(QLabel('Size'))

        self.yield_header.setLayout(yield_header_layout)

        self.add_yield_row_button = QPushButton('Add Another Yield')
        self.add_yield_row_button.setIcon(QIcon('Icons/plus-button.png'))
        self.add_yield_row_button.setFixedWidth(130)
        self.add_yield_row_button.clicked.connect(self.add_yield_input_row)  

        yield_layout = QVBoxLayout()
        self.yield_input_layout = QVBoxLayout()
        self.yield_input_fields_container_widget = QWidget()
        self.yield_input_fields_container_widget.setLayout(self.yield_input_layout)
        for k in range(3):
            self.yield_input_layout.addWidget(YieldInputRow())
        for k in range(7):
            invisible_row = YieldInputRow()
            retain = QSizePolicy()
            retain.setRetainSizeWhenHidden(True)
            invisible_row.setSizePolicy(retain)
            invisible_row.hide()
            self.yield_input_layout.addWidget(invisible_row)
        self.yield_input_layout.addStretch()
        self.yield_insertion_index = 3
        
        self.yield_scroll_area = QScrollArea()
        self.yield_scroll_area.setWidget(self.yield_input_fields_container_widget)
        self.yield_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.yield_scroll_area.setWidgetResizable(True)

        yield_layout.addWidget(self.yield_header)
        yield_layout.addWidget(self.yield_scroll_area)
        yield_layout.addWidget(self.add_yield_row_button)
        self.yield_input_widget.setLayout(yield_layout)
    
        # Combined Header & Input Row

        combined_input_layout = QHBoxLayout()
        combined_input_layout.addWidget(self.ingredient_input_widget)
        combined_input_layout.addWidget(self.yield_input_widget)
        self.combined_input_widget.setLayout(combined_input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Add Recipe')
        self.add_ingr_button.clicked.connect(self.add_recipe)

        self.close_button = QPushButton('Adios')
        self.close_button.clicked.connect(self.close_window)

        main_button_layout.addWidget(self.add_ingr_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        central_layout = QVBoxLayout()

        central_layout.addWidget(self.combined_input_widget)
        central_layout.addWidget(self.addition_button_row)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)


    def add_ingredient_input_row(self):

        self.ingredient_input_layout.addWidget(IngredientInputRow())
        

    def add_yield_input_row(self):

        if self.yield_insertion_index < 10:
            self.yield_input_layout.insertWidget(self.yield_insertion_index, YieldInputRow())
            self.yield_input_layout.itemAt(self.yield_insertion_index+1).widget().setParent(None)
            self.yield_insertion_index += 1
        else:
            self.yield_input_layout.insertWidget(self.yield_insertion_index, YieldInputRow())        

    def add_recipe(self):

        for edit in self.ingredient_input_row.edits + self.yield_input_row.edits:
            edit.clear()

    def close_window(self):

        self.close()


class RecipeEditor(QMainWindow):

    def __init__(self, recipe):

        super().__init__()

        self.recipe_name = recipe.name
        self.rec_df = recipe.rec_df

        self.setWindowTitle('Edit ' + self.recipe_name.capitalize())
        self.setWindowIcon(QIcon('Icons/cake--pencil.png'))

        self.ingredient_header = QWidget()
        self.yield_header = QWidget()
        self.ingredient_input_widget = QWidget()
        self.yield_input_widget = QWidget()
        self.combined_input_widget = QWidget()
        self.addition_button_row = QWidget()
        self.main_button_row = QWidget()
        self.central_container_widget = QWidget()

        # Ingredient Column

        ingredient_header_layout = QHBoxLayout()
        ingredient_header_layout.addWidget(QLabel('Ingredient'))
        ingredient_header_layout.addWidget(QLabel('Quantity'))
        ingredient_header_layout.addWidget(QLabel('Unit'))
    
        self.ingredient_header.setLayout(ingredient_header_layout)

        self.add_ingr_row_button = QPushButton('Add Another Ingredient')
        self.add_ingr_row_button.setIcon(QIcon('Icons/plus-button.png'))
        self.add_ingr_row_button.setFixedWidth(160)
        self.add_ingr_row_button.clicked.connect(self.add_ingredient_input_row)

        ingredient_layout = QVBoxLayout()
        self.ingredient_input_layout = QVBoxLayout()
        self.ingredient_input_container_widget = QWidget()
        self.ingredient_input_container_widget.setLayout(self.ingredient_input_layout)
        for k in range(self.rec_df.shape[0]):
            self.ingredient_input_layout.addWidget(IngredientInputRow())
        self.ingredient_input_layout.addStretch()

        self.ingredient_scroll_area = QScrollArea()
        self.ingredient_scroll_area.setWidget(self.ingredient_input_container_widget)
        self.ingredient_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ingredient_scroll_area.setWidgetResizable(True)

        ingredient_layout.addWidget(self.ingredient_header)
        ingredient_layout.addWidget(self.ingredient_scroll_area)
        ingredient_layout.addWidget(self.add_ingr_row_button)
        self.ingredient_input_widget.setLayout(ingredient_layout)

        # Yield Column

        yield_header_layout = QHBoxLayout()
        yield_header_layout.addWidget(QLabel('Makes'))
        yield_header_layout.addWidget(QLabel('Size'))

        self.yield_header.setLayout(yield_header_layout)

        self.add_yield_row_button = QPushButton('Add Another Yield')
        self.add_yield_row_button.setIcon(QIcon('Icons/plus-button.png'))
        self.add_yield_row_button.setFixedWidth(130)
        self.add_yield_row_button.clicked.connect(self.add_yield_input_row)  

        yield_layout = QVBoxLayout()
        self.yield_input_layout = QVBoxLayout()
        self.yield_input_fields_container_widget = QWidget()
        self.yield_input_fields_container_widget.setLayout(self.yield_input_layout)
        for k in range(self.rec_df.shape[0]):
            self.yield_input_layout.addWidget(YieldInputRow())
        self.yield_input_layout.addStretch()
        self.yield_insertion_index = 3
        
        self.yield_scroll_area = QScrollArea()
        self.yield_scroll_area.setWidget(self.yield_input_fields_container_widget)
        self.yield_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.yield_scroll_area.setWidgetResizable(True)

        yield_layout.addWidget(self.yield_header)
        yield_layout.addWidget(self.yield_scroll_area)
        yield_layout.addWidget(self.add_yield_row_button)
        self.yield_input_widget.setLayout(yield_layout)
    
        # Combined Header & Input Row

        combined_input_layout = QHBoxLayout()
        combined_input_layout.addWidget(self.ingredient_input_widget)
        combined_input_layout.addWidget(self.yield_input_widget)
        self.combined_input_widget.setLayout(combined_input_layout)

        # Main Button Row

        main_button_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Update Recipe')
        self.add_ingr_button.clicked.connect(self.update_recipe)

        self.close_button = QPushButton('Sike')
        self.close_button.clicked.connect(self.close_window)

        main_button_layout.addWidget(self.add_ingr_button)
        main_button_layout.addWidget(self.close_button)
        self.main_button_row.setLayout(main_button_layout)

        # Central Widget

        central_layout = QVBoxLayout()

        central_layout.addWidget(self.combined_input_widget)
        central_layout.addWidget(self.addition_button_row)
        central_layout.addWidget(self.main_button_row)

        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)

    def add_ingredient_input_row(self):

        self.ingredient_input_layout.addWidget(IngredientInputRow())

    def add_yield_input_row(self):

        self.yield_input_layout.addWidget(YieldInputRow())        

    def update_recipe(self):

        self.close()

    def close_window(self):

        self.close()

class MissingFieldsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Zoinks!')
        self.setWindowIcon(QIcon('Icons/dummy.png'))

        self.error_message = QPushButton('WRONG! Needs more data.')
        self.error_message.setIcon(QIcon('prohibition.png'))
        self.error_message.clicked.connect(self.close_window)

        self.setCentralWidget(self.error_message)

    def close_window(self):

        self.close()

class EditRecipesWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.recipe_editor = None

        self.setWindowTitle('Edit Recipes')
        self.setWindowIcon(QIcon('Icons/cake--pencil.png'))

        self.recipe_selector = QComboBox()
        self.recipe_selector.addItems(cost.rec_dict.keys())
        self.recipe_selector.setEditable(True)
        self.recipe_selector.setCompleter(QCompleter(cost.rec_dict.keys()))

        self.main_button_row = QWidget()
        main_button_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Edit Recipe')
        self.add_ingr_button.clicked.connect(self.edit_recipe)

        self.close_button = QPushButton('Sayonara')
        self.close_button.clicked.connect(self.close_window)

        main_button_layout.addWidget(self.add_ingr_button)
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

        self.recipe_editor = RecipeEditor(selected_recipe)
        self.recipe_editor.show()

    def close_window(self):

        self.close()

    def closeEvent(self, event):

        if self.recipe_editor:

            self.recipe_editor.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.add_recipe_window, self.edit_recipe_window, self.output_window = None, None, None

        self.setWindowTitle('Recipes')
        self.setWindowIcon(QIcon('cake.png'))
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
        icon.setPixmap(QPixmap('Icons/recipe_icon.png'))
               
        container_widget = QWidget()
        container_widget.setLayout(vlayout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    def generate_add_recipe_window(self):

        self.add_recipe_window = AddRecipeWindow()
        self.add_recipe_window.show()

    def generate_edit_recipes_window(self):
        
        self.edit_recipes_window = EditRecipesWindow()
        self.edit_recipes_window.show()        

    def generate_output_window(self):

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
    