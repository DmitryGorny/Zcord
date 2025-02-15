import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget
from PyQt6.QtCore import Qt
from logic.Main.Parameters.Parameters import Ui_Parameters
from logic.Main.Voice_main.VoiceParamsClass import VoiceParamsClass


class ParamsWindow(QMainWindow):
    def __init__(self, ui, voicepr):
        super(ParamsWindow, self).__init__()

        self.ui = ui

        self.ui_pr = Ui_Parameters()
        self.ui_pr.setupUi(self)

        self.voicepr = voicepr

        self.ui_pr.OptionWidget.addWidget(self.voicepr.ui_voice_pr.settingsWrapper)

        self.ui_pr.pushButton.clicked.connect(self.show_voice_params)
        self.ui_pr.backButton.clicked.connect(self.back_into_main)

    def show_voice_params(self):
        self.ui_pr.OptionWidget.setCurrentWidget(self.voicepr.ui_voice_pr.settingsWrapper)

    def back_into_main(self):
        self.ui.stackedWidget.setCurrentIndex(0)
