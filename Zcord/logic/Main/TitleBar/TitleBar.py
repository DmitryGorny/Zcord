from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor, QPainter
from PyQt6.QtWidgets import QLabel
from qframelesswindow import TitleBar

from logic.Main.TitleBar.TitleBarQt import Ui_Form


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        #self.window().windowIconChanged.connect(self.setIcon)
        self.bg_color = QColor("black")

        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: grey;
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: grey;
            }
        """)

        self.closeBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: grey;
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: grey;
            }
        """)

        self.minBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: grey;
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: grey;
            }
        """)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.titleLabel.setStyleSheet("""
        font-size:18px;
        color:white;
        """)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    #def setIcon(self, icon):
        #self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        super().paintEvent(event)
