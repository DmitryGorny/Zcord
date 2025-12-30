from abc import abstractmethod

from logic.client.Strats.Strategy import Strategy


class ChooseStrategy:
    def __init__(self):
        self.__current_strategy = None

    def get_strategy(self, header: str, service_conn_obj, nickname_yours: str) -> Strategy:
        if self.__current_strategy is not None:
            if self.__current_strategy.header_name == header:
                return self.__current_strategy

        if header not in ClientsStrategies.headers.keys():
            return None

        self.__current_strategy = ClientsStrategies.headers[header]()
        self.__current_strategy.set_data(service_connection=service_conn_obj, nick=nickname_yours)
        return self.__current_strategy


class ClientsStrategies(Strategy):
    headers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "header_name"):
            cls.headers[cls.header_name] = cls

    def __init__(self):
        self.service_connection_pointer = None
        self._nickname_yours: str = None

    def set_data(self, **kwargs):
        self.service_connection_pointer = kwargs.get("service_connection")
        self._nickname_yours = kwargs.get("nick")

    @abstractmethod
    def execute(self, msg: dict) -> None:
        pass


class UserStatusReceive(ClientsStrategies):
    header_name = "USER-STATUS"

    def __init__(self):
        super(UserStatusReceive, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg['sender_id']
        sender_status = msg["user-status"]
        sender_nickname = msg["nickname"]
        receiver_nickname = self.service_connection_pointer.user.getNickName()
        target = "self" if sender_nickname == receiver_nickname else "friend"
        self.service_connection_pointer.call_main_dynamic_update("CHANGE-ACTIVITY", {'target': target,
                                                                                     'sender_nickname': sender_nickname,
                                                                                     'status_instance': sender_status[
                                                                                         'status_instance']})
        self.service_connection_pointer.user.group_member_change_status(sender_id, sender_status['status_instance'])


class SendFirstInfo(ClientsStrategies):
    header_name = "__USER-INFO__"

    def __init__(self):
        super(SendFirstInfo, self).__init__()

    def execute(self, msg: dict) -> None:
        dictToSend = {
            "friends": self.service_connection_pointer.user.getFriends(),
            "status": {'status_name': self.service_connection_pointer.user.status.name,
                       'status_instance': str(self.service_connection_pointer.user.status)},
            "last_online": self.service_connection_pointer.user.last_online,
            'chats': self.service_connection_pointer.user.get_chats(True)
        }
        self.service_connection_pointer.send_message(group='CLIENT',
                                                     msg_type="USER-INFO",
                                                     message=self.service_connection_pointer.serialize(
                                                         dictToSend).decode('utf-8'))


class ConnectToMessageServer(ClientsStrategies):
    header_name = "__CONNECT__"

    def __init__(self):
        super(ConnectToMessageServer, self).__init__()

    def execute(self, msg: dict) -> None:
        self.service_connection_pointer.connect_to_msg_server()  # TODO: Отловить ошибки подключения
        self.service_connection_pointer.send_message(group='CHAT', msg_type="CACHE-REQUEST")


class CallNotificationStrat(ClientsStrategies):
    header_name = "__CALL-NOTIFICATION__"

    def __init__(self):
        super(CallNotificationStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        user_id = msg["user_id"]  # Юзер позвонивший
        chat_id = str(msg["chat_id"])
        call_flg = int(msg["call_flg"])
        call_flg = bool(call_flg)
        print("Клиент принял ивент звонка")
        self.service_connection_pointer.chat.socket_controller.receive_call(chat_id, call_flg)


class FriendshipRequestSendStrat(ClientsStrategies):
    header_name = 'FRIENDSHIP-REQUEST-SEND'

    def __init__(self):
        super(FriendshipRequestSendStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg["sender_id"]
        receiver_id = msg['receiver_id']
        if str(self.service_connection_pointer.user.id) == str(sender_id):
            receiver_nick = msg['receiver_nick']
            self.service_connection_pointer.call_main_dynamic_update('FRIENDSHIP-REQUEST-SELF',
                                                                     {'receiver_nick': receiver_nick,
                                                                      'receiver_id': receiver_id})
        else:
            sender_nick = msg['sender_nick']
            self.service_connection_pointer.call_main_dynamic_update('FRIENDSHIP-REQUEST-OTHER',
                                                                     {'sender_id': sender_id,
                                                                      'sender_nick': sender_nick})


class FriendshipRecallSendStrat(ClientsStrategies):
    header_name = 'FRIEND-REQUEST-RECALL'

    def __init__(self):
        super(FriendshipRecallSendStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg["sender_id"]
        receiver_id = msg['friend_id']
        if sender_id == str(self.service_connection_pointer.user.id):
            self.service_connection_pointer.call_main_dynamic_update('SELF-RECALL-REQUEST', {'user_id': receiver_id})
        else:
            self.service_connection_pointer.call_main_dynamic_update('OTHERS-RECALL-REQUEST', {'user_id': sender_id})


class AcceptFriendRequestStrat(ClientsStrategies):
    header_name = 'ACCEPT-FRIEND'

    def __init__(self):
        super(AcceptFriendRequestStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg["sender_id"]
        receiver_id = msg['friend_id']
        chat_id = msg['chat_id']
        friend_nickname = msg['friend_nickname']
        sender_nickname = msg['sender_nickname']

        if str(self.service_connection_pointer.user.id) != str(sender_id):
            self.service_connection_pointer.user.add_friend(username=sender_nickname,
                                                            user_id=sender_id)
            self.service_connection_pointer.call_main_dynamic_update('ACCEPT-REQUEST-OTHERS', {'user_id': sender_id,
                                                                                               'chat_id': chat_id,
                                                                                               'sender_nickname': sender_nickname,
                                                                                               'friend_id': receiver_id
                                                                                               })
        else:
            self.service_connection_pointer.user.add_friend(username=friend_nickname,
                                                            user_id=receiver_id)
            self.service_connection_pointer.call_main_dynamic_update('ACCEPT-REQUEST-SELF', {'user_id': receiver_id,
                                                                                             'chat_id': chat_id,
                                                                                             'friend_nickname': friend_nickname,
                                                                                             })


class DeleteFriendRequestStrat(ClientsStrategies):
    header_name = 'DELETE-FRIEND'

    def __init__(self):
        super(DeleteFriendRequestStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg['friend_id']
        chat_id = str(msg['chat_id'])

        self.service_connection_pointer.user.delete_friend(friend_id=sender_id)
        self.service_connection_pointer.user.delete_chat(chat_id, True)
        self.service_connection_pointer.call_main_dynamic_update('DELETE-FRIEND', {'chat_id': chat_id})


class DeclineFriendRequestStrat(ClientsStrategies):
    header_name = 'DECLINE-FRIEND'

    def __init__(self):
        super(DeclineFriendRequestStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg["sender_id"]
        receiver_id = msg['friend_id']
        friend_nickname = msg['friend_nickname']
        if str(self.service_connection_pointer.user.id) != str(sender_id):
            self.service_connection_pointer.call_main_dynamic_update('DECLINE-REQUEST-OTHERS', {'COSTIL': 1})
        else:
            self.service_connection_pointer.call_main_dynamic_update('DECLINE-REQUEST-SELF',
                                                                     {'receiver_id': str(receiver_id),
                                                                      'friend_nickname': friend_nickname})


class CallConnectionIconStrat(ClientsStrategies):
    header_name = "__ICON-CALL__"

    def __init__(self):
        super(CallConnectionIconStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        chat_id = msg["chat_id"]
        user_id = msg["user_id"]
        username = msg["username"]
        self.service_connection_pointer.chat.socket_controller.icon_call(chat_id, user_id, username)


class CallConnectionIconLeftStrat(ClientsStrategies):
    header_name = "__LEFT-ICON-CALL__"

    def __init__(self):
        super(CallConnectionIconLeftStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        chat_id = msg["chat_id"]
        user_id = msg["user_id"]
        self.service_connection_pointer.chat.socket_controller.icon_call_left(chat_id, user_id)


class UserJoinedGroupStrat(ClientsStrategies):
    header_name = "USER-JOINED-GROUP"

    def __init__(self):
        super(UserJoinedGroupStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        group_id = str(msg["group_id"])
        joined_user = str(msg["user_id"])
        group_name = str(msg["group_name"])
        is_private = msg['is_private']
        is_password = msg['is_private']
        is_admin_invite = msg['is_admin_invite']
        admin_id = str(msg['admin_id'])
        if joined_user == str(self.service_connection_pointer.user.id):
            members_activity = msg['members_activity']
            self.service_connection_pointer.call_main_dynamic_update('JOIN-GROUP',
                                                                     {'group_id': group_id,
                                                                      'group_name': group_name,
                                                                      'is_private': is_private,
                                                                      'is_admin_invite': is_admin_invite,
                                                                      'is_password': is_password,
                                                                      'admin_id': admin_id,
                                                                      'members_activity': members_activity
                                                                      })
        else:
            status = msg['status_instance']
            self.service_connection_pointer.call_main_dynamic_update('USER-JOINED-GROUP',
                                                                     {'group_id': group_id,
                                                                      'joined_user_id': joined_user,
                                                                      'status': status})


class GroupCreatedStrat(ClientsStrategies):
    header_name = "GROUP-CREATED-SUCCESS"

    def __init__(self):
        super(GroupCreatedStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        group_json = msg['group_json']
        group_id = str(group_json['id'])
        group_name = group_json['group']["group_name"]
        is_private = group_json['group']['is_private']
        is_invite_from_admin = group_json['group']["is_invite_from_admin"]
        is_password = group_json['group']["is_password"]
        admin_id = str(group_json['group']["user_admin"])

        self.service_connection_pointer.call_main_dynamic_update('GROUP-CREATED',
                                                                 {'group_id': group_id,
                                                                  'group_name': group_name,
                                                                  'is_private': is_private,
                                                                  'is_admin_invite': is_invite_from_admin,
                                                                  'is_password': is_password,
                                                                  'admin_id': admin_id})


class GroupRequestReceiveStrat(ClientsStrategies):
    header_name = "GROUP-REQUEST"

    def __init__(self):
        super(GroupRequestReceiveStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        sender_id = msg['sender_id'],
        group_id = msg['group_id'],
        request_id = msg['request_id']
        group_name = msg['group_name']
        self.service_connection_pointer.call_main_dynamic_update('GROUP_REQUEST_RECEIVE',
                                                                 {'sender_id': sender_id,
                                                                  'group_id': str(group_id[0]),  # TODO: ПОЧЕМУ
                                                                  'request_id': request_id,
                                                                  'group_name': group_name})


class GroupRequestSentStrat(ClientsStrategies):
    header_name = "GROUP-REQUEST-SENT"

    def __init__(self):
        super(GroupRequestSentStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        group_id = str(msg['group_id'])
        self.service_connection_pointer.call_main_dynamic_update('GROUP_REQUEST_SENT',
                                                                 {'group_id': group_id})


class GroupRequestRejectedStrat(ClientsStrategies):
    header_name = "GROUP-REQUEST-REJECTED"

    def __init__(self):
        super(GroupRequestRejectedStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        user_id = str(msg['user_id'])
        if user_id == str(self.service_connection_pointer.user.id):
            self.service_connection_pointer.call_main_dynamic_update('GROUP-REQUEST-REJECTED-SELF',
                                                                     {})


class GroupUserLeftStrat(ClientsStrategies):
    header_name = "USER-LEFT-GROUP"

    def __init__(self):
        super(GroupUserLeftStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        left_user_id = str(msg['user_id'])
        group_id = str(msg['group_id'])

        if left_user_id == str(self.service_connection_pointer.user.id):
            self.service_connection_pointer.call_main_dynamic_update('GROUP-MEMBER-LEFT',
                                                                     {'chat_id': group_id, 'user_id': left_user_id})
        else:
            self.service_connection_pointer.user.remove_group_member(left_user_id, group_id)


class GroupAdminChangedStrat(ClientsStrategies):
    header_name = "GROUP-ADMIN-CHANGED"

    def __init__(self):
        super(GroupAdminChangedStrat, self).__init__()

    def execute(self, msg: dict) -> None:
        new_admin_id = str(msg['new_admin_id'])
        group_id = str(msg['chat_id'])

        self.service_connection_pointer.user.group_admin_changed(group_id, new_admin_id)

