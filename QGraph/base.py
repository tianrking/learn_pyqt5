import sys
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView)


app = QApplication(sys.argv)

scene = QGraphicsScene()
scene.addText("Hello, world!")

view = QGraphicsView(scene)
view.show()

sys.exit(app.exec_())