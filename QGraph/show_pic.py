
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene

import sys
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, )
# def showImage(self):

app = QApplication(sys.argv)
frame = QImage("../ui_designer/btc.png")
pix = QPixmap.fromImage(frame)
item = QGraphicsPixmapItem(pix)
scene = QGraphicsScene()
scene.addItem(item)
view = QGraphicsView(scene)
view.setWindowTitle('w0x7ce')
view.resize(480, 320)
view.show()
sys.exit(app.exec_())
