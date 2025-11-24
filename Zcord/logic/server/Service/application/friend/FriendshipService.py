from logic.server.Service.core.MessageServiceCommunication.IMessageServiceDispatcher import IMessageServiceDispatcher
from logic.server.Service.core.repositroies.chat_repo.IChatDBRepo import IChatDBRepo
from logic.server.Service.core.repositroies.chat_repo.IChatRepo import IChatRepo
from logic.server.Service.core.repositroies.client_repo.IClientDBRepo import IClientDBRepo
from logic.server.Service.core.repositroies.client_repo.IClientRepo import IClientRepo
from logic.server.Service.core.repositroies.friend_repo.IFriendDBRepo import IFriendDBRepo
from logic.server.Service.core.repositroies.friend_repo.IFriendRepo import IFriendRepo
from logic.server.Service.core.services.friend.IFriendService import IFriendService


class FriendService(IFriendService):
    def __init__(self, client_repo: IClientRepo,
                 friend_repo: IFriendRepo,
                 chat_repo: IChatRepo,
                 chat_db_rp: IChatDBRepo,
                 friend_db_rp: IFriendDBRepo,
                 client_db_rp: IClientDBRepo,
                 msg_communication: IMessageServiceDispatcher):
        self._client_repo: IClientRepo = client_repo
        self._client_db_repo: IClientDBRepo = client_db_rp
        self._friend_repo: IFriendRepo = friend_repo
        self._friend_db_repo = friend_db_rp
        self._chat_repo: IChatRepo = chat_repo
        self._chat_db_repo: IChatDBRepo = chat_db_rp
        self._msg_server_communication: IMessageServiceDispatcher = msg_communication

    async def friend_request_send(self, friend_id: str, user_id: str, receiver_nick: str, sender_nick: str) -> None:
        fr_request = self._friend_db_repo.create_friendship_request(int(user_id), int(friend_id))

        if fr_request is None:
            friendship = self._friend_db_repo.get_friendship_by_users_id(int(user_id), int(friend_id))[0]
            if friend_id != str(friendship['user2']) and user_id != str(friendship['user1']):
                self._friend_db_repo.patch_friendship_status(friendship['id'], 2)

        self._friend_db_repo.send_friend_request(sender_id=int(user_id), receiver_id=int(friend_id),
                                                 friendship_id=fr_request["id"])
        await self._client_repo.send_message(client_id=user_id, msg_type="FRIENDSHIP-REQUEST-SEND",
                                             extra_data={'sender_id': user_id,
                                                         'receiver_id': friend_id,
                                                         'sender_nick': sender_nick})
        await self._client_repo.send_message(client_id=friend_id, msg_type="FRIENDSHIP-REQUEST-SEND",
                                             extra_data={'sender_id': user_id,
                                                         'receiver_id': friend_id,
                                                         'sender_nick': sender_nick})

        self._friend_repo.add_friend(client_id=user_id, friend_name=receiver_nick, friend_id=friend_id, status='1')
        self._friend_repo.add_friend(client_id=friend_id, friend_name=sender_nick, friend_id=friend_id, status='1')

    def friend_request_recall(self, friend_id: str, sender_id: str) -> None:
        friendship = self._friend_db_repo.get_friendship_by_users_id(int(sender_id), int(friend_id))[0]
        friendship_id = friendship['id']

        delete_friend_request = self._friend_db_repo.delete_friendship_request(int(sender_id), int(friend_id),
                                                                               int(friendship_id))
        if delete_friend_request is not None:
            self._friend_db_repo.delete_friendship(friendship_id)

        self._client_repo.send_message(client_id=friend_id, msg_type="FRIEND-REQUEST-RECALL",
                                       extra_data={'sender_id': sender_id,
                                                   'friend_id': friend_id})
        self._client_repo.send_message(client_id=sender_id, msg_type="FRIEND-REQUEST-RECALL",
                                       extra_data={'sender_id': sender_id,
                                                   'friend_id': friend_id})

        self._friend_repo.delete_friend(sender_id, friend_id)

    async def friend_request_accepted(self, friend_id: str, sender_id: str) -> None:
        friendship = self._friend_db_repo.get_friendship_by_users_id(int(sender_id), int(friend_id))[0]
        self._friend_db_repo.patch_friendship_status(friendship['id'], 2)
        # TODO: Вот это все какая-то полная хуйня, проверить как можно получить ник отправителя на клиенте
        self._chat_db_repo.create_dm_chat(friendship['id'])
        friend = self._client_db_repo.get_user_by_id(int(friend_id))
        sender = self._client_db_repo.get_user_by_id(int(sender_id))
        self._friend_db_repo.delete_friendship_request(int(sender_id), int(friend_id), friendship['id'])

        # Рассылка сообщений
        await self._client_repo.send_message(client_id=sender_id, msg_type="ACCEPT-FRIEND",
                                             extra_data={'sender_id': sender_id,
                                                         'friend_id': friend_id,
                                                         'chat_id': friendship['id'],
                                                         'friend_nickname': friend['nickname'],
                                                         'sender_nickname': sender['nickname']})

        await self._client_repo.send_message(client_id=friend_id, msg_type="ACCEPT-FRIEND",
                                             extra_data={'sender_id': sender_id,
                                                         'friend_id': friend_id,
                                                         'chat_id': friendship['id'],
                                                         'friend_nickname': friend['nickname'],
                                                         'sender_nickname': sender['nickname']})
        # Изменение статуса дружбы на сервере
        self._friend_repo.change_friendship_status(sender_id, friend_id, '2')
        self._friend_repo.change_friendship_status(friend_id, sender_id, '2')

        # Добавление чата
        self._chat_repo.add_chat(str(friendship['id']), [str(friend_id), str(sender_id)])

        # Уведомление месседж сервера
        await self._msg_server_communication.send_msg_server("ADD-FRIEND", {"sender_id": sender_id,
                                                                            "receiver_id": friend_id,
                                                                            "chat_id": friendship['id']})

        # Рассылка нового статуса онлайна
        await self._client_repo.change_client_activity_status(client_id=sender_id,
                                                              status={'color': 'green', 'user-status': 'В сети'})
        await self._client_repo.change_client_activity_status(client_id=friend_id,
                                                              status={'color': 'green', 'user-status': 'В сети'})

    async def friend_request_rejected(self, friend_id: str, sender_id: str) -> None:
        friendship = self._friend_db_repo.get_friendship_by_users_id(int(sender_id), int(friend_id))[0]
        self._friend_db_repo.delete_friendship_request(int(sender_id), int(friend_id), friendship['id'])
        self._friend_db_repo.delete_friendship(friendship['id'])

        friend = self._client_db_repo.get_user_by_id(int(friend_id))
        await self._client_repo.send_message(client_id=sender_id, msg_type="DECLINE-FRIEND",
                                             extra_data={'sender_id': sender_id,
                                                         'friend_id': friend_id,
                                                         'friend_nickname': friend['nickname']
                                                         })
        await self._client_repo.send_message(client_id=friend_id, msg_type="DECLINE-FRIEND",
                                             extra_data={'sender_id': sender_id,
                                                         'friend_id': friend_id,
                                                         'friend_nickname': friend['nickname']
                                                         })

        self._friend_repo.delete_friend(sender_id, friend_id)


    def friend_delete(self) -> None:
        pass
