from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import pytesseract
from PIL import Image

class SnippingTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.start, self.end = None, None
        self.shape = None  # Track current shape

    def mousePressEvent(self, event):
        self.start = event.pos()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.capture_screen()
        self.close()

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
            rect = QtCore.QRect(self.start, self.end)
            if self.shape == 'rectangle':
                painter.drawRect(rect)
            elif self.shape == 'circle':
                painter.drawEllipse(rect)

    def capture_screen(self):
        if not self.start or not self.end:
            return  # Safety check if coordinates are not set
        x1 = min(self.start.x(), self.end.x())
        y1 = min(self.start.y(), self.end.y())
        x2 = max(self.start.x(), self.end.x())
        y2 = max(self.start.y(), self.end.y())
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, x1, y1, x2 - x1, y2 - y1)
        screenshot.save("screenshot.png", "png")
        self.extract_text_from_image("screenshot.png")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:  # C for Circle
            self.shape = 'circle'
        elif event.key() == QtCore.Qt.Key_R:  # R for Rectangle
            self.shape = 'rectangle'
        elif event.key() == QtCore.Qt.Key_Escape:  # Exit on Escape
            self.close()
        self.update()

    def extract_text_from_image(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        print("Extracted Text:", text)
        return text

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SnippingTool()
    window.show()
    sys.exit(app.exec_())