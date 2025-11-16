from PyQt6.QtCore import QObject, pyqtSignal

from logic.client.ClientConnections.ClientConnections import ClientConnections


class GroupsCreateModel(QObject):
    group_is_being_created_view = pyqtSignal()

    def __init__(self):
        super(GroupsCreateModel, self).__init__()

    def send_form(self, group_name: str, is_private: bool, is_invite_from_admin: bool, is_password: bool, password: str = None) -> None:
        try:
            ClientConnections.send_service_message(msg_type='GROUP-CREATE', extra_data={'group_name': group_name,
                                                                                        'is_private': is_private,
                                                                                        'is_invite_from_admin': is_invite_from_admin,
                                                                                        'is_password': is_password,
                                                                                        'password': password})
        except Exception as e:
            print(e)
            return
        self.group_is_being_created_view.emit()



