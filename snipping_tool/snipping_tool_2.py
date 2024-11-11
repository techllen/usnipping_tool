import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QFileDialog, QTextEdit
from PyQt5.QtGui import QIcon, QImage, QPainter, QTextCursor
from PyQt5.QtCore import Qt, QRect, QPoint
from snipping_tool import SnippingTool


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
        self.current_tool = None  # Initialize current_tool
        self.toolbar = self.addToolBar('Tools')

        # Toolbar Configuration
        self.add_toolbar_actions()

        # Text Edit for extracted text
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(QRect(10, 50, 780, 200))

        # Create canvas
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

    def add_toolbar_actions(self):

        # Add a button to snip images
        snip_action = QAction(QIcon.fromTheme('document-camera'), 'Snip', self)
        snip_action.triggered.connect(self.snip)
        self.toolbar.addAction(snip_action)

        # Add a button to save the snipped image
        save_action = QAction(QIcon.fromTheme('document-save'), 'Save', self)
        save_action.triggered.connect(self.save_image)
        self.toolbar.addAction(save_action)

        # Add a button to draw rectangle
        rect_action = QAction(QIcon.fromTheme('draw-rectangle'), 'Rectangle', self)
        rect_action.triggered.connect(self.start_rectangle)
        self.toolbar.addAction(rect_action)

        # Add a button to draw circle
        circle_action = QAction(QIcon.fromTheme('draw-circle'), 'Circle', self)
        circle_action.triggered.connect(self.start_circle)
        self.toolbar.addAction(circle_action)

        # Add a button to resize text
        resize_text_action = QAction(QIcon.fromTheme('format-text-size'), 'Resize Text', self)
        resize_text_action.triggered.connect(self.resize_text)
        self.toolbar.addAction(resize_text_action)

        # Add a button to highlight text
        highlight_text_action = QAction(QIcon.fromTheme('format-fill-color'), 'Highlight Text', self)
        highlight_text_action.triggered.connect(self.highlight_text)
        self.toolbar.addAction(highlight_text_action)

    def snip(self):
        pass

    def start_rectangle(self):
        self.current_tool = 'rectangle'

    def start_circle(self):
        self.current_tool = 'circle'

    def resize_text(self):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.Document)
        fmt = cursor.charFormat()
        fmt.setFontPointSize(16)
        cursor.setCharFormat(fmt)

    def highlight_text(self):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        fmt = cursor.charFormat()
        fmt.setBackground(Qt.yellow)
        cursor.setCharFormat(fmt)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingTool()
    window.show()
    sys.exit(app.exec_())