
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
import ingredients_window, recipes_window, output_window
import cost

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Main Window')
        self.setWindowIcon(QIcon('cutleries.png'))
        self.setFixedSize(250,135)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()

        self.ingredients_button = QPushButton('Ingredientes')
        self.ingredients_button.clicked.connect(self.generate_ingredients_window)

        self.recipes_button = QPushButton('Recetas')
        self.recipes_button.clicked.connect(self.generate_recipes_window)

        self.pricing_button = QPushButton('Precios')
        self.pricing_button.pressed.connect(self.generate_output_window)

        vlayout.addStretch()
        vlayout.addWidget(self.ingredients_button)
        vlayout.addWidget(self.recipes_button)
        vlayout.addWidget(self.pricing_button)
        vlayout.addStretch()

        logo = QLabel()
        pixmap = QPixmap('chef_logo.png')
        logo.setPixmap(pixmap)

        container_widget = QWidget()
        container_widget.setLayout(vlayout)

        hlayout.addWidget(container_widget)
        hlayout.addWidget(logo)
        #hlayout.setContentsMargins(10,10,10,20)

        widget = QWidget()
        widget.setLayout(hlayout)

        self.setCentralWidget(widget)

    def generate_ingredients_window(self):

        self.ingredients_window = ingredients_window.NavigationWindow()
        self.ingredients_window.show()

    def generate_recipes_window(self):

        self.recipes_window = recipes_window.NavigationWindow()
        self.recipes_window.show()

    def generate_output_window(self):

        self.output_window = output_window.SelectionWindow()
        self.output_window.show()
        

def main():

    cost.main()

    app = QApplication()

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == '__main__':

    main()


    