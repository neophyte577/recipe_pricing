
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap 
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
import cost
import output_window


class YieldInputRow(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QHBoxLayout()

        self.makes_field = QLineEdit()
        self.size_field = QLineEdit()

        self.edits = [self.makes_field, self.size_field]

        self.layout.addWidget(self.makes_field)
        self.layout.addWidget(self.size_field)

        self.setLayout(self.layout)


class IngredientInputRow(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QHBoxLayout()

        self.ingr_name_field = QLineEdit()
        self.qty_field = QLineEdit()
        self.unit_field = QLineEdit()

        self.edits = [self.ingr_name_field, self.qty_field, self.unit_field]

        self.layout.addWidget(self.ingr_name_field)
        self.layout.addWidget(self.qty_field)
        self.layout.addWidget(self.unit_field)

        self.setLayout(self.layout)


class AddRecipeWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Recipe')

        self.ingredient_header = QWidget()
        self.yield_header = QWidget()
        self.ingredient_input_widget = QWidget()
        self.yield_input_widget = QWidget()
        self.combined_input_widget = QWidget()
        self.button_row = QWidget()
        central_container_widget = QWidget()

        # Ingredient Column

        ingredient_header_layout = QHBoxLayout()
        ingredient_header_layout.addWidget(QLabel('Ingredient'))
        ingredient_header_layout.addWidget(QLabel('Quantity'))
        ingredient_header_layout.addWidget(QLabel('Unit'))
    
        self.ingredient_header.setLayout(ingredient_header_layout)

        self.ingredient_input_row = IngredientInputRow()

        ingredient_layout = QVBoxLayout()
        ingredient_layout.addWidget(self.ingredient_header)
        ingredient_layout.addWidget(self.ingredient_input_row)

        self.ingredient_input_widget.setLayout(ingredient_layout)

        # Yield Column

        yield_header_layout = QHBoxLayout()
        yield_header_layout.addWidget(QLabel('Makes'))
        yield_header_layout.addWidget(QLabel('Size'))

        self.yield_header.setLayout(yield_header_layout)

        self.yield_input_row = YieldInputRow()

        yield_layout = QVBoxLayout()
        yield_layout.addWidget(self.yield_header)
        yield_layout.addWidget(self.yield_input_row)

        self.yield_input_widget.setLayout(yield_layout)

        # Combined Header & Input Row

        combined_input_layout = QHBoxLayout()
        combined_input_layout.addWidget(self.ingredient_input_widget)
        combined_input_layout.addWidget(self.yield_input_widget)

        self.combined_input_widget.setLayout(combined_input_layout)

        # Button Row

        button_row_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Add Recipe')
        self.add_ingr_button.clicked.connect(self.add_ingredient)

        self.close_button = QPushButton('Adios')
        self.close_button.clicked.connect(self.close_window)

        button_row_layout.addWidget(self.add_ingr_button)
        button_row_layout.addWidget(self.close_button)

        self.button_row.setLayout(button_row_layout)

        # Central Widget

        central_layout = QVBoxLayout()

        central_layout.addWidget(self.combined_input_widget)
        central_layout.addWidget(self.button_row)

        central_container_widget = QWidget()
        central_container_widget.setLayout(central_layout)
        self.setCentralWidget(central_container_widget)

    def add_ingredient(self):

        for edit in self.input_row.edits:
            edit.clear()

    def close_window(self):

        self.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Recipes')
        self.setFixedSize(300,120)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()
        
        self.add_recipe_button = QPushButton('Add Recipe')
        self.add_recipe_button.clicked.connect(self.generate_add_recipe_window)

        self.modify_recipe_button = QPushButton('Modify Recipe')
        #self.add_recipe_button.clicked.connect(self.generate_update_rec_window)

        self.price_recipe_button = QPushButton('Price Recipe')
        self.price_recipe_button.clicked.connect(self.generate_output_window)

        vlayout.addWidget(self.add_recipe_button)
        vlayout.addWidget(self.modify_recipe_button)
        vlayout.addWidget(self.price_recipe_button)

        icon = QLabel()
        pixmap = QPixmap('recipe_icon.png')
        icon.setPixmap(pixmap)
               
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
        

    def generate_output_window(self):

        self.output_window = output_window.SelectionWindow()
        self.output_window.show()


def main():

    cost.main()

    app = QApplication()

    window = NavigationWindow()
    window.show()

    app.exec()


if __name__ == '__main__':

    main()
    