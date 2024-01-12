
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QDoubleValidator, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QLabel, QComboBox, QCompleter, QPushButton, QVBoxLayout, QHBoxLayout
import pandas as pd
import cost


class AddIngredientWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Ingredient')
        self.setWindowIcon(QIcon('flask--plus.png'))

        # Input Fields

        self.input_field_container_widget = QWidget()

        self.name_widget = QWidget()
        name_layout = QVBoxLayout()
        self.name_field = QLineEdit()
        name_layout.addWidget(QLabel('Name'))
        name_layout.addWidget(self.name_field)
        self.name_widget.setLayout(name_layout)
    
        self.cost_widget = QWidget()
        cost_layout = QVBoxLayout()
        self.cost_field = QLineEdit()
        self.cost_field.setValidator(QDoubleValidator())
        cost_layout.addWidget(QLabel('Cost'))
        cost_layout.addWidget(self.cost_field)
        self.cost_widget.setLayout(cost_layout)

        self.qty_widget = QWidget()
        qty_layout = QVBoxLayout()
        self.qty_field = QLineEdit()
        self.qty_field.setValidator(QDoubleValidator())
        qty_layout.addWidget(QLabel('Quantity'))
        qty_layout.addWidget(self.qty_field)
        self.qty_widget.setLayout(qty_layout)

        self.unit_widget = QWidget()
        unit_layout = QVBoxLayout()
        self.unit_field = QComboBox()
        self.unit_field.addItems(cost.unit_list)
        self.unit_field.setEditable(True)
        self.unit_field.setCompleter(QCompleter(cost.unit_list))
        self.unit_field.setCurrentIndex(-1)
        unit_layout.addWidget(QLabel('Unit'))
        unit_layout.addWidget(self.unit_field)
        self.unit_widget.setLayout(unit_layout)

        self.density_widget = QWidget()
        density_layout = QVBoxLayout()
        self.density_field = QLineEdit()
        self.density_field.setValidator(QDoubleValidator())
        density_layout.addWidget(QLabel('Density'))
        density_layout.addWidget(self.density_field)
        self.density_widget.setLayout(density_layout)

        self.each_qty_widget = QWidget()
        each_qty_layout = QVBoxLayout()
        self.each_qty_field = QLineEdit()
        self.each_qty_field.setValidator(QDoubleValidator())
        each_qty_layout.addWidget(QLabel('Each Quantity'))
        each_qty_layout.addWidget(self.each_qty_field)
        self.each_qty_widget.setLayout(each_qty_layout)

        self.each_unit_widget = QWidget()
        each_unit_layout = QVBoxLayout()
        self.each_unit_field = QComboBox()
        self.each_unit_field.addItems(cost.unit_list)
        self.each_unit_field.setEditable(True)
        self.each_unit_field.setCompleter(QCompleter(cost.unit_list))
        self.each_unit_field.setCurrentIndex(-1)
        each_unit_layout.addWidget(QLabel('Each Unit'))
        each_unit_layout.addWidget(self.each_unit_field)
        self.each_unit_widget.setLayout(each_unit_layout)

        self.product_code_widget = QWidget()
        product_code_layout = QVBoxLayout()
        self.product_code_field = QLineEdit()
        product_code_layout.addWidget(QLabel('Product Code'))
        product_code_layout.addWidget(self.product_code_field)
        self.product_code_widget.setLayout(product_code_layout)

        self.input_fields = [ self.name_field,
                    self.cost_field,
                    self.qty_field,
                    self.unit_field,
                    self.density_field,
                    self.each_qty_field,
                    self.each_unit_field,
                    self.product_code_field ]
        
        self.input_field_widgets = [ self.name_widget,
                    self.cost_widget,
                    self.qty_widget,
                    self.unit_widget,
                    self.density_widget,
                    self.each_qty_widget,
                    self.each_unit_widget,
                    self.product_code_widget ]
        
        input_layout = QHBoxLayout()
        for widget in self.input_field_widgets:
            input_layout.addWidget(widget)
        self.input_field_container_widget.setLayout(input_layout)
        
        # Buttons

        self.button_row = QWidget()

        button_row_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Add Ingredient')
        self.add_ingr_button.clicked.connect(self.add_ingredient)

        self.close_button = QPushButton('Adios')
        self.close_button.clicked.connect(self.close_window)

        button_row_layout.addWidget(self.add_ingr_button)
        button_row_layout.addWidget(self.close_button)
        self.button_row.setLayout(button_row_layout)

        # Central Layout

        self.central_container_widget = QWidget()

        central_layout = QVBoxLayout()

        central_layout.addWidget(self.input_field_container_widget)
        central_layout.addWidget(self.button_row)

        self.central_container_widget = QWidget()
        self.central_container_widget.setLayout(central_layout)

        self.setCentralWidget(self.central_container_widget)

    def add_ingredient(self):

        for field in self.input_fields:
            field.clear()

    def close_window(self):

        self.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Ingredients')
        self.setWindowIcon(QIcon('flask.png'))
        self.setFixedSize(300,120)
        

        hlayout = QHBoxLayout()

        central_layout = QVBoxLayout()
        
        self.add_ingr_button = QPushButton('Add Ingredients')
        self.add_ingr_button.clicked.connect(self.generate_add_ingr_window)

        self.update_ingr_button = QPushButton('Update Ingredients')
        #self.add_ingr_button.clicked.connect(self.generate_update_ingr_window)

        self.edit_ingr_button = QPushButton('Manually Edit Ingredients')
        #self.add_ingr_button.clicked.connect(self.generate_edit_ingr_window)

        central_layout.addWidget(self.add_ingr_button)
        central_layout.addWidget(self.update_ingr_button)
        central_layout.addWidget(self.edit_ingr_button)

        icon = QLabel()
        pixmap = QPixmap('ingredients_icon.png')
        icon.setPixmap(pixmap)
               
        container_widget = QWidget()
        container_widget.setLayout(central_layout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    def generate_add_ingr_window(self):

        self.add_ingr_window = AddIngredientWindow()
        self.add_ingr_window.show()


def main():

    cost.main()

    app = QApplication()

    window = NavigationWindow()

    window.show()

    app.exec()


if __name__ == '__main__':

    main()
    