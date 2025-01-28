from logic.Main.Voice_main.VoiceParameters import Ui_VoiceParams
from PyQt6 import QtWidgets, QtCore
from logic.Voice import audio_send


class VoiceParamsClass(QtWidgets.QWidget):
    def __init__(self):
        super(VoiceParamsClass, self).__init__()

        self.ui = Ui_VoiceParams()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.call_noise_profile)

    def call_noise_profile(self):
        audio_send.listen_noise()
