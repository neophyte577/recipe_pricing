
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap 
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
import cost

class IngredientInputRow(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QHBoxLayout()

        self.name_field = QLineEdit()
        self.cost_field = QLineEdit()
        self.qty_field = QLineEdit()
        self.unit_field = QLineEdit()
        self.density_field = QLineEdit()
        self.each_qty_field = QLineEdit()
        self.each_unit_field = QLineEdit()
        self.product_code_field = QLineEdit()

        self.edits = [ self.name_field,
                    self.cost_field,
                    self.qty_field,
                    self.unit_field,
                    self.density_field,
                    self.each_qty_field,
                    self.each_unit_field,
                    self.product_code_field ]

        self.layout.addWidget(self.name_field)
        self.layout.addWidget(self.cost_field)
        self.layout.addWidget(self.qty_field)
        self.layout.addWidget(self.unit_field)
        self.layout.addWidget(self.density_field)
        self.layout.addWidget(self.each_qty_field)
        self.layout.addWidget(self.each_unit_field)
        self.layout.addWidget(self.product_code_field)

        self.setLayout(self.layout)


class AddIngredientsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Ingredients')

        self.label_row = QWidget()
        self.button_row = QWidget()
        central_container_widget = QWidget()

        vlayout = QVBoxLayout()

        label_row_layout = QHBoxLayout()

        label_row_layout.addWidget(QLabel('Name'))
        label_row_layout.addWidget(QLabel('Cost'))
        label_row_layout.addWidget(QLabel('Quantity'))
        label_row_layout.addWidget(QLabel('Unit'))
        label_row_layout.addWidget(QLabel('Density'))
        label_row_layout.addWidget(QLabel('Each Qty'))
        label_row_layout.addWidget(QLabel('Each Unit'))
        label_row_layout.addWidget(QLabel('Product Code'))

        self.label_row.setLayout(label_row_layout)

        self.input_row = IngredientInputRow()

        button_row_layout = QHBoxLayout()

        self.add_ingr_button = QPushButton('Add Ingredient')
        self.add_ingr_button.clicked.connect(self.add_ingredient)

        self.close_button = QPushButton('Adios')
        self.close_button.clicked.connect(self.close_window)

        button_row_layout.addWidget(self.add_ingr_button)
        button_row_layout.addWidget(self.close_button)

        self.button_row.setLayout(button_row_layout)

        vlayout.addWidget(self.label_row)
        vlayout.addWidget(self.input_row)
        vlayout.addWidget(self.button_row)

        central_container_widget = QWidget()
        central_container_widget.setLayout(vlayout)
        self.setCentralWidget(central_container_widget)

    def add_ingredient(self):

        for edit in self.input_row.edits:
            edit.clear()

    def close_window(self):

        self.close()


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Ingredients')
        self.setFixedSize(300,120)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()
        
        self.add_ingr_button = QPushButton('Add Ingredients')
        self.add_ingr_button.clicked.connect(self.generate_add_ingr_window)

        self.update_ingr_button = QPushButton('Update Ingredients')
        #self.add_ingr_button.clicked.connect(self.generate_update_ingr_window)

        self.edit_ingr_button = QPushButton('Manually Edit Ingredients')
        #self.add_ingr_button.clicked.connect(self.generate_edit_ingr_window)

        vlayout.addWidget(self.add_ingr_button)
        vlayout.addWidget(self.update_ingr_button)
        vlayout.addWidget(self.edit_ingr_button)

        icon = QLabel()
        pixmap = QPixmap('ingredients_icon3.jpg')
        icon.setPixmap(pixmap)
               
        container_widget = QWidget()
        container_widget.setLayout(vlayout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

    def generate_add_ingr_window(self):

        self.add_ingr_window = AddIngredientsWindow()
        self.add_ingr_window.show()


def main():

    cost.main()

    app = QApplication()

    window = NavigationWindow()

    window.show()

    app.exec()



if __name__ == '__main__':

    main()
    