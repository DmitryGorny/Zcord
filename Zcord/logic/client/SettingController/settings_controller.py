class VoiceSettingsController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(VoiceSettingsController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def input_volume(self):
        pass

    def output_volume(self):
        pass

    def current_input_device(self):
        pass

    def current_output_device(self):
        pass


class ChatSettingController:
    def __init__(self):
        pass
