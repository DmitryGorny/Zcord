import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# Разрешаем незащищённые источники (HTTP с IP)
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--unsafely-treat-insecure-origin-as-secure=http://26.36.124.241:8080 "
    "--ignore-certificate-errors "
    "--autoplay-policy=no-user-gesture-required"
)

class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Видео-конференция")
        self.layout = QVBoxLayout(self)
        self.btn = QPushButton("Подключиться к комнате")
        self.btn.clicked.connect(self.add_room)
        self.layout.addWidget(self.btn)
        self.views = []

    def add_room(self):
        room_id = "100"  # например, можно потом делать prompt()
        view = QWebEngineView()
        url = f"http://26.36.124.241:8080/"
        view.load(QUrl(url))
        self.layout.addWidget(view)
        self.views.append(view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoApp()
    w.show()
    sys.exit(app.exec())
