from typing import Dict, List


class UnseenManager: # TODO: Повесить try-except, поставить lock на защиту от гонки потоков???
    def __init__(self):
        self._unseen_messages: Dict[str, Dict[str, int]] = {}

    def add_user(self, chat_id: str, user_id: str) -> None:
        if chat_id not in self._unseen_messages.keys():
            self._unseen_messages[chat_id] = {user_id: 0}
            return

        if user_id not in self._unseen_messages[chat_id]:
            self._unseen_messages[chat_id][user_id] = 0
            return

    def increment_users_count(self, chat_id: str, user_id: str) -> None:
        self._unseen_messages[chat_id][user_id] += 1

    def subtract_users_count(self, chat_id: str, user_id: str, number: int) -> None:
        self._unseen_messages[chat_id][user_id] = max(0, self._unseen_messages[chat_id][user_id] - number)


    def set_new_value(self, chat_id: str, user_id: str, val: int) -> None:
        self._unseen_messages[chat_id][user_id] = val

    def delete_chat(self, chat_id: str) -> None:
        del self._unseen_messages[chat_id]

    def delete_user(self, user_id: str):
        for chat_id in self._unseen_messages.keys():
            if user_id not in self._unseen_messages[chat_id].keys():
                continue
            del self._unseen_messages[chat_id][user_id]

    def get_user_count(self, chat_id: str, user_id: str) -> int:
        return self._unseen_messages[chat_id][user_id]

    def get_users(self, chat_id: str, user_id: str) -> List[str]:
        users_ids = []
        for user in self._unseen_messages[chat_id].keys():
            if user == user_id:
                continue
            users_ids.append(user)
        return users_ids
