from abc import abstractmethod, ABCMeta
from typing import Optional, Union
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDesktopMediaRequest
from PyQt6.QtWebEngineCore import QWebEnginePermission
from qframelesswindow.utils import ScreenCaptureFilter
from qframelesswindow import FramelessWindow
from qframelesswindow.webengine import FramelessWebEngineView
from logic.Main.Chat.View.Message.Message import Message
from logic.Main.Chat.View.CallDialog.CallView import Call
from logic.Main.Chat.View.ServiceMessage.ServiceMessage import ServiceMessage
from logic.Main.Chat.View.UserIcon.UserIcon import UserIcon, MiniUserIcon
from logic.Main.Chat.View.dm_view.ChatClass.ChatGUI import Ui_Chat
from logic.Main.Chat.View.group_view.Group.GroupQt import Ui_Group


class MyWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, sourceID):
        # Теперь все ошибки из JS будут печататься в терминале PyCharm/VS Code
        print(f"JS Console [{level}]: {message} (line {line})")


class DesktopMediaPicker(QtWidgets.QDialog):
    """Диалог выбора экрана/окна для демонстрации.

    QtWebEngine начиная с 6.7 при вызове JS-метода getDisplayMedia()
    эмитит сигнал desktopMediaRequested и ожидает, что приложение
    вручную выберет конкретный экран или окно из переданных моделей.
    Если этого не сделать, getDisplayMedia на стороне страницы
    отклоняется, и кнопка «Поделиться экраном» не работает.
    """

    def __init__(self, screens_model, windows_model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор источника для демонстрации")
        self.resize(620, 400)

        self._selected_kind = None
        self._selected_index = None

        layout = QtWidgets.QVBoxLayout(self)

        sources_layout = QtWidgets.QHBoxLayout()

        screens_box = QtWidgets.QGroupBox("Экраны")
        screens_box_layout = QtWidgets.QVBoxLayout(screens_box)
        self._screens_view = QtWidgets.QListView()
        self._screens_view.setModel(screens_model)
        self._screens_view.clicked.connect(self._on_screen_clicked)
        self._screens_view.doubleClicked.connect(
            lambda idx: (self._on_screen_clicked(idx), self.accept())
        )
        screens_box_layout.addWidget(self._screens_view)

        windows_box = QtWidgets.QGroupBox("Окна")
        windows_box_layout = QtWidgets.QVBoxLayout(windows_box)
        self._windows_view = QtWidgets.QListView()
        self._windows_view.setModel(windows_model)
        self._windows_view.clicked.connect(self._on_window_clicked)
        self._windows_view.doubleClicked.connect(
            lambda idx: (self._on_window_clicked(idx), self.accept())
        )
        windows_box_layout.addWidget(self._windows_view)

        sources_layout.addWidget(screens_box)
        sources_layout.addWidget(windows_box)
        layout.addLayout(sources_layout)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # По умолчанию выделяем первый доступный экран, чтобы по нажатию OK
        # сразу был корректный выбор без обязательного клика мыши.
        if screens_model is not None and screens_model.rowCount() > 0:
            first = screens_model.index(0, 0)
            self._screens_view.setCurrentIndex(first)
            self._selected_kind = "screen"
            self._selected_index = first

    def _on_screen_clicked(self, index):
        self._selected_kind = "screen"
        self._selected_index = index
        self._windows_view.clearSelection()

    def _on_window_clicked(self, index):
        self._selected_kind = "window"
        self._selected_index = index
        self._screens_view.clearSelection()

    def selection(self):
        return self._selected_kind, self._selected_index


class WebWindow(FramelessWindow):
    ready_to_connect = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("PyQt-Frameless-Window")

        self.hBoxLayout = QtWidgets.QHBoxLayout(self)
        self.webEngine = FramelessWebEngineView(self)
        self.installEventFilter(ScreenCaptureFilter(self))

        self.myPage = MyWebPage(self.webEngine)
        self.myPage.settings().setAttribute(
            # ВСЯ МАГИЯ ЗАХВАТА ЭКРАНА ЮЗАЕТСЯ ЧЕРЕЗ НАСТРОЙКИ ВОТ ЗДЕСЬ
            self.myPage.settings().WebAttribute.ScreenCaptureEnabled, True,
        )
        self.webEngine.setPage(self.myPage)
        self.webEngine.page().permissionRequested.connect(self._on_permission_requested)
        # Без этой подписки JS-вызов navigator.mediaDevices.getDisplayMedia()
        # в QtWebEngine 6.7+ зависает, потому что сторона приложения должна
        # явно выбрать конкретный экран или окно из переданных моделей.
        self.webEngine.page().desktopMediaRequested.connect(
            self._on_desktop_media_requested
        )

        self.webEngine.loadFinished.connect(self._on_load_finished)
        self.webEngine.load(QtCore.QUrl("http://26.181.96.20:8080/"))

        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.webEngine)

        self.titleBar.raise_()

    def _on_load_finished(self, ok):
        if ok:
            self.ready_to_connect.emit()
        else:
            print("Ошибка загрузки страницы")

    def _on_permission_requested(self, permission):
        # Список разрешений, которые мы готовы дать автоматически
        allowed_features = [
            QWebEnginePermission.PermissionType.MediaAudioCapture,
            QWebEnginePermission.PermissionType.MediaVideoCapture,
            QWebEnginePermission.PermissionType.MediaAudioVideoCapture,
            QWebEnginePermission.PermissionType.DesktopVideoCapture,
            QWebEnginePermission.PermissionType.DesktopAudioVideoCapture
        ]

        if permission.permissionType() in allowed_features:
            print("Есть разрешение")
            # Даем разрешение
            permission.grant()
        else:
            print("Нет разрешение")
            permission.deny()
            # Не даем разрешение

    def _on_desktop_media_requested(self, request: QWebEngineDesktopMediaRequest):
        screens_model = request.screensModel()
        windows_model = request.windowsModel()

        picker = DesktopMediaPicker(screens_model, windows_model, parent=self)
        if picker.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            request.cancel()
            return

        kind, index = picker.selection()
        if kind == "screen" and index is not None and index.isValid():
            request.selectScreen(index)
        elif kind == "window" and index is not None and index.isValid():
            request.selectWindow(index)
        else:
            request.cancel()


