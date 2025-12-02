from logic.Main.Groups.GroupsRequests.GroupRequestsModel import GroupRequestModel, IGroupRequestModel
from logic.Main.Groups.GroupsRequests.View.RequestsView import IRequestsView, RequestsView


class GroupRequestsController:
    def __init__(self, user):
        self._view: IRequestsView = RequestsView()
        self._model: IGroupRequestModel = GroupRequestModel(user)

        self._view.connect_request_accepted(self._model.accept_request)
        self._view.connect_decline_accepted(self._model.reject_request)

        self._model.connect_remove_requests(self._view.remove_request)
        self._model.connect_add_requests(self._view.add_request)

        self._model.get_groups_rejects()

    def get_widget(self):
        return self._view.get_widget()

    def request_received(self, group_id: str, group_name: str, request_id: int):
        self._view.add_request(group_id=group_id, group_name=group_name, request_id=request_id)

    def reload_page(self):
        self._view.clear_page()
        self._model.get_groups_rejects()
