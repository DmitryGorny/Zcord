import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

# Windows API
user32 = ctypes.windll.user32

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet("background: #333; color: white; font-size: 14px;")

        layout = QVBoxLayout()
        self.label = QLabel("Custom TitleBar", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.startPos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            delta = event.globalPosition().toPoint() - self.startPos
            self.window().move(self.window().pos() + delta)
            self.startPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = None
            self.window().checkSnap()

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(400, 300)

        self.titleBar = CustomTitleBar(self)
        self.centralWidget = QWidget(self)
        self.centralWidget.setStyleSheet("background: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titleBar)
        layout.addWidget(self.centralWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def event(self, event):
        """ Безопасная обработка системных событий (без nativeEvent) """
        if event.type() == 174:  # 174 = Windows WM_NCHITTEST
            cursor_pos = self.mapFromGlobal(QPoint(QApplication.instance().cursor().pos()))
            if cursor_pos.y() <= self.titleBar.height():
                return True  # Заголовок - можно двигать окно
        return super().event(event)

    def checkSnap(self):
        """ Проверяет AeroSnap и привязывает окно """
        try:
            monitor_info = ctypes.create_string_buffer(40)
            ctypes.memset(monitor_info, 0, 40)

            hMonitor = user32.MonitorFromWindow(int(self.winId()), 1)
            if not hMonitor:
                print("MonitorFromWindow failed")
                return

            if user32.GetMonitorInfoW(hMonitor, monitor_info):
                rect = ctypes.cast(monitor_info, ctypes.POINTER(ctypes.c_int * 4)).contents
                x, y, w, h = rect[0], rect[1], rect[2], rect[3]

                win_x, win_y = self.pos().x(), self.pos().y()
                win_w, win_h = self.width(), self.height()

                if win_x <= x + 10:  # Левый край
                    self.setGeometry(x, y, w // 2, h)
                elif win_x + win_w >= w - 10:  # Правый край
                    self.setGeometry(w // 2, y, w // 2, h)
                elif win_y <= y + 10:  # Верхний край
                    self.setGeometry(x, y, w, h // 2)
        except Exception as e:
            print(f"Error in checkSnap: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomMainWindow()
    window.show()
    sys.exit(app.exec())
