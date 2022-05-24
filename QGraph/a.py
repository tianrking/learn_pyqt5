import sys
from PyQt5.QtWidgets import QApplication,QGraphicsView,QGraphicsScene,QGraphicsEllipseItem
from PyQt5.QtCore import Qt,QPointF


class MovingObject(QGraphicsEllipseItem):
    def __init__(self,x,y,r):
        super().__init__(0,0,r,r*1)
        self.setPos(x,y)
        self.setBrush(Qt.green)
        self.setAcceptHoverEvents(True)
    
    def hoverEnterEvent(self, event) :
        app.instance().setOverrideCursor(Qt.OpenHandCursor)
    
    def hoverEnterEvent(self, event) :
        app.instance().restoreOverrideCursor()
        
    def mousePressEvent(self, event) :
        pass
    
    def mouseMoveEvent(self, event) :
        orig_cursor_position = event.lastScenePos()
        update_cursor_position = event.scenePos()
        
        orig_position = self.scenePos()
        
        update_cursor_x = update_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        update_cursor_y = update_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        
        self.setPos(QPointF(update_cursor_x,update_cursor_y))
    
        
    def mouseReleaseEvent(self, event) :
        print('x:{0},y:{1}'.format(self.pos().x(),self.pos().y()))
        
        
        
        
        
class GraphicView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0,0,1200,1400)
        
        self.movObject = MovingObject(50,50,40)
        # self.movObject2 = MovingObject(100,150,80)
        self.scene.addItem(self.movObject)
        # self.scene.addItem(self.movObject2) 

app = QApplication(sys.argv)

view = GraphicView()
view.show()

sys.exit(app.exec_())