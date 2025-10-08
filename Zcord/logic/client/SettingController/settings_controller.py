import json
from PyQt6.QtCore import QFileSystemWatcher, pyqtSignal, QObject


class VoiceSettingsController(QObject):
    _instance = None
    _initialized = False
    settingsChanged = pyqtSignal(dict)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(VoiceSettingsController, cls).__new__(cls)
        return cls._instance

    def __init__(self, path="Resources/settings/settings_voice.json"):
        """Подгрузка настроек клиента"""
        if self._initialized:
            return
        super().__init__()
        self._initialized = True

        self.path = path
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.path)
        self.watcher.fileChanged.connect(self.load_settings)
        self.load_settings()

    def load_settings(self):
        try:
            with open('Resources/settings/settings_voice.json', 'r', encoding='utf-8') as file:
                self.loaded_data = json.load(file)

            self.mic_index = self.loaded_data["microphone_index"]
            self.head_index = self.loaded_data["headphones_index"]
            self.volume_mic_settings = self.loaded_data["volume_mic"]
            self.volume_head_settings = self.loaded_data["volume_head"]

            self.settingsChanged.emit(self.loaded_data)
        except Exception as e:
            print(e)
            self.mic_index = -1
            self.head_index = -1

    def input_volume(self) -> float:
        return self.volume_mic_settings / 10

    def output_volume(self) -> float:
        return self.volume_head_settings / 10

    def current_input_device(self) -> int:
        return self.mic_index

    def current_output_device(self) -> int:
        return self.head_index


class ChatSettingController:
    def __init__(self):
        pass
