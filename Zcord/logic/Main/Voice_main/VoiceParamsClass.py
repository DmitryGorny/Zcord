from logic.Main.Voice_main.VoiceParameters import Ui_VoiceParams
from PyQt6 import QtWidgets, QtCore
from logic.VoiceRoom import audio_send
import threading
import pyaudio
import json


class VoiceParamsClass(QtWidgets.QWidget):
    changer_input = QtCore.pyqtSignal(int)
    changer_output = QtCore.pyqtSignal(int)

    def __init__(self):
        super(VoiceParamsClass, self).__init__()

        self.ui_voice_pr = Ui_VoiceParams()
        self.ui_voice_pr.setupUi(self)

        self.ui_voice_pr.pushButton.clicked.connect(self.call_noise_profile)
        self.ui_voice_pr.pushButton_2.clicked.connect(self.check_mic_volume)

        self.ui_voice_pr.VolumeOfMicSlider.valueChanged.connect(self.change_voice_volume)
        self.ui_voice_pr.VolumeOHeadphonesSlider.valueChanged.connect(self.change_headphones_volume)

        self.ui_voice_pr.VolumeOfMicSlider.sliderReleased.connect(self.save_settings)
        self.ui_voice_pr.VolumeOHeadphonesSlider.sliderReleased.connect(self.save_settings)

        self.ui_voice_pr.VolumeCheckWithNoiseReduceSlider.setEnabled(False)

        self.p = pyaudio.PyAudio()

        with open('Resources/settings/settings_voice.json', 'r', encoding='utf-8') as file:
            self.loaded_data = json.load(file)
        try:
            self.mic_index = self.loaded_data["microphone_index"]
            self.head_index = self.loaded_data["headphones_index"]
            self.volume_mic_settings = self.loaded_data["volume_mic"]
            self.volume_head_settings = self.loaded_data["volume_head"]

            self.ui_voice_pr.VolumeOfMicSlider.setValue(self.volume_mic_settings)
            self.ui_voice_pr.VolumeOHeadphonesSlider.setValue(self.volume_head_settings)
            self.change_voice_volume()
            self.change_headphones_volume()
        except Exception as e:
            print(e)
            self.mic_index = -1
            self.head_index = -1

        self.default_mic = self.p.get_default_input_device_info()['index']
        self.default_head = self.p.get_default_output_device_info()['index']
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            name = info["name"]
            try:
                name = name.encode("cp1251").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
            if info["maxInputChannels"] > 0 and info.get("hostApi") == 0:
                self.ui_voice_pr.ChooseMicroBox.addItem(name, i)
                if self.default_mic == i and self.mic_index != -1:
                    self.ui_voice_pr.ChooseMicroBox.setCurrentText(name)
                elif self.mic_index == i:
                    self.ui_voice_pr.ChooseMicroBox.setCurrentText(name)

            elif info["maxOutputChannels"] > 0 and info.get("hostApi") == 0:
                self.ui_voice_pr.ChooseHeadPhonesBox.addItem(name, i)
                if self.default_head == i and self.head_index != -1:
                    self.ui_voice_pr.ChooseHeadPhonesBox.setCurrentText(name)
                elif self.head_index == i:
                    self.ui_voice_pr.ChooseHeadPhonesBox.setCurrentText(name)

        self.ui_voice_pr.ChooseMicroBox.currentTextChanged.connect(self.change_input_device)
        self.ui_voice_pr.ChooseHeadPhonesBox.currentTextChanged.connect(self.change_output_device)

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

    def change_headphones_volume(self):
        current_volume = self.ui_voice_pr.VolumeOHeadphonesSlider.value() / 10.0
        self.ui_voice_pr.VolimeOfHeadphonesLabel.setText(f"{current_volume}")
        audio_send.headphones_volume_change(current_volume)

    def check_mic_volume(self):
        if not self.is_check_volume:
            audio_send.VoiceConnection.voice_checker = True
            self.thread = threading.Thread(target=audio_send.activity_detection, args=(self.ui_voice_pr,))
            self.thread.start()
            self.is_check_volume = True
        else:
            audio_send.VoiceConnection.voice_checker = False
            self.is_check_volume = False

    def change_input_device(self):
        if audio_send.VoiceConnection.is_running:
            self.changer_input.emit(self.ui_voice_pr.ChooseMicroBox.currentData())
        self.save_settings()

    def change_output_device(self):
        if audio_send.VoiceConnection.is_running:
            self.changer_output.emit(self.ui_voice_pr.ChooseHeadPhonesBox.currentData())
        self.save_settings()

    def save_settings(self):
        data = {
            "headphones_index": self.ui_voice_pr.ChooseHeadPhonesBox.currentData(),
            "microphone_index": self.ui_voice_pr.ChooseMicroBox.currentData(),
            "volume_mic": self.ui_voice_pr.VolumeOfMicSlider.value(),
            "volume_head": self.ui_voice_pr.VolumeOHeadphonesSlider.value()
        }
        with open('Resources/settings/settings_voice.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
