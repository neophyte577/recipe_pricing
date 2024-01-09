
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap 
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
import cost
import output_window


class NavigationWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Recipes')
        self.setFixedSize(300,120)

        hlayout = QHBoxLayout()

        vlayout = QVBoxLayout()
        
        self.add_recipe_button = QPushButton('Add Recipe')
        #self.add_recipe_button.clicked.connect(self.generate_add_rec_window)

        self.modify_recipe_button = QPushButton('Modify Recipe')
        #self.add_recipe_button.clicked.connect(self.generate_update_rec_window)

        self.price_recipe_button = QPushButton('Price Recipe')
        self.price_recipe_button.clicked.connect(self.generate_output_window)

        vlayout.addWidget(self.add_recipe_button)
        vlayout.addWidget(self.modify_recipe_button)
        vlayout.addWidget(self.price_recipe_button)

        icon = QLabel()
        pixmap = QPixmap('recipe_icon2.png')
        icon.setPixmap(pixmap)
               
        container_widget = QWidget()
        container_widget.setLayout(vlayout)
        
        hlayout.addWidget(container_widget)
        hlayout.addWidget(icon)
        hlayout.setContentsMargins(10,10,10,10)

        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)

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
    