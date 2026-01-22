from logic.Main.Groups.GroupsList.GroupListModel import GroupListModel
from logic.Main.Groups.GroupsList.View.GroupListView import GroupListView


class GroupListController:
    def __init__(self, user_id: str, user_nickname: str):
        self._view = GroupListView()
        self._model = GroupListModel(user_id, user_nickname)

        self._model.add_group_view.connect(self._view.add_group)
        self._model.show_password_dialog.connect(self._view.show_password_dialog)
        self._model.remove_group_view.connect(self._view.remove_group)

        self._view.send_password_model.connect(self._model.send_password)
        self._view.join_group_model.connect(self._model.join_group)

        self._model.get_groups()

    def get_widget(self):
        return self._view.get_widget()

