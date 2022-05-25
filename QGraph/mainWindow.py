import cv2 as cv
import numpy as np
import sys
import random
# import halcon as ha
import math
# from graphicsView import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# 用于qtpixmap转换为cv图片
def Qtmap2Cvmap(qtpixmap):
    qimg = qtpixmap.toImage()
    temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
    temp_shape += (4,)
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
    result = result[..., :3]

    return result


# 用于Cvmap转换为Qtimg（注意是Qtimg而不是pixmap）
def Cvmap2Qtimg(cvimg):
    height, width, depth = cvimg.shape
    cvimg = cv.cvtColor(cvimg, cv.COLOR_BGR2RGB)
    cvimg = QImage(cvimg.data, width, height, width * depth, QImage.Format_RGB888)

    return cvimg


class MyGraphicsView(QGraphicsView):
    mouseMove = QtCore.pyqtSignal(QPoint)
    mouseClicked = QtCore.pyqtSignal(QPoint)

    def mouseMoveEvent(self, event):
        point = event.pos()
        self.mouseMove.emit(point)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = event.pos()
            self.mouseClicked.emit(point)
        super().mousePressEvent(event)


class Biao_Ding(QMainWindow):

    def __init__(self):
        super(Biao_Ding, self).__init__()
        self.distCoeffs = None
        self.cameraMatrix = None
        self.UI_init()  # 初始化UI界面
        self.initGraphicsSystem()  # 初始化graphics view系统
        self.flag = 1  # 用于判断是否在按下添加点之前进行了标定
        self.rows = 0
        self.cols = 0
        self.amounts_points = 0
        self.h = 0  # 图像列像素数量
        self.w = 0  # 图像行像素数量
        self.all_points = []  # 存放角点，用于对单个点操作
        self.all_obj_points = []  # 用于存放三维坐标
        self.flag_cali = 0  # 1表示已标定好图片
        self.img = None  # 图片
        self.pixmap = None
        self.points = None  # 保存点的数组

    def UI_init(self):
        self.setWindowTitle('标定工具')
        self.resize(1400, 900)

        # 打开图片按键的设置
        self.btn_openImage = QPushButton(self)
        self.btn_openImage.setGeometry(1280, 10, 100, 45)
        self.btn_openImage.setText('打开图片')
        self.btn_openImage.clicked.connect(self.openFile)

        # 设置网格行列按键设置
        self.label_setcr = QLabel(self)
        self.label_setcr.setGeometry(1294, 75, 100, 20)
        self.label_setcr.setText('设置网格行列')

        self.label_rows = QLabel(self)
        self.label_rows.setGeometry(1260, 98, 30, 20)
        self.label_rows.setText('行：')
        self.lineEdit_rows = QLineEdit(self)
        self.lineEdit_rows.setGeometry(1280, 100, 100, 20)

        self.label_cols = QLabel(self)
        self.label_cols.setGeometry(1260, 125, 30, 20)
        self.label_cols.setText('列：')
        self.lineEdit_cols = QLineEdit(self)
        self.lineEdit_cols.setGeometry(1280, 125, 100, 20)

        self.btn_setcr = QPushButton(self)
        self.btn_setcr.setGeometry(1305, 150, 50, 20)
        self.btn_setcr.setText('确定')
        self.btn_setcr.setObjectName('btn_setcr')

        # 开始标定按键的设置
        self.btn_calibration = QPushButton(self)
        self.btn_calibration.setGeometry(1280, 190, 100, 45)
        self.btn_calibration.setText('开始标定')
        self.btn_calibration.setObjectName('btn_calibration')

        # 添加点按键设置
        self.btn_add = QPushButton(self)
        self.btn_add.setGeometry(1280, 255, 100, 45)
        self.btn_add.setText('添加点')
        self.btn_add.setObjectName('btn_add')
        self.btn_add.setCheckable(True)

        # 删除点按键设置
        self.btn_delete = QPushButton(self)
        self.btn_delete.setGeometry(1280, 320, 100, 45)
        self.btn_delete.setText('删除点')
        self.btn_delete.setObjectName('btn_delete')

        # 生成校正文件按键设置
        self.btn_adjust = QPushButton(self)
        self.btn_adjust.setGeometry(1280, 385, 100, 45)
        self.btn_adjust.setText('生成校正文件')
        self.btn_adjust.setObjectName('btn_adjust')

        # 校畸变按钮
        self.btn_calibration_distortion = QPushButton(self)
        self.btn_calibration_distortion.setGeometry(1280, 450, 100, 45)
        self.btn_calibration_distortion.setText('纠正图像')
        self.btn_calibration_distortion.setEnabled(False)
        self.btn_calibration_distortion.setObjectName('btn_calibration_distortion')

        # 清空GV系统按键设置
        self.btn_clear = QPushButton(self)
        self.btn_clear.setGeometry(1280, 660, 100, 45)
        self.btn_clear.setText('重置屏幕')
        self.btn_clear.setObjectName('btn_clear')

        # 设置标签显示坐标
        # 先设置状态栏
        # statusBar = QStatusBar(self)
        # self.setStatusBar(statusBar)
        # # 再设置标签
        self.label_coordinate = QLabel(self)
        self.label_coordinate.setGeometry(1180, 850, 200, 30)
        # self.label_coordinate.setMinimumWidth(100)
        # # 将标签加入到状态栏中
        # statusBar.addWidget(self.label_coordinate)

        # 中间工作区
        centralWidget = QWidget(self)
        centralWidget.setGeometry(0, 0, 1250, 850)
        # 绘图视图
        self.view = MyGraphicsView(centralWidget)
        self.view.setCursor(Qt.CrossCursor)  # 设置在GV里的鼠标样式
        self.view.setMouseTracking(True)
        self.view.mouseMove.connect(self.do_mouseMovePoint)

        QtCore.QMetaObject.connectSlotsByName(self)

    # 设置点显示在图片上
    def setItemProperties(self, item):
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(item)
        item.setSelected(False)

    # 初始化Graphics View系统
    def initGraphicsSystem(self):
        rect = QRectF(0, 0, 1240, 800)  # 显示图片的区域，不是GV的区域，前面两个要0，0，否则图片显示不完全
        self.scene = QGraphicsScene(rect)
        self.view.setScene(self.scene)

    # 打开图片
    def openFile(self):
        self.img_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '.', '图像文件(*.jpg *.pnQt *.bmp *.png)')
        if self.img_path:
            self.img = QImage(self.img_path)
            if self.img.width() > 1240 or self.img.height() > 800:
                self.scale = 0.2  # 之后坐标除以0.2即可得到真实坐标
            else:
                self.scale = 1
            mgnWidth = int(self.img.width() * self.scale)
            mgnHeight = int(self.img.height() * self.scale)  # 缩放宽高尺寸
            size = QSize(mgnWidth, mgnHeight)
            self.pixmap = QPixmap.fromImage(self.img.scaled(size, Qt.IgnoreAspectRatio))
            self.item = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.item)
            self.view.setScene(self.scene)
            self.view.show()
            self.btn_openImage.setEnabled(False)

    # 设置行列
    @pyqtSlot()
    def on_btn_setcr_clicked(self):
        self.rows = self.lineEdit_rows.text()
        self.cols = self.lineEdit_cols.text()
        if int(self.rows) == 0 or int(self.cols) == 0:
            QMessageBox.warning(self, '错误', '请输入正整数')
        try:
            self.amounts_points = int(self.rows) * int(self.cols)
        except ValueError:
            QMessageBox.warning(self, '错误', '请输入正整数')
        if self.amounts_points:
            self.rows = int(self.rows)
            self.cols = int(self.cols)
            QMessageBox.information(self, '完成', '设置完成')

    # 标定
    @pyqtSlot()
    def on_btn_calibration_clicked(self):
        if self.img == None or self.cols == 0 or self.rows == 0 or self.amounts_points == 0:
            QMessageBox.warning(self, '错误', '未打开图片或未设置行列')
        else:
            Row, Column = self.image_preprocessing()
            self.points = np.zeros((0, 1, 2), dtype=np.float32)
            for i in range(len(Row)):
                if Column[i] != 0:
                    self.points = np.append(self.points, [[[Column[i], Row[i]]]], 0)
            for i in range(len(self.points)):
                item = QGraphicsEllipseItem(- 3,
                                            - 3, 6, 6)
                item.setBrush(Qt.red)
                item.setPos(self.points[i][0][0] * self.scale,
                            self.points[i][0][1] * self.scale)
                self.setItemProperties(item)
            self.all_points.append(self.points)
            self.btn_calibration.setEnabled(False)

    # 添加点
    def do_mouseClicked(self, point):
        item = QGraphicsEllipseItem(- 3, - 3, 6, 6)
        item.setBrush(QBrush(Qt.red))
        item.setPos(point.x(),
                    point.y())
        self.points = np.append(self.points, [[[point.x() / self.scale, point.y() / self.scale]]], 0)
        self.setItemProperties(item)

    # 添加点前设置
    @pyqtSlot(bool)
    def on_btn_add_clicked(self, checked):
        if checked:
            if self.all_points:
                self.btn_delete.setEnabled(False)
                self.btn_calibration.setEnabled(False)
                self.btn_calibration.setEnabled(False)
                self.flag = 1
                self.view.mouseClicked.connect(self.do_mouseClicked)
            else:
                self.flag = 0
                self.btn_add.setChecked(False)
                QMessageBox.warning(self, '警告', '请先进行图像标定')
        else:
            if self.flag == 1:
                self.btn_delete.setEnabled(True)
                self.btn_calibration.setEnabled(True)
                self.btn_calibration.setEnabled(False)
                self.view.mouseClicked.disconnect(self.do_mouseClicked)

    # 删除点
    @pyqtSlot()
    def on_btn_delete_clicked(self):
        if not self.all_points:
            QMessageBox.warning(self, "警告", "请先进行图像标定")
        else:
            delete_amounts = 0
            items = self.scene.selectedItems()
            count = len(items)
            count_points = len(self.points)
            for i in range(count):
                item = items[i]
                for j in range(count_points):
                    if j >= count_points - delete_amounts:
                        break
                    elif abs(item.scenePos().x() / self.scale - self.points[j][0][0]) < 5 and abs(
                            item.scenePos().y() / self.scale - self.points[j][0][1]) < 5:
                        self.points = np.delete(self.points, j, axis=0)
                        delete_amounts = delete_amounts + 1
                self.scene.removeItem(item)

    # 生成校正文件
    @pyqtSlot()
    def on_btn_adjust_clicked(self):
        if self.all_points and len(self.points) == self.amounts_points:
            cvImage = cv.imread(self.img_path)
            cvImage = cv.cvtColor(cvImage, cv.COLOR_BGR2GRAY)
            self.points = self.points.astype(np.float32)

            obj_points = np.zeros((self.amounts_points, 3), np.float32)
            obj_points[:, :2] = np.mgrid[0:self.cols, 0:self.rows].T.reshape(-1, 2)
            obj_points = np.reshape(obj_points, (self.amounts_points, 1, 3))
            self.all_obj_points.append(obj_points)

            self.points = self.sort_points(self.points)
            self.all_points.clear()
            self.all_points.append(self.points)
            self.h, self.w = cvImage.shape[:2]
            _, self.cameraMatrix, self.distCoeffs, self.rvecs, self.tvecs = cv.calibrateCamera(self.all_obj_points,
                                                                                               self.all_points,
                                                                                               (self.w, self.h),
                                                                                               None,
                                                                                               None)
            self.flag_cali = 1
            self.btn_calibration_distortion.setEnabled(True)
            QMessageBox.information(self, '完成', '生成完成')
        else:
            QMessageBox.warning(self, '警告', '未进行图像标定或未添加足够的点')

    # 矫正畸变
    @pyqtSlot()
    def on_btn_calibration_distortion_clicked(self):
        if self.img_path and self.flag_cali == 1:
            self.cvImg = cv.imread(self.img_path)
            src_img_revise = cv.undistort(self.cvImg, self.cameraMatrix, self.distCoeffs, newCameraMatrix=None)
            scale_img_revise = cv.resize(src_img_revise, dsize=None, fy=0.2, fx=0.2)

            scale_qtimg_revise = Cvmap2Qtimg(scale_img_revise)
            scale_qtpixmap_revise = QPixmap.fromImage(scale_qtimg_revise)
            item = QGraphicsPixmapItem(scale_qtpixmap_revise)
            self.scene.addItem(item)
            self.view.setScene(self.scene)
            self.view.show()

            self.btn_add.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_calibration.setEnabled(False)

            # # 测试用
            # img_copy = self.cvImg.copy()
            # img_points_save = cv.drawChessboardCorners(img_copy, (self.cols, self.rows), self.points, True)
            # cv.imwrite('E:/CVproject/pictures/points.jpg', img_points_save)
            # total_error = 0
            # for i in range(len(self.all_obj_points)):
            #     imgpoints2, _ = cv.projectPoints(self.all_obj_points[i], self.rvecs[i], self.tvecs[i],
            #                                      self.cameraMatrix, self.distCoeffs)
            #     error = cv.norm(self.all_points[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
            #     total_error += error
            # print("total error: ", total_error / len(self.all_obj_points))
        else:
            QMessageBox.warning(self, '提示', '请先标定图片')

    # 鼠标移动
    def do_mouseMovePoint(self, point):
        if self.img:
            self.label_coordinate.setText("坐标(x, y)：%d,%d" % (int(point.x() / self.scale), int(point.y() / self.scale)))

    # 清空屏幕
    @pyqtSlot()
    def on_btn_clear_clicked(self):
        self.initGraphicsSystem()
        self.btn_openImage.setEnabled(True)
        self.btn_calibration.setEnabled(True)
        self.flag = 1
        self.rows = 0
        self.cols = 0
        self.amounts_points = 0
        self.h = 0
        self.w = 0
        self.all_points = []
        self.all_obj_points = []
        self.flag_cali = 0
        self.img = None
        self.pixmap = None
        self.points = None

    # 给标志点排序
    def sort_points(self, point):
        counts = int(np.size(point) / 2)
        for i in range(1, counts):
            for j in range(1, counts - i + 1):
                if point[j - 1][0][1] > point[j][0][1]:
                    point[j - 1][0][1], point[j][0][1] = point[j][0][1], point[j - 1][0][1]
                    point[j - 1][0][0], point[j][0][0] = point[j][0][0], point[j - 1][0][0]
        for i in range(1, counts):
            for j in range(1, counts - i + 1):
                if point[j - 1][0][0] > point[j][0][0] and (abs(point[j][0][1] - point[j - 1][0][1]) < 90):
                    point[j - 1][0][1], point[j][0][1] = point[j][0][1], point[j - 1][0][1]
                    point[j - 1][0][0], point[j][0][0] = point[j][0][0], point[j - 1][0][0]
        return point

    # 图片预处理
    def image_preprocessing(self):
            image = ha.read_image(self.img_path)
            gray_image = ha.rgb1_to_gray(image)

            Rectangle = ha.gen_rectangle1(200, 300, 3400, 4900)
            ImageReduced = ha.reduce_domain(gray_image, Rectangle)

            MaxLineWidth = 8
            Contrast = [12]
            Contrast.append(0)
            Sigma, Low, High = self.calculate_lines_gauss_parameters(MaxLineWidth, Contrast)
            Lines = ha.lines_gauss(ImageReduced, Sigma, Low, High, 'dark', 'true', 'parabolic', 'true')

            UnionContours = ha.union_collinear_contours_xld(Lines, 18, 0.1, 18, 0.1, 'attr_keep')
            SelectedContours2 = ha.select_contours_xld(UnionContours, 'contour_length', 185, 99999, -0.5, 0.5)
            UnionContours2 = ha.union_collinear_contours_xld(SelectedContours2, 800, 1, 800, 0.1, 'attr_keep')
            SelectedContours3 = ha.select_contours_xld(UnionContours2, 'contour_length', 2000, 99999, -0.5, 0.5)
            ContoursSplit = ha.segment_contours_xld(SelectedContours3, 'lines_circles', 5, 4, 2)
            SelectedContours3 = ha.select_contours_xld(ContoursSplit, 'contour_length', 90, 99999, -0.5, 0.5)
            UnionContours5 = ha.union_collinear_contours_xld(SelectedContours3, 350, 1, 350, 0.2, 'attr_keep')
            Region = ha.gen_region_contour_xld(UnionContours5, 'filled')

            RegionOpening1 = ha.opening_rectangle1(Region, 1, 10)
            RegionDilation1 = ha.dilation_rectangle1(RegionOpening1, 1, 500)

            RegionOpening2 = ha.opening_rectangle1(Region, 10, 1)
            RegionDilation2 = ha.dilation_rectangle1(RegionOpening2, 500, 1)

            RegionIntersection = ha.intersection(RegionDilation1, RegionDilation2)
            ConnectedRegions = ha.connection(RegionIntersection)
            Area, Row, Column = ha.area_center(ConnectedRegions)

            return Row, Column

    # 计算高斯线参数
    def calculate_lines_gauss_parameters(self, MaxLineWidth, Contrast):
        ContrastHigh = Contrast[0]
        if len(Contrast) == 2:
            ContrastLow = Contrast[1]
        else:
            ContrastLow = ContrastHigh / 3.0
        if MaxLineWidth < math.sqrt(3.0):
            ContrastLow = ContrastLow * MaxLineWidth / math.sqrt(3.0)
            ContrastHigh = ContrastHigh * MaxLineWidth / math.sqrt(3.0)
            MaxLineWidth = math.sqrt(3.0)
        HalfWidth = MaxLineWidth / 2.0
        Sigma = HalfWidth / math.sqrt(3.0)
        Help = -2.0 * HalfWidth / (math.sqrt(6.283185307178) * pow(Sigma, 3.0)) * math.exp(-0.5 * pow(HalfWidth / Sigma, 2.0))
        High = math.fabs(ContrastHigh * Help)
        Low = math.fabs(ContrastLow * Help)
        return Sigma, Low, High


if __name__ == "__main__":
    app = QApplication(sys.argv)
    biaoding = Biao_Ding()
    biaoding.show()
    sys.exit(app.exec_())