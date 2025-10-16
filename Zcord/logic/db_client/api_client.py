import requests


class APIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.base_url = "http://127.0.0.1:8000/api"
            cls._instance.session = requests.Session()  # Общая сессия
            cls._instance.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
        return cls._instance

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {method} {url} - {e}")
            return None

    # Работа с пользователями
    def get_users(self):
        return self._request('GET', 'users/')

    def get_user(self, nickname):
        return self._request('GET', 'users/', params={'search': nickname})

    def get_user_by_id(self, user_id):
        return self._request('GET', f'users/{user_id}/')

    def create_user(self, nickname, password, firstname=None, secondname=None, lastname=None):
        data = {
            "nickname": nickname,
            "password": password,
            "firstname": firstname,
            "secondname": secondname,
            "lastname": lastname
        }
        return self._request('POST', 'users/', json=data)

    # Работа с заявками в друзья
    def get_friend_request(self, sender_id, receiver_id):
        data = {
            "sender_id": sender_id,
            "receiver_id": receiver_id
        }
        return self._request('GET', 'friends_adding/', params=data)

    def get_your_friend_request(self, sender_id):
        data = {
            "sender_id": sender_id,
        }
        return self._request('GET', 'friends_adding/', params=data)

    def get_others_friend_request(self, receiver_id):
        data = {
            "receiver_id": receiver_id,
        }
        return self._request('GET', 'friends_adding/', params=data)

    def send_friend_request(self, sender_id, receiver_id, friendship_id):
        data = {
            "sender": sender_id,
            "receiver": receiver_id,
            'friendship_id': friendship_id
        }
        return self._request('POST', 'friends_adding/', json=data)

    def delete_friendship_request(self, sender_id, receiver_id, friendship_id):
        data = {
            "sender": sender_id,
            "receiver": receiver_id,
            'friendship_id': friendship_id
        }
        return self._request('DELETE', 'friends_adding/', json=data)

    def delete_friend_requests(self, friend_requests_id):
        return self._request('DELETE', f'friends_adding/{friend_requests_id}/')

    # Работа с дружбой
    def create_friendship_request(self, user1, user2):
        data = {
            "status": 1,
            "user1": user1,
            "user2": user2
        }
        return self._request('POST', 'friendship/', json=data)

    def get_friendship_by_nicknames(self, nickname1, nickname2):
        data = {
            'user1': nickname1,
            'user2': nickname2
        }
        return self._request('GET', 'friendship/', params=data)

    def get_friendship_by_id(self, user1_id, user2_id):
        data = {
            'user1_id': user1_id,
            'user2_id': user2_id
        }
        return self._request('GET', 'friendship/', params=data)

    def get_friendships_by_nickname(self, nickname):
        data = {
            'search': nickname
        }
        return self._request('GET', 'friendship/', params=data)

    def patch_friendship_status(self, friendship_id, status):
        data = {
            "status": status,
        }
        return self._request('PATCH', f'friendship/{friendship_id}/', json=data)

    def put_friendship(self, status, user1, user2):
        data = {
            "status": status,
            "user1": user1,
            "user2": user2
        }
        return self._request('PUT', 'friendship/', json=data)

    def delete_friendship(self, friendship_id):
        return self._request('DELETE', f'friendship/{friendship_id}/')

    # Работа с сообщениями
    def send_messages(self, chat_id, sender_id, message_text):
        data = {
            "chat_id": chat_id,
            "sender": sender_id,
            "message": message_text
        }
        return self._request('POST', 'messages/', json=data)

    def get_messages(self, chat_id):
        data = {
            'search': chat_id
        }
        return self._request('GET', 'messages/', params=data)

    def mark_message_as_seen(self, message_id):
        data = {
            "was_seen": True
        }
        return self._request('PATCH', f'messages/{message_id}/', json=data)

    def get_messages_limit(self, chat_id, limit):
        data = {
            "search": chat_id,
            "limit": limit
        }
        return self._request("GET", "messages/", params=data)['results']

    def get_messages_limit_offset(self, chat_id, limit, offset):
        data = {
            "search": chat_id,
            "limit": limit,
            "offset": offset
        }
        return self._request("GET", "messages/", params=data)['results']

    def send_messages_bulk(self, messages_list):
        data = {
            "messages": messages_list
        }
        return self._request('POST', 'messages-bulk/', json=data)

    def update_messages_bulk(self, ids: list):
        data = {
            "ids": ids
        }
        return self._request('POST', "messages-bulk-update/", json=data)

    def get_uneesn_messages_count(self, chat_id, user_id):
        params = {
            'id': int(chat_id),
            'user_id': int(user_id)
        }
        return self._request("GET", 'messages-unseen-count/', params=params)

    # Работа с группами
    def get_users_group(self, user_id):
        return self._request('GET', f'groups-members/?user_id={user_id}/')

    # Работа с чатами
    def get_chats(self, user_id, is_group):
        """{
        "id": 1,
        "is_group": false,
        "group": null,
        "DM": {
            "id": 278,
            "status": 2,
            "created_at": "2025-10-10T10:10:09.162144Z",
            "updated_at": "2025-10-10T10:10:11.554547Z",
            "user1": 1,
            "user2": 3
        }
    }"""
        params = {
            'is_group': 1 if is_group else 0,
            'user_id': int(user_id)
        }
        return self._request('GET', f'chats/', params=params)

    def create_dm_chat(self, chat_id):
        params = {
            'DM_id': chat_id,
            'is_group': False
        }
        return self._request('POST', f'chats/', data=params)

    def create_group_chat(self, group_id):
        params = {
            'group_id': group_id,
            'is_group': True
        }
        return self._request('POST', f'chats/', params=params)
