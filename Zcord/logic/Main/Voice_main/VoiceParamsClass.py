from logic.Main.Voice_main.VoiceParameters import Ui_VoiceParams
from PyQt6 import QtWidgets, QtCore
from logic.Voice import audio_send
import threading


class VoiceParamsClass(QtWidgets.QWidget):
    def __init__(self):
        super(VoiceParamsClass, self).__init__()

        self.ui_voice_pr = Ui_VoiceParams()
        self.ui_voice_pr.setupUi(self)
        self.ui_voice_pr.pushButton.clicked.connect(self.call_noise_profile)
        self.ui_voice_pr.VolumeOfMicSlider.valueChanged.connect(self.change_voice_volume)
        self.ui_voice_pr.VolumeCheckWithNoiseReduceSlider.setEnabled(False)
        self.ui_voice_pr.pushButton_2.clicked.connect(self.check_mic_volume)
        self.is_check_volume = False
        self.is_noise_down = False
        self.thread = None
        self.thread1 = None

    def call_noise_profile(self):
        if not self.is_noise_down:
            self.thread1 = threading.Thread(target=audio_send.listen_noise)
            self.thread1.start()
            self.is_noise_down = True
        else:
            audio_send.VoiceConnection.noise_profile = None
            self.is_noise_down = False

    def change_voice_volume(self):
        current_volume = self.ui_voice_pr.VolumeOfMicSlider.value() / 10.0
        self.ui_voice_pr.label_6.setText(f"{current_volume}")
        audio_send.volume_change(current_volume)

    def check_mic_volume(self):
        if not self.is_check_volume:
            audio_send.VoiceConnection.voice_checker = True
            self.thread = threading.Thread(target=audio_send.activity_detection, args=(self.ui_voice_pr,))
            self.thread.start()
            self.is_check_volume = True
        else:
            audio_send.VoiceConnection.voice_checker = False
            self.is_check_volume = False
