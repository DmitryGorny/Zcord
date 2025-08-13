from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QConicalGradient, QBrush, QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget


class AnimatedBorderButton(QWidget):
    def __init__(self, parent_button):
        super().__init__(parent_button.parent())
        self.button = parent_button
        self.setGeometry(self.button.geometry())
        self._offset = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_animation)
        self._timer.start(32)  # Скорость анимации

        self.show()

    def update_animation(self):
        self._offset = (self._offset + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Градиент "змейка" по окружности
        gradient = QConicalGradient(self.width() / 2, self.height() / 2, self._offset)
        gradient.setColorAt(0.0, QColor("#3ba55d"))  # Ярко-зелёный
        gradient.setColorAt(0.1, QColor("#3ba55d"))
        gradient.setColorAt(0.2, QColor("#3ba55d"))
        gradient.setColorAt(0.3, QColor("#3ba55d"))
        gradient.setColorAt(0.4, QColor("#3ba55d"))
        gradient.setColorAt(0.5, QColor(0, 255, 0, 0))
        gradient.setColorAt(0.6, QColor(0, 255, 0, 0))  # Полностью прозрачный
        gradient.setColorAt(0.7, QColor(0, 255, 0, 0))
        gradient.setColorAt(0.8, QColor(0, 255, 0, 0))
        gradient.setColorAt(0.9, QColor("#3ba55d"))
        gradient.setColorAt(1.0, QColor("#3ba55d"))  # Замыкается в зелёный

        pen = QPen(QBrush(gradient), 3)  # Толщина границы
        painter.setPen(pen)
        painter.setBrush(QBrush())
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)  # Коррекция размеров

    def start_animation(self):
        self._timer.start(32)

    def stop_animation(self):
        self._offset = 0
        self._timer.stop()
        self.update()
        self.hide()
