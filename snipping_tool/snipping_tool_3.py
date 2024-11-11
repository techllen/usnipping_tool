from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QTextEdit
from PyQt5.QtGui import QIcon, QImage, QPainter, QTextCursor
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5 import QtWidgets, QtGui, QtCore
import sys


class SnippingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snipping Tool')
        self.setGeometry(100, 100, 800, 600)
        self.drawing = False
        self.rect_start = QPoint()
        self.rect_end = QPoint()
        self.current_tool = None
        self.toolbar = self.addToolBar('Tools')

        # Toolbar Configuration
        self.add_toolbar_actions()

        # Text Edit for extracted text
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(QRect(10, 50, 780, 200))

        # Create canvas
        self.image = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)  # Use ARGB32 for transparency
        self.image.fill(Qt.transparent)  # Fill with transparent color

    def add_toolbar_actions(self):
        snip_action = QAction('Snip', self)
        snip_action.triggered.connect(self.snip)
        self.toolbar.addAction(snip_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        self.toolbar.addAction(save_action)

        rect_action = QAction('Rectangle', self)
        rect_action.triggered.connect(self.start_rectangle)
        self.toolbar.addAction(rect_action)

        circle_action = QAction('Circle', self)
        circle_action.triggered.connect(self.start_circle)
        self.toolbar.addAction(circle_action)

    def snip(self):
        self.snip_window = Snip()
        self.snip_window.show()

    def start_rectangle(self):
        self.current_tool = 'rectangle'

    def start_circle(self):
        self.current_tool = 'circle'

    def save_image(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG Files (*.png);;JPEG Files (*.jpeg);;All Files (*)")
        if filePath == "":
            return
        self.image.save(filePath)

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rect_start = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.rect_end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rect_end = event.pos()
            self.drawing = False
            painter = QPainter(self.image)
            if self.current_tool == 'rectangle':
                painter.drawRect(QRect(self.rect_start, self.rect_end))
            elif self.current_tool == 'circle':
                painter.drawEllipse(QRect(self.rect_start, self.rect_end))
            self.update()

    def resizeEvent(self, event):
        new_image = QImage(self.size(), QImage.Format_RGB32)
        new_image.fill(Qt.white)
        painter = QPainter(new_image)
        painter.drawImage(QPoint(), self.image)
        self.image = new_image
        super().resizeEvent(event)

class Snip(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.start, self.end = None, None

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QtGui.QPen(Qt.red, 2))
            painter.drawRect(QRect(self.start, self.end))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()

    def mouseMoveEvent(self, event):
        if self.start:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end = event.pos()
            # Capture screen logic can be added here
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingTool()
    window.show()
    sys.exit(app.exec_())