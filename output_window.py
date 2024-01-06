
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QComboBox, QPushButton, QVBoxLayout, QLabel
from string import capwords
import cost


class OutputWindow(QMainWindow):

    def __init__(self, recipe, size, scale_factor):

        super().__init__()

        self.setWindowTitle(capwords(recipe.name))
        self.setFixedSize(300,300)

        layout = QVBoxLayout()        

        self.output_label = QLabel(cost.output_template(recipe.name, size, scale_factor))
        self.output_label.setAlignment(Qt.AlignLeft)

        self.close_button = QPushButton('Bet')
        self.close_button.clicked.connect(self.closeWindow)

        layout.addWidget(self.output_label)
        layout.addWidget(self.close_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeWindow(self):

        self.close()


class MainWindow(QMainWindow):

    def __init__(self, rec_dict):

        super().__init__()

        self.setWindowTitle('Get Cost and Pricing Info')
        self.setFixedSize(350,350)
        self.rec_dict = rec_dict

        layout = QVBoxLayout()
        
        self.recipe_label = QLabel('Select a recipe:')
        self.recipe_label.setAlignment(Qt.AlignLeft)

        self.recipe_selector = QComboBox()
        self.recipe_selector.addItems(rec_dict.keys())
        self.recipe_selector.setFixedSize(200,25)
        self.recipe_selector.activated.connect(self.current_recipe_selection)
        self.recipe_selector.currentIndexChanged.connect(self.update_sizes)

        self.size_label = QLabel('Select a size:')
        self.size_label.setAlignment(Qt.AlignLeft)

        self.size_selector = QComboBox()
        self.size_selector.addItems(rec_dict[self.current_recipe_selection()].makes.keys())
        self.size_selector.setFixedSize(200,25)
        self.size_selector.activated.connect(self.current_size_selection)

        self.factor_label = QLabel('Set margin by scale factor:')
        self.factor_label.setAlignment(Qt.AlignLeft)

        self.set_scale_factor = QComboBox()
        self.set_scale_factor.addItems(['1','2','3'])
        self.set_scale_factor.setFixedSize(50,25)
        self.set_scale_factor.activated.connect(self.current_scale_factor)
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
        layout.addWidget(self.display_output_button)
        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def current_recipe_selection(self, _=0):
        
        recipe_selection = self.recipe_selector.currentText()

        return recipe_selection
    
    def update_sizes(self, _):

        self.size_selector.clear()
        self.size_selector.addItems(self.rec_dict[self.current_recipe_selection()].makes.keys())

    def current_size_selection(self, _):
        
        size_selection = self.size_selector.currentText()

        return size_selection

    def current_scale_factor(self, _):
        
        factor_selection = self.set_scale_factor.currentText()
        
        return factor_selection
    
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

    window = MainWindow(rec_dict)

    window.show()

    app.exec()


if __name__ == '__main__':
    main()



    

