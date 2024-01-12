
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QComboBox, QPushButton, QVBoxLayout, QLabel
from string import capwords
import cost


class OutputWindow(QMainWindow):

    def __init__(self, recipe, size, scale_factor):

        super().__init__()

        self.setWindowTitle(capwords(recipe.name) + ' Breakdown')
        
        font = QFont('Courier New')

        layout = QVBoxLayout()        

        self.output_label = QLabel(cost.output_template(recipe.name, size, scale_factor))
        self.output_label.setFont(font)
        self.output_label.setAlignment(Qt.AlignLeft)

        self.close_button = QPushButton('Bet')
        self.close_button.clicked.connect(self.close_window)

        layout.addWidget(self.output_label)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(15,0,15,15)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def close_window(self):

        self.close()


class SelectionWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Price Which?')
        icon = QIcon()
        icon.addFile('currency.png')
        self.setWindowIcon(icon)
        self.setFixedSize(250,200)
        self.rec_dict = cost.rec_dict

        layout = QVBoxLayout()
        
        self.recipe_label = QLabel('Select a recipe:')
        self.recipe_label.setAlignment(Qt.AlignLeft)

        self.recipe_selector = QComboBox()
        self.recipe_selector.addItems(self.rec_dict.keys())
        self.recipe_selector.setFixedSize(200,25)
        self.recipe_selector.currentIndexChanged.connect(self.update_sizes)

        self.size_label = QLabel('Select a size:')
        self.size_label.setAlignment(Qt.AlignLeft)

        self.size_selector = QComboBox()
        self.size_selector.addItems(self.rec_dict[self.recipe_selector.currentText()].makes.keys())
        self.size_selector.setFixedSize(200,25)
        self.factor_label = QLabel('Set margin by scale factor:')
        self.factor_label.setAlignment(Qt.AlignLeft)

        self.set_scale_factor = QComboBox()
        self.set_scale_factor.addItems(['3','2.5','2'])
        self.set_scale_factor.setFixedSize(50,25)
        self.set_scale_factor.setEditable(True)
        self.set_scale_factor.setInsertPolicy(QComboBox.InsertAlphabetically)

        self.display_output_button = QPushButton('Vamanos')
        self.display_output_button.setFixedSize(100,25)
        self.display_output_button.pressed.connect(self.display_button_pressed)

        layout.addWidget(self.recipe_label)
        layout.addWidget(self.recipe_selector)
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_selector)
        layout.addWidget(self.factor_label)
        layout.addWidget(self.set_scale_factor)
        layout.addWidget(self.display_output_button, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def update_sizes(self, _):

        self.size_selector.clear()
        self.size_selector.addItems(self.rec_dict[self.recipe_selector.currentText()].makes.keys())
    
    def display_button_pressed(self):

        recipe = self.rec_dict[self.recipe_selector.currentText()]

        size = self.size_selector.currentText()

        scale_factor = int(self.set_scale_factor.currentText())

        self.output = OutputWindow(recipe, size, scale_factor)

        self.output.show()
    

def main():

    cost.main()

    rec_dict = cost.rec_dict

    app = QApplication()

    window = SelectionWindow()
    window.show()

    app.exec()



if __name__ == '__main__':
    main()



    

