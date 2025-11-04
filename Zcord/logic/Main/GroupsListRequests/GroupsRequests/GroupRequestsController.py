from logic.Main.GroupsListRequests.GroupsRequests.GroupRequestsModel import GroupRequestModel, IGroupRequestModel
from logic.Main.GroupsListRequests.GroupsRequests.View.RequestsView import IRequestsView, RequestsView


class GroupRequestsController:
    def __init__(self, user):
        self._view: IRequestsView = RequestsView()
        self._model: IGroupRequestModel = GroupRequestModel(user)

        self._view.connect_request_accepted(self._model.accept_request)
        self._view.connect_decline_accepted(self._model.reject_request)

        self._model.connect_remove_requests(self._view.remove_request)
        self._model.connect_add_requests(self._view.add_request)

    def get_widget(self):
        return self._view.get_widget()
