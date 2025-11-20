from logic.Main.Chat.View.GroupInviteDialog.GroupInviteModel import GroupInviteModel
from logic.Main.Chat.View.GroupInviteDialog.view.GroupInviteView import GroupInviteView


class GroupInviteController:
    def __init__(self, user):
        self._view: GroupInviteView = GroupInviteView()
        self._model: GroupInviteModel = GroupInviteModel(user)

        self._view.create_group_model.connect(self._model.create_group)

