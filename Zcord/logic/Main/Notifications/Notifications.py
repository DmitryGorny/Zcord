from win10toast import ToastNotifier
from playsound import playsound
import threading

class Notification:
    def __init__(self, user):
        self.__user = user
        self.__soundPath = None

    def show_chat_notifications(self, title, message):
        def play_sound():
            try:
                playsound(self._soundPath)
            except Exception as e:
                return

        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10, threaded=True)

        sound_thread = threading.Thread(target=play_sound)
        sound_thread.start()
