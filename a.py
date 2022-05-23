from cProfile import label
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.setGeometry(500,200,300,300)
        self.setWindowTitle("Test")
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Test Label")
        self.label.move(50,50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Click me")
        self.b1.clicked.connect(self.clicked)
    
    def clicked(self):
        # print("Click")
        self.label.setText("Press Button")
        self.update()

    def update(self):
        self.label.adjustSize()

def clicked():
    print("Click")

def window():
    # app = QApplication(sys.argv)
    # win = QMainWindow()
    # # win.setGeometry(xpos,ypos,width,height)
    # # win.setGeometry(500,200,300,300)
    # # win.setWindowTitle("Test")

    # # label = QtWidgets.QLabel(win)
    # # label.setText("Test Label")
    # # label.move(50,50)

    # # b1 = QtWidgets.QPushButton(win)
    # # b1.setText("Click me")
    # # b1.clicked.connect(clicked)

    # win.show()

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()

    sys.exit(app.exec_())

window()