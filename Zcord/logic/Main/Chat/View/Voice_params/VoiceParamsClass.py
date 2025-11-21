from logic.Main.Chat.View.Voice_params.VoiceParameters import Ui_VoiceParams
from logic.client.SettingController.settings_controller import VoiceSettingsController
from PyQt6 import QtWidgets, QtCore
import threading
import pyaudio
import audioop
import json


class VoiceParamsClass(QtWidgets.QWidget):
    def __init__(self,):
        super(VoiceParamsClass, self).__init__()

        self.ui_voice_pr = Ui_VoiceParams()
        self.ui_voice_pr.setupUi(self)

        self.ui_voice_pr.AutoGainControl.toggled.connect(self.enable_ags)

        #self.ui_voice_pr.pushButton.clicked.connect(self.call_noise_profile)
        self.ui_voice_pr.pushButton_2.clicked.connect(self.check_mic_volume)

        self.ui_voice_pr.VolumeOfMicSlider.valueChanged.connect(self.change_voice_volume)
        self.ui_voice_pr.VolumeOHeadphonesSlider.valueChanged.connect(self.change_headphones_volume)

        self.ui_voice_pr.VolumeOfMicSlider.sliderReleased.connect(self.save_settings)
        self.ui_voice_pr.VolumeOHeadphonesSlider.sliderReleased.connect(self.save_settings)

        self.ui_voice_pr.VolumeCheckWithNoiseReduceSlider.setEnabled(False)

        self.p = pyaudio.PyAudio()

        self.mic_index = VoiceSettingsController().current_input_device()
        self.head_index = VoiceSettingsController().current_output_device()

        try:
            self.ui_voice_pr.VolumeOfMicSlider.setValue(int(VoiceSettingsController().input_volume() * 10))
            self.ui_voice_pr.VolumeOHeadphonesSlider.setValue(int(VoiceSettingsController().output_volume() * 10))
        except Exception as e:
            print(e)

        if VoiceSettingsController().is_state_ags():
            self.ui_voice_pr.AutoGainControl.toggle()

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

    """def call_noise_profile(self):
        if not self.is_noise_down:
            self.thread1 = threading.Thread(target=audio_send.listen_noise)
            self.thread1.start()
            self.is_noise_down = True
        else:
            audio_send.VoiceConnection.noise_profile = None
            self.is_noise_down = False"""

    def enable_ags(self, checked: bool):
        if checked:
            self.save_settings()
        else:
            self.save_settings()

    def change_voice_volume(self):
        current_volume = self.ui_voice_pr.VolumeOfMicSlider.value() / 10.0
        self.ui_voice_pr.label_6.setText(f"{current_volume}")
        self.save_settings()

    def change_headphones_volume(self):
        current_volume = self.ui_voice_pr.VolumeOHeadphonesSlider.value() / 10.0
        self.ui_voice_pr.VolimeOfHeadphonesLabel.setText(f"{current_volume}")
        self.save_settings()

    def change_input_device(self):
        self.save_settings()

    def change_output_device(self):
        self.save_settings()

    def save_settings(self):
        data = {
            "headphones_index": self.ui_voice_pr.ChooseHeadPhonesBox.currentData(),
            "microphone_index": self.ui_voice_pr.ChooseMicroBox.currentData(),
            "volume_mic": self.ui_voice_pr.VolumeOfMicSlider.value(),
            "volume_head": self.ui_voice_pr.VolumeOHeadphonesSlider.value(),
            "ags": self.ui_voice_pr.AutoGainControl.isChecked()
        }
        with open('Resources/settings/Voice/settings_voice.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def check_mic_volume(self):
        """Включает или выключает тест микрофона"""
        if not self.is_check_volume:
            self.is_check_volume = True
            self.ui_voice_pr.pushButton_2.setText("Остановка")
            self.thread = threading.Thread(target=self._mic_test_loop, daemon=True)
            self.thread.start()
        else:
            self.is_check_volume = False
            self.ui_voice_pr.pushButton_2.setText("Проверка")

    def _mic_test_loop(self):
        """Поток для тестирования микрофона"""
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                input=True,
                frames_per_buffer=960,
                input_device_index=VoiceSettingsController().current_input_device()
            )
            out_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                frames_per_buffer=960,
                output_device_index=VoiceSettingsController().current_output_device()
            )
        except Exception as e:
            print(f"[MicTest] Ошибка открытия микрофона: {e}")
            self.is_check_volume = False
            return

        print(f"[MicTest] Тест микрофона запущен")

        while self.is_check_volume:
            try:
                data = stream.read(960, exception_on_overflow=False)
                data = audioop.mul(data, 2, VoiceSettingsController().input_volume())
                rms = audioop.rms(data, 2)
                volume_percent = min(100, int(rms / 50))
                out_stream.write(data)
                QtCore.QMetaObject.invokeMethod(
                    self.ui_voice_pr.VolumeCheckWithNoiseReduceSlider,
                    "setValue",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                    QtCore.Q_ARG(int, volume_percent)
                )
            except Exception:
                pass

        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass

        QtCore.QMetaObject.invokeMethod(
            self.ui_voice_pr.VolumeCheckWithNoiseReduceSlider,
            "setValue",
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(int, 0)
        )

        print("[MicTest] Тест микрофона остановлен.")
