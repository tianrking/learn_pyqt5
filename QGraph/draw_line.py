import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen,QColor
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem)
                             

# 视图（View）
# QGraphicsView提供视图部件，它可以将场景的内容可视化。
# 视图窗口部件是一个可滚动区域，它提供了用于在大型场景中导航的滚动条。
# 如果要启用OpenGL支持，可以通过调用QGraphicsView.setViewport()将QOpenGLWidget对象设置为视口。

# scene =QGraphicsScene()
# myPopulateScene(scene)
# view = QGraphicsView(scene)
# view.show()

# 视图从键盘和鼠标接收输入事件，
# 然后将其转换为场景事件（在适当的情况下将其转换为场景坐标），
# 然后再将事件发送到可视化场景

# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene
 
# def showImage(self):
 
#     frame = QImage("img/entrance1.png")
#     pix = QPixmap.fromImage(frame)
#     item = QGraphicsPixmapItem(pix)
#     scene = QGraphicsScene()
#     scene.addItem(item)
#     self.graphicsView.setScene(scene)

app = QApplication(sys.argv)
scene = QGraphicsScene()

scene.addLine(20, 20, 200, 200)
scene.addText('Test Graphics View')

scene.addRect(0, 0, 320, 240)
scene.addEllipse(100, 100, 100, 100)

rect = QGraphicsRectItem(99, 99, 102, 102)
rect.setPen(QPen(Qt.red))
scene.addItem(rect)

view = QGraphicsView(scene)
view.setWindowTitle('w0x7ce')
view.resize(480, 320)
view.show()
sys.exit(app.exec_())
