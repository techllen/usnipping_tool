from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QTextEdit, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QImage, QPainter, QTextCursor, QPalette, QColor, QPixmap, QClipboard
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
import sys
from pytesseract import pytesseract


class SnippingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snipping Tool')
        self.setGeometry(50, 50, 400, 300)

        # Add QLabel to display image
        self.image_label = QLabel(self)
        self.image_label.setGeometry(20, 50, 360, 200)  # Adjust size and position as needed

        # Toolbar
        self.toolbar = self.addToolBar('Tools')

        # Toolbar Configuration
        self.add_toolbar_actions()

        # Snipped image dimensions
        self.width_snipped, self.height_snipped = 0, 0

    def add_toolbar_actions(self):
        snip_action = QAction('Snip', self)
        snip_action.triggered.connect(self.snip)
        self.toolbar.addAction(snip_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        self.toolbar.addAction(save_action)

        extract_text_action = QAction('Extract Texts From Image', self)
        extract_text_action.triggered.connect(self.extract_text_from_image)
        self.toolbar.addAction(extract_text_action)

    def snip(self):
        self.snip_window = Snip(self)  # Pass the main window reference
        self.snip_window.show()

    def save_image(self):
        image = Image.open('/home/matare/app_development/snipping_tool/screenshot.png')

        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG Files (*.png);;JPEG Files (*.jpeg);;All Files (*)")
        if filePath == "":
            return

        # Ensure the filePath has a correct extension
        if not filePath.lower().endswith(('.png', '.jpeg', '.jpg')):
            filePath += '.png'  # Default to PNG if no extension is provided

        # Save the image
        image.save(filePath)

    def extract_text_from_image(self):
        image = Image.open('/home/matare/app_development/snipping_tool/screenshot.png')
        text = pytesseract.image_to_string(image)
        print("Extracted Text:", text)

        # Show extracted text in a new window
        self.show_extracted_text_window(text)

        # Copy the extracted text to clipboard
        self.copy_to_clipboard(text)

    def show_extracted_text_window(self, text):
        self.extracted_text_from_an_image_window = ExtractedTextFromAnImageWindow(text)
        self.extracted_text_from_an_image_window.show()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)  # Copy extracted text to clipboard

    def resize_window(self, w, h):
        self.setGeometry(50, 50, w + 40, h + 70)  # Resize the main window

    def update_image_display(self, image_path):
        # Load and display the image in QLabel
        pixmap = QPixmap(image_path)
        # Resize the QLabel to match the image size
        self.image_label.resize(pixmap.width(), pixmap.height())
        # Set the pixmap to the QLabel
        self.image_label.setPixmap(pixmap)


class Snip(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Store the reference to main window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowOpacity(0.05)
        self.start, self.end = None, None

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QtGui.QPen(Qt.red, 3))
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
            self.capture_screen()
            self.load_image()
            self.main_window.resize_window(self.width_snipped, self.height_snipped)  # Use resize_window method
            self.main_window.update_image_display(
                "/home/matare/app_development/snipping_tool/screenshot.png")  # Update image display
            self.close()

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

    def load_image(self):
        # Open an image file
        image = Image.open("/home/matare/app_development/snipping_tool/screenshot.png")  # Replace with your image path
        # Get the size of the image
        self.width_snipped, self.height_snipped = image.size

class ExtractedTextFromAnImageWindow(QWidget):
    def __init__(self, text):
        super().__init__()
        text_window = QWidget(self)  # Set the parent to maintain reference
        text_window.setWindowTitle('Extracted Text')
        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setText(text)  # Set the extracted text
        text_edit.setReadOnly(True)  # Make the QTextEdit read-only
        layout.addWidget(text_edit)

        text_window.setLayout(layout)
        self.adjust_window_size(text, text_window)  # Adjust the window size based on text length
        text_window.show()  # Ensure the window is shown properly

    def adjust_window_size(self, text, text_window):
        # Calculate number of lines or characters
        num_lines = text.count("\n") + 1
        num_chars = len(text)

        # Adjust window size based on the number of lines and characters
        height = max(300, num_lines * 25)  # Set minimum height to 300, adjust height based on number of lines
        width = min(600, max(400, num_chars * 0.5))  # Adjust width based on number of characters, with a minimum and maximum limit

        text_window.resize(int(width), int(height))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingTool()
    window.show()
    sys.exit(app.exec_())

