from logic.server.Service.infrastructure.strats.IStrat import IServiceStrat, FriendStrategyKeeper


class SendFriendRequest(FriendStrategyKeeper, IServiceStrat):
    command_name = "FRIENDSHIP-REQUEST-SEND"

    def __init__(self):
        super(SendFriendRequest, self).__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['friend_id']
        user_id: str = msg['user_id']
        receiver_nick = msg['friend_nick']
        sender_nick = msg['sender_nick']

        await self._service.friend_request_send(user_id=user_id,
                                                friend_id=friend_id,
                                                receiver_nick=receiver_nick,
                                                sender_nick=sender_nick)


class RecallFriendRequest(FriendStrategyKeeper, IServiceStrat):
    command_name = "FRIENDSHIP-REQUEST-RECALL"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['friend_id']
        sender_id: str = msg['sender_id']
        await self._service.friend_request_recall(friend_id, sender_id)


class AcceptFriendRequestStrat(FriendStrategyKeeper, IServiceStrat):
    command_name = "ACCEPT-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['receiver_id']
        sender_id: str = msg['sender_id']
        await self._service.friend_request_accepted(friend_id, sender_id)


class DeclineFriendRequestStrat(FriendStrategyKeeper, IServiceStrat):
    command_name = "DECLINE-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        friend_id: str = msg['receiver_id']
        sender_id: str = msg['sender_id']
        await self._service.friend_request_rejected(friend_id, sender_id)


class DeleteFriendRequestStrat(FriendStrategyKeeper, IServiceStrat):
    command_name = "DELETE-FRIEND"

    def __init__(self):
        super().__init__()

    async def execute(self, msg: dict) -> None:
        print(111)
        friend_id: str = msg['receiver_id']
        sender_id: str = msg['sender_id']
        await self._service.friend_delete(friend_id, sender_id)