class QWidgetABCMeta(type(QtWidgets.QWidget), ABCMeta):
    pass


class IView(QtWidgets.QWidget, metaclass=QWidgetABCMeta):
    @abstractmethod
    def ask_for_cached_messages(self, val):
        pass

    @abstractmethod
    def enable_scroll(self):
        pass

    @abstractmethod
    def send_message(self):
        pass

    @abstractmethod
    def receive_message(self, sender, text, date, messageIndex=1, wasSeen: bool = False):  # Нужно еще 20 аргументов
        pass

    @abstractmethod
    def change_unseen_status(self, number_of_widgets):
        pass

    @abstractmethod
    def clear_unseen_messages(self):
        pass

    @abstractmethod
    def clear_chat_layout(self):
        pass

    @property
    @abstractmethod
    def chat_id(self) -> str:
        pass


class BaseChatView(IView):
    messageReceived = QtCore.pyqtSignal(str, dict, int)
    clear_layout = QtCore.pyqtSignal()
    enable_scroll_bar = QtCore.pyqtSignal()
    change_unseen_status_signal = QtCore.pyqtSignal(int)
    clear_unseen = QtCore.pyqtSignal()

    muteDevice = QtCore.pyqtSignal(str, bool, object)
    connectReceived = QtCore.pyqtSignal(list)
    disconnectReceived = QtCore.pyqtSignal(object)
    callReceived = QtCore.pyqtSignal(bool)
    speechDetector = QtCore.pyqtSignal(bool, int)
    iconCall = QtCore.pyqtSignal(int, str)
    iconCallLeft = QtCore.pyqtSignal(int)

    def __init__(self, chatId, user, controller, is_group: bool):
        super(BaseChatView, self).__init__()
        self.ui: Optional[Union[Ui_Chat, Ui_Group]]
        """Окно приходящего звонка"""
        self.call_dialog: Call
        """Окно для web"""
        self.web_window = None
        # Сигналы
        self.messageReceived.connect(self.receive_message)
        self.enable_scroll_bar.connect(self.enable_scroll)
        self.change_unseen_status_signal.connect(self.change_unseen_status)
        self.clear_unseen.connect(self.clear_unseen_messages)
        self.muteDevice.connect(self.mute_device_friend)
        self.connectReceived.connect(self.join_icon)
        self.disconnectReceived.connect(self.left_icon)
        self.callReceived.connect(self.show_call_widget)
        self.speechDetector.connect(self.speech_detector)
        self.iconCall.connect(self.icon_call)
        self.iconCallLeft.connect(self.icon_call_left)
        # Сигналы

        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self._controller = controller

        self._chat_id = chatId
        self._user = user
        self._old_max_scroll = None
        self._old_value_scroll = None

        self.installEventFilter(self)

        self.messageNumber = None

        self.unseenMessages = []

        self.scroll_pos = 0

        self._is_group: bool = is_group

        # Словарь по иконкам юзеров: {client: icon}
        self.client_icons = {}
        self.client_mini_icons = {}
        # Переменные мутов
        self.microphone_mute = False
        self.headphone_mute = False

    def ask_for_cached_messages(self, val):
        if val <= int(self.ui.ChatScroll.verticalScrollBar().maximum() / 4):
            self._controller.ask_for_cached_message()

            self._old_max_scroll = self.ui.ChatScroll.verticalScrollBar().maximum()
            self._old_value_scroll = self.ui.ChatScroll.verticalScrollBar().value()

    @QtCore.pyqtSlot()
    def enable_scroll(self):
        scrollbar = self.ui.ChatScroll.verticalScrollBar()

        new_max = scrollbar.maximum()
        scroll_delta = new_max - self._old_max_scroll

        if scroll_delta > 0:
            scrollbar.setValue(self._old_value_scroll + scroll_delta)

    def send_message(self):
        message_text = self.ui.Chat_input_.text()

        if len(message_text) == 0:
            return

        self._controller.send_message(message_text)
        self.ui.Chat_input_.clear()

    @QtCore.pyqtSlot(str, dict, int)
    def receive_message(self, msg_type: str, message_dict: dict[str, str], index_of_message: int = 1):
        if msg_type == 'text':
            self.receive_text_message(message_dict, index_of_message)
        elif msg_type == 'service':
            self.receive_service_message(message_dict, index_of_message)

    def receive_text_message(self, message_dict: dict[str, str], messageIndex=1):  # Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)

        text = message_dict['message']
        sender_id = message_dict['sender']
        date = message_dict['created_at']
        was_seen = message_dict['was_seen']

        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        qss = ''

        if str(sender_id) == str(self._user.id):
            sender = self._user.getNickName()
            qss = """QFrame {
                    background-color:rgba(38,40,45,255);
                    border-radius:25%;
                    border:2px solid white;
                    }
                    }"""
            layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        else:
            try:
                sender = next((fr["nickname"] for fr in self._user.getFriends() if fr["id"] == str(sender_id)))
            except StopIteration:
                group = next((gr for gr in self._user.get_groups() if gr["chat_id"] == self._chat_id))
                sender = next((gm.nickname for gm in group['users'] if str(gm.user_id) == str(sender_id)))

        if len(message_dict['message']) == 0:
            return

        message = Message(text, sender)
        message.ui.date_label.setText(date)

        if not was_seen:
            message.ui.WasSeenlabel.setText("Unseen")
            self.unseenMessages.append(message.ui)

        if len(qss) != 0:
            message.ui.Message_.setStyleSheet(qss)

        outer_widget = QtWidgets.QWidget()
        outer_widget.setFixedHeight(message.ui.Message_.height() + 10)
        layout.addWidget(message.ui.Message_)
        outer_widget.setLayout(layout)
        widget = QtWidgets.QListWidgetItem()
        widget.setSizeHint(message.ui.Message_.sizeHint())

        if messageIndex == 1:
            self.ui.ChatScroll.addItem(widget)
        else:
            self.ui.ChatScroll.insertItem(0, widget)
            # self.scroll_pos = self.ui.ChatScroll.verticalScrollBar().value()

        self.ui.ChatScroll.setItemWidget(widget, outer_widget)

        if messageIndex == 1:
            self.ui.ChatScroll.setCurrentItem(widget)

        return True

    def receive_service_message(self, message_dict: dict[str, str], messageIndex=1):  # Нужно еще 20 аргументов
        if self.ui.ChatScroll.verticalScrollBar().signalsBlocked():
            self.ui.ChatScroll.verticalScrollBar().blockSignals(False)

        text = message_dict['service_message']
        date = message_dict['created_at']
        was_seen = message_dict['was_seen']

        if len(text) == 0:
            return

        message = ServiceMessage(text)
        message.ui.date_label.setText(date)

        if not was_seen:
            message.ui.WasSeenlabel.setText("Unseen")
            self.unseenMessages.append(message.ui)

        widget = QtWidgets.QListWidgetItem()
        widget.setSizeHint(message.ui.Message_.sizeHint())

        if messageIndex == 1:
            self.ui.ChatScroll.addItem(widget)
        else:
            self.ui.ChatScroll.insertItem(0, widget)

        self.ui.ChatScroll.setItemWidget(widget, message.ui.Message_)

        if messageIndex == 1:
            self.ui.ChatScroll.setCurrentItem(widget)

        return True

    @QtCore.pyqtSlot(int)
    def change_unseen_status(self, number_of_widgets):
        if not self.unseenMessages or number_of_widgets <= 0:
            return
        try:

            count = min(number_of_widgets, len(self.unseenMessages))

            messages_to_process = self.unseenMessages[-count:]

            for message in messages_to_process:
                message.WasSeenlabel.setText("Seen")

            self.unseenMessages = self.unseenMessages[:-count]

        except Exception as e:
            print(f"Error updating unseen status: {e}")

    @QtCore.pyqtSlot()
    def clear_unseen_messages(self):
        self.unseenMessages.clear()

    def clear_chat_layout(self):
        self.ui.ChatScroll.verticalScrollBar().blockSignals(True)
        self.ui.ChatScroll.clear()

    @property
    def chat_id(self):
        return self._chat_id

    def stop_call(self):
        self.ui.Call.hide()
        self.web_window.hide()
        self.web_window.close()
        self._controller.stop_call()

        for icon in self.client_icons.values():
            self.ui.UsersFiled_layout.removeWidget(icon.ui.widget_2)
        self.client_icons = {}

    # Функция чередования для девайса мута друга
    def mute_device_friend(self, device, flg, client):
        if device == "mic":
            self.mute_mic_friend(flg, client)
        elif device == "head":
            self.mute_head_friend(flg, client)

    # Микрофон
    def mute_mic_self(self):
        self.microphone_mute = not self.microphone_mute
        self.client_icons[self._user.id].mute_mic(self.microphone_mute)
        self._controller.mute_mic_self(self.microphone_mute)

    def mute_mic_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_mic(flg)

    # Наушники
    def mute_head_self(self):
        self.headphone_mute = not self.headphone_mute
        self.client_icons[self._user.id].mute_head(self.headphone_mute)
        self._controller.mute_head_self(self.headphone_mute)

    def mute_head_friend(self, flg, client):  # Сюда будет передаваться id юзера у которого пришел мут с сервера
        self.client_icons[int(client["user_id"])].mute_head(flg)

    # Работа с иконками юзеров
    # Условие 1 - подключение к группе пользователей
    def join_icon(self, clients):
        print(f"join_icon")
        for client in clients:
            if int(client["user_id"]) not in self.client_icons.keys():
                newcomer = UserIcon(client, self._user)
                self.client_icons[int(client["user_id"])] = newcomer
                self.ui.UsersFiled_layout.addWidget(newcomer.ui.widget_2,
                                                    alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            else:
                self.client_icons[int(client["user_id"])].animate_call.stop_animation()
                self.client_icons[int(client["user_id"])].default_animation()

    # Условие 2 - выход одного из пользователей peer_left
    def left_icon(self, client):
        print("left_icon")
        self.ui.UsersFiled_layout.removeWidget(self.client_icons[int(client["user_id"])].ui.widget_2)
        del self.client_icons[int(client["user_id"])]

    def show_call_widget(self, flg):
        if flg and self.ui.Call.isHidden():
            self.call_dialog.show_call_event()
        else:
            self.call_dialog.hide_call_event()

    def speech_detector(self, flg, user_id):
        try:
            self.client_icons[int(user_id)].speech_animation(flg)
        except KeyError as e:
            pass

    def icon_call(self, user_id, username):
        if int(user_id) not in self.client_mini_icons.keys():
            newcomer = MiniUserIcon(user_id, username)
            self.client_mini_icons[int(user_id)] = newcomer
            self.ui.miniIconsCall.addWidget(newcomer.ui.widget_2)

    def icon_call_left(self, user_id):
        if int(user_id) in self.client_mini_icons.keys():
            self.ui.miniIconsCall.removeWidget(self.client_mini_icons[int(user_id)].ui.widget_2)
            del self.client_mini_icons[int(user_id)]

    """Подключение Видеосвязи"""
    def assign_room(self, state, btn):
        if state:
            self.web_window = WebWindow()
            self.web_window.ready_to_connect.connect(lambda: self._controller.assign_room(self.chat_id))
            self.web_window.show()
        else:
            self.web_window.hide()
            self.web_window.close()