# class SnippingTool(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('Snipping Tool')
#         self.setGeometry(50, 50, 400, 300)
#
#         # Add QLabel to display image
#         self.image_label = QLabel(self)
#         self.image_label.setGeometry(20, 50, 360, 200)  # Adjust size and position as needed
#
#         # Toolbar
#         self.toolbar = self.addToolBar('Tools')
#
#         # Toolbar Configuration
#         self.add_toolbar_actions()
#
#         # Snipped image dimensions
#         self.width_snipped, self.height_snipped = 0, 0
#
#     def add_toolbar_actions(self):
#         snip_action = QAction('Snip', self)
#         snip_action.triggered.connect(self.snip)
#         self.toolbar.addAction(snip_action)
#
#         save_action = QAction('Save', self)
#         save_action.triggered.connect(self.save_image)
#         self.toolbar.addAction(save_action)
#
#         extract_text_action = QAction('Extract Texts From Image', self)
#         extract_text_action.triggered.connect(self.extract_text_from_image)
#         self.toolbar.addAction(extract_text_action)
#
#     def snip(self):
#         self.snip_window = Snip(self)  # Pass the main window reference
#         self.snip_window.show()
#
#     def save_image(self):
#         image = Image.open('/home/matare/app_development/snipping_tool/screenshot.png')
#
#         filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
#                                                   "PNG Files (*.png);;JPEG Files (*.jpeg);;All Files (*)")
#         if filePath == "":
#             return
#
#         # Ensure the filePath has a correct extension
#         if not filePath.lower().endswith(('.png', '.jpeg', '.jpg')):
#             filePath += '.png'  # Default to PNG if no extension is provided
#
#         # Save the image
#         image.save(filePath)
#
#     def extract_text_from_image(self, image_path):
#         image = Image.open('/home/matare/app_development/snipping_tool/screenshot.png')
#         text = pytesseract.image_to_string(image)
#         print("Extracted Text:", text)
#
#         # Show extracted text in a new window
#         self.show_extracted_text_window(text)
#
#         # Copy the extracted text to clipboard
#         self.copy_to_clipboard(text)
#
#     def show_extracted_text_window(self, text):
#         # Create a new window to show extracted text
#         text_window = QWidget()
#         text_window.setWindowTitle('Extracted Text')
#         layout = QVBoxLayout()
#
#         text_edit = QTextEdit()
#         text_edit.setText(text)  # Set the extracted text
#         text_edit.setReadOnly(True)  # Make the QTextEdit read-only
#         layout.addWidget(text_edit)
#
#         text_window.setLayout(layout)
#         text_window.resize(400, 300)
#         text_window.show()
#
#     def copy_to_clipboard(self, text):
#         clipboard = QApplication.clipboard()
#         clipboard.setText(text)  # Copy extracted text to clipboard
#
#     def resize_window(self, w, h):
#         self.setGeometry(50, 50, w + 40, h + 70)  # Resize the main window
#
#     def update_image_display(self, image_path):
#         # Load and display the image in QLabel
#         pixmap = QPixmap(image_path)
#         # Resize the QLabel to match the image size
#         self.image_label.resize(pixmap.width(), pixmap.height())
#         # Set the pixmap to the QLabel
#         self.image_label.setPixmap(pixmap)
#
# class Snip(QtWidgets.QWidget):
#     def __init__(self, main_window):
#         super().__init__()
#         self.main_window = main_window  # Store the reference to main window
#         self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
#         self.setWindowState(QtCore.Qt.WindowFullScreen)
#         self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
#         self.setWindowOpacity(0.05)
#         self.start, self.end = None, None
#
#     def paintEvent(self, event):
#         if self.start and self.end:
#             painter = QPainter(self)
#             painter.setPen(QtGui.QPen(Qt.red, 3))
#             painter.drawRect(QRect(self.start, self.end))
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.start = event.pos()
#
#     def mouseMoveEvent(self, event):
#         if self.start:
#             self.end = event.pos()
#             self.update()
#
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.end = event.pos()
#             self.capture_screen()
#             self.load_image()
#             self.main_window.resize_window(self.width_snipped, self.height_snipped)  # Use resize_window method
#             self.main_window.update_image_display("/home/matare/app_development/snipping_tool/screenshot.png")  # Update image display
#             self.close()
#
#     def capture_screen(self):
#         if not self.start or not self.end:
#             return  # Safety check if coordinates are not set
#         x1 = min(self.start.x(), self.end.x())
#         y1 = min(self.start.y(), self.end.y())
#         x2 = max(self.start.x(), self.end.x())
#         y2 = max(self.start.y(), self.end.y())
#         screen = QtWidgets.QApplication.primaryScreen()
#         screenshot = screen.grabWindow(0, x1, y1, x2 - x1, y2 - y1)
#         screenshot.save("screenshot.png", "png")
#
#     def load_image(self):
#         # Open an image file
#         image = Image.open("/home/matare/app_development/snipping_tool/screenshot.png")  # Replace with your image path
#         # Get the size of the image
#         self.width_snipped, self.height_snipped = image.size
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = SnippingTool()
#     window.show()
#     sys.exit(app.exec_())


