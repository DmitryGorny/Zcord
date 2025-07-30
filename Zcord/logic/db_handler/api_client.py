import requests


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.base_url = base_url

    # Работа с пользователями
    def get_users(self):
        response = requests.get(f"{self.base_url}/users/")
        return response.json()

    def get_user(self, nickname):
        response = requests.get(f"{self.base_url}/users/?search={nickname}")
        return response.json()

    def create_user(self, nickname, password, firstname=None, secondname=None, lastname=None):
        data = {
            "nickname": nickname,
            "password": password,
            "firstname": firstname,
            "secondname": secondname,
            "lastname": lastname
        }
        response = requests.post(f"{self.base_url}/users/", json=data)
        return response.json()

    # Работа с заявками в друзья
    def get_friend_request(self, sender_id, receiver_id):
        data = {
            "sender": sender_id,
            "receiver": receiver_id
        }
        response = requests.get(f"{self.base_url}/friendsadding/", json=data)
        return response.json()

    def send_friend_request(self, sender_id, receiver_id):
        data = {
            "sender": sender_id,
            "receiver": receiver_id
        }
        response = requests.post(f"{self.base_url}/friendsadding/", json=data)
        return response.json()

    def delete_friend_requests(self, friend_requests_id):
        response = requests.delete(f"{self.base_url}/friendsadding/{friend_requests_id}")
        return response.json()

    # Работа с дружбой
    def create_friendship_request(self, user1, user2):
        data = {
            "status": 1,
            "user1": user1,
            "user2": user2
        }
        response = requests.post(f"{self.base_url}/friendship/", json=data)
        return response.json()

    def get_friendship_by_nicknames(self, nickname1, nickname2):
        params = {
            'user1': nickname1,
            'user2': nickname2
        }
        try:
            response = requests.get(
                f"{self.base_url}/friendship/",
                params=params
            )
            response.raise_for_status()
            friendships = response.json()
            # Возвращаем первую найденную дружбу (если есть)
            return friendships[0] if friendships else None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при поиске дружбы: {e}")
            return None

    def patch_friendship_status(self, friendship_id, status):
        data = {
            "status": status,
        }
        response = requests.patch(f"{self.base_url}/friendship/{friendship_id}", json=data)
        return response.json()

    def put_friendship(self, status, user1, user2):
        data = {
            "status": status,
            "user1": user1,
            "user2": user2
        }
        response = requests.put(f"{self.base_url}/friendship/", json=data)
        return response.json()

    def delete_friendship(self, friendship_id):
        response = requests.delete(f"{self.base_url}/friendship/{friendship_id}")
        return response.json()

    # Работа с сообщениями
    def send_messages(self, chat_id, sender_id, message_text):
        data = {
            "chat_id": chat_id,
            "sender": sender_id,
            "message": message_text
        }
        response = requests.post(f"{self.base_url}/message/", json=data)
        return response.json()

    def get_messages(self, chat_id):
        response = requests.get(f"{self.base_url}/message/?chat_id={chat_id}")
        return response.json()

    def mark_message_as_seen(self, message_id):
        data = {
            "was_seen": True
        }
        response = requests.patch(f"{self.base_url}/message/{message_id}/", json=data)
        return response.json()
