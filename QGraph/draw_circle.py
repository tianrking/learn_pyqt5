
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene,QGraphicsObject

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen,QColor
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem)

class Planet(QGraphicsObject):
    def __init__(self, parent=None):
        super(Planet, self).__init__(parent)
        self.color = QColor(Qt.lightGray)
        self.dragOver = False
        self.setAcceptDrops(True)

    def dragLeaveEvent(self, event):
        self.dragOver = False
        self.update()
    
    def dropEvent(self, event):
        self.dragOver = False
        self.update()


a = Planet()

view = QGraphicsView(a)
view.setWindowTitle('w0x7ce')
view.resize(480, 320)
view.show()
sys.exit(app.exec_())