# class SnippingTool(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('Snipping Tool')
#         self.setGeometry(50, 50, 400, 300)
#
#         # Toolbar
#         self.toolbar = self.addToolBar('Tools')
#
#         # Toolbar Configuration
#         self.add_toolbar_actions()
#
#         # Snipped image dimensions
#         self.width_snipped, self.height_snipped = 0, 0
#
#     def add_toolbar_actions(self):
#         snip_action = QAction('Snip', self)
#         snip_action.triggered.connect(self.snip)
#         self.toolbar.addAction(snip_action)
#
#     def snip(self):
#         self.snip_window = Snip(self)  # Pass the main window reference
#         self.snip_window.show()
#
#     def resize_window(self, w, h):
#         self.setGeometry(50, 50, w + 20, h + 20)  # Resize the main window
#
#
# class Snip(QtWidgets.QWidget):
#     def __init__(self, main_window):
#         super().__init__()
#         self.main_window = main_window  # Store the reference to main window
#         self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
#         self.setWindowState(QtCore.Qt.WindowFullScreen)
#         self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
#         self.setWindowOpacity(0.05)
#         self.start, self.end = None, None
#
#     def paintEvent(self, event):
#         if self.start and self.end:
#             painter = QPainter(self)
#             painter.setPen(QtGui.QPen(Qt.red, 3))
#             painter.drawRect(QRect(self.start, self.end))
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.start = event.pos()
#
#     def mouseMoveEvent(self, event):
#         if self.start:
#             self.end = event.pos()
#             self.update()
#
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.end = event.pos()
#             self.capture_screen()
#             self.load_image()
#             self.main_window.resize_window(self.width_snipped, self.height_snipped)  # Use resize_window method
#             self.close()
#
#     def capture_screen(self):
#         if not self.start or not self.end:
#             return  # Safety check if coordinates are not set
#         x1 = min(self.start.x(), self.end.x())
#         y1 = min(self.start.y(), self.end.y())
#         x2 = max(self.start.x(), self.end.x())
#         y2 = max(self.start.y(), self.end.y())
#         screen = QtWidgets.QApplication.primaryScreen()
#         screenshot = screen.grabWindow(0, x1, y1, x2 - x1, y2 - y1)
#         screenshot.save("screenshot.png", "png")
#
#     def load_image(self):
#         # Open an image file
#         image = Image.open("/home/matare/app_development/snipping_tool/screenshot.png")  # Replace with your image path
#         # Get the size of the image
#         self.width_snipped, self.height_snipped = image.size
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = SnippingTool()
#     window.show()
#     sys.exit(app.exec_())