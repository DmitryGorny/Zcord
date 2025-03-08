from pygame import mixer


class SoundPlayer:
    def __init__(self, obj_user=None):
        self.obj_user = obj_user  # Объект пользователя
        mixer.init()

    def load_sound(self, file_path):
        self.sound = mixer.Sound(file_path)

    def play(self, loops=0):
        self.sound.play(loops=loops)

    def stop(self):
        self.sound.stop()

    def set_volume(self, volume: float):
        self.sound.set_volume(volume)

    def quit(self):
        mixer.quit()
