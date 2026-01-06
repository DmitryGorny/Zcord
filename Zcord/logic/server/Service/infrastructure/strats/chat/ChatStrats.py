import json

from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, ChatStrategyKeeper


class RequestCacheStrategy(ChatStrategyKeeper, IServiceStrat):
    command_name = "CACHE-REQUEST"

    def __init__(self):
        super(RequestCacheStrategy, self).__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])

        await self._service.cache_request(user_id=user_id)


class ChangeChatStrategy(ChatStrategyKeeper, IServiceStrat):
    command_name = "__change_chat__"

    def __init__(self):
        super(ChangeChatStrategy, self).__init__()

    async def execute(self, msg: dict) -> None:
        user_id = str(msg["user_id"])
        chat_code = int(msg["chat_id"])

        await self._service.change_chat(user_id=user_id, chat_code=chat_code)


class GroupRejectAcceptStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "GROUP-REQUEST-REJECTED"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_id = str(msg['request_id'])
        user_id = str(msg['user_id'])
        group_id = str(msg['group_id'])
        await self._service.group_request_rejected(request_id, user_id, group_id)


class GroupRequestAcceptStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "GROUP-REQUEST-ACCEPTED"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_receiver = str(msg['user_id'])
        group_id = str(msg['group_id'])
        request_id = str(msg['request_id'])
        nickname = str(msg['nickname'])
        await self._service.add_user_group(request_receiver=request_receiver,
                                           group_id=group_id,
                                           request_id=request_id,
                                           receiver_nick=nickname)


class UserLeftGroupStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "USER-LEFT-GROUP"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        request_receiver = str(msg['request_receiver'])
        group_id = str(msg['group_id'])
        await self._service.user_left_group(request_receiver=request_receiver, group_id=group_id)


class CreateGroupStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "CREATE-GROUP"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        creator_id = str(msg['user_id'])
        group_name = msg['group_name']
        is_private = msg['is_private']
        is_invite_from_admin = msg['is_invite_from_admin']
        is_password = msg['is_password']
        password = msg['password']
        members = msg['members']
        await self._service.create_group(creator_id=creator_id,
                                         group_name=group_name,
                                         is_private=is_private,
                                         is_invite_from_admin=is_invite_from_admin,
                                         is_password=is_password,
                                         password=password,
                                         members=members)


class SendGroupInviteStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "SEND-GROUP-INVITE"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        sender_id = str(msg['user_id'])
        receiver_id = str(msg['receiver_id'])
        group_id = msg['group_id']
        await self._service.send_group_request(sender_id=sender_id, receiver_id=receiver_id, group_id=group_id)


class ChangeGroupSettingsStrat(ChatStrategyKeeper, IServiceStrat):
    command_name = "CHANGE-GROUP-SETTINGS"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        sender_id = str(msg['user_id'])
        group_id = str(msg['group_id'])
        new_settings = json.loads(msg['new_settings'])
        flags = json.loads(msg['flags'])

        await self._service.change_group_settings(sender_id=sender_id, new_settings=new_settings, group_id=group_id, flags=flags)
