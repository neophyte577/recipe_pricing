
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QPixmap, QValidator, QDoubleValidator, QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QLineEdit, QLabel, QComboBox, QCompleter, QPushButton, QVBoxLayout, 
                               QScrollArea, QHBoxLayout, QTableView, QDialog, QDialogButtonBox)
import pandas as pd
import cost

# Custom input validator

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

# Model for table view

class TableModel(QAbstractTableModel):

    def __init__(self, df):

        super().__init__()
        self.df = df

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self.df.iloc[index.row(), index.column()]
                return str(value)

    def rowCount(self, _):
        return self.df.shape[0]

    def columnCount(self, _):
        return self.df.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            if orientation == Qt.Vertical:
                return str(self.df.index[section])
            
    def flags(self, _):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable
    
    def setData(self, index, value, role):

        if role == Qt.EditRole:

            self.df.iloc[index.row(),index.column()] = value

            return True  
        
# General use dialogs

class SuccessDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__()

        self.setWindowTitle('You did it!')
        self.setWindowIcon(QIcon('Icons/tick.png'))

        self.button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button.button(QDialogButtonBox.Ok).setText('Cool')
        self.button.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.message = QLabel('Great success!')
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

class InputErrorDialog(QDialog):

    def __init__(self, parent=None, message=''):

        super().__init__()

        self.setWindowTitle('Zoinks!')
        self.setWindowIcon(QIcon('Icons/dummy.png'))

        self.button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button.button(QDialogButtonBox.Ok).setText('Ard')
        self.button.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.message = QLabel(message)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

# Add Ingredients window and associated dialogs

class AddIngredientWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Add Ingredient')
        self.setWindowIcon(QIcon('Icons/flask--plus.png'))

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
        self.unit_field.setValidator(InputValidator(cost.unit_list))
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
        self.each_unit_field.setValidator(InputValidator(cost.unit_list))
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

        ingredient_name = self.name_field.text().strip().lower()
            
        if any((field.text().strip() == '') for field in self.input_fields[0:3]) or (self.unit_field.currentText().strip() == ''):

            InputErrorDialog(self, 'WRONG! Needs more input.').exec()
            return
        
        elif ingredient_name in cost.ingr_dict.keys():

            InputErrorDialog(self, 'WRONG! ' + ingredient_name + ' is already an ingredient.').exec()
        
        else:

            new_ingr_row = []

            for field in self.input_fields:

                if isinstance(field, QLineEdit):

                    new_ingr_row.append(field.text())

                if isinstance(field, QComboBox):

                    new_ingr_row.append(field.currentText())

            pd.DataFrame([new_ingr_row]).to_csv('Ingredients.csv', mode='a', header=False, index=False)

            for field in self.input_fields:
                field.clear()

            cost.main()

            SuccessDialog(self).exec()

    def close_window(self):

        self.close()

# Edit Ingredients window 

class EditIngredientsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Edit Ingredients')
        self.setWindowIcon(QIcon('Icons/flask--pencil.png'))
        self.setFixedSize(900,600)

        # Viewing Table

        table = cost.ingr_df.copy(deep=True)
        table.set_index('name', inplace=True)
        table.columns = ['Cost', 'Quantity', 'Unit', 'Density', 'Each Quantity', 'Each Unit', 'Product Code']
        table.sort_index(ascending=True, inplace=True)
        table.fillna('', inplace=True)

        self.ingredients_table = QTableView()
        self.model = TableModel(table)
        self.ingredients_table.setModel(self.model)

        # Buttons

        self.save_button = QPushButton('Save Changes')
        self.save_button.clicked.connect(self.save_changes)
        
        self.close_button = QPushButton('Farewell')
        self.close_button.clicked.connect(self.close_window)
        
        self.button_row = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.close_button)
        self.button_row.setLayout(button_layout)
        
        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.ingredients_table)
        central_layout.addWidget(self.button_row)
        central_layout.setContentsMargins(5, 5, 5, 5)
        self.central_container_widget.setLayout(central_layout)
    
        self.setCentralWidget(self.central_container_widget)

    def save_changes(self):

        pass

    def close_window(self):

        self.close()

# Remove Ingredients window and associated dialog

class RemoveIngredientsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Remove Ingredients')
        self.setWindowIcon(QIcon('Icons/flask--minus.png'))
        self.setFixedWidth(275)

        # Selector

        self.ingredient_selector = QComboBox()
        self.ingredient_selector.addItems(sorted(cost.ingr_dict.keys()))
        self.ingredient_selector.setEditable(True)
        self.ingredient_selector.setCompleter(QCompleter(cost.ingr_dict.keys()))
        self.ingredient_selector.setValidator(InputValidator(cost.ingr_dict.keys()))
        self.ingredient_selector.setCurrentIndex(-1)

        # Buttons

        self.button_row = QWidget()
        button_layout = QHBoxLayout()

        self.remove_ingredient_button = QPushButton('Remove Ingredient')
        self.remove_ingredient_button.clicked.connect(self.remove_ingredient)

        self.close_button = QPushButton('Deuces')
        self.close_button.clicked.connect(self.close_window)

        button_layout.addWidget(self.remove_ingredient_button)
        button_layout.addWidget(self.close_button)
        self.button_row.setLayout(button_layout)

        self.central_container_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addStretch()
        central_layout.addWidget(self.ingredient_selector)
        central_layout.addWidget(self.button_row)
        self.central_container_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_container_widget)        

    def remove_ingredient(self):

        ingredient_selection = self.ingredient_selector.currentText().lower().strip()

        if ingredient_selection.strip() == '':

            InputErrorDialog(self, 'WRONG! Please enter an ingredient.').exec()
            return

        elif self.ingredient_selector.currentText().lower().strip() in cost.ingr_dict.keys():
            
            if ConfirmationDialog(self).exec():
                ingr_df = cost.ingr_df.copy(deep=True)
                ingr_df.drop(ingr_df[ingr_df['name']==self.ingredient_selector.currentText()].index, inplace=True)
                ingr_df.to_csv('Ingredients.csv', mode='w', index=False)
                self.ingredient_selector.removeItem(self.ingredient_selector.currentIndex())
                self.ingredient_selector.setCurrentIndex(-1)
                cost.main()
                SuccessDialog(self).exec()
            else:
                return
            
        else:
            InputErrorDialog(self, 'WRONG! ' + ingredient_selection.capitalize() + ' is not an ingredient!').exec()
            return

    def close_window(self):
        
        self.close()

class ConfirmationDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__()

        self.setWindowTitle('No Cap?')
        self.setWindowIcon(QIcon('Icons/exclamation--frame.png'))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText('frfr ong')
        self.buttons.button(QDialogButtonBox.Cancel).setText('Nah')
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.message = QLabel('Are you sure you finna buss it?')
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

# Main navigation window

class NavigationWindow(QMainWindow):

    def __init__(self):

        self.add_ingr_window, self.edit_ingr_window, self.remove_ingr_window = None, None, None

        super().__init__()

        self.setWindowTitle('Ingredients')
        self.setWindowIcon(QIcon('Icons/flask.png'))
        self.setFixedSize(300,120)
        
        hlayout = QHBoxLayout()

        central_layout = QVBoxLayout()
        
        self.add_ingr_button = QPushButton('Add Ingredients')
        self.add_ingr_button.clicked.connect(self.generate_add_ingr_window)

        self.view_ingr_button = QPushButton('Edit Ingredients')
        self.view_ingr_button.clicked.connect(self.generate_edit_ingredients_window)

        self.remove_ingr_button = QPushButton('Remove Ingredients')
        self.remove_ingr_button.clicked.connect(self.generate_remove_ingredients_window)

        central_layout.addWidget(self.add_ingr_button)
        central_layout.addWidget(self.view_ingr_button)
        central_layout.addWidget(self.remove_ingr_button)

        icon = QLabel()
        pixmap = QPixmap('Icons/ingredients_icon.png')
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

    def generate_edit_ingredients_window(self):

        self.edit_ingr_window = EditIngredientsWindow()
        self.edit_ingr_window.show()

    def generate_remove_ingredients_window(self):

        self.remove_ingr_window = RemoveIngredientsWindow()
        self.remove_ingr_window.show()

    def closeEvent(self, event):

        for w in [self.add_ingr_window, self.edit_ingr_window, self.remove_ingr_window]:
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
    