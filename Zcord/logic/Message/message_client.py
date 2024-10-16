import socket
import threading


class MainInterface:
    __current_chat = 1

    def __init__(self):
        pass

    def change_chat(self, current_chat):
        MainInterface.__current_chat = current_chat

    def return_current_chat(self):
        return MainInterface.__current_chat


class MessageConnection(MainInterface):
    def __init__(self, client_tcp):
        self.client_tcp = client_tcp
        super().__init__()

    def send_message(self):
        while True:
            a = input()
            if a == "change chat":
                self.change_chat(input("Введите id чата: "))
            else:
                msg = f"{self.return_current_chat()}, {nickname}, {a}".encode("utf-8")
                self.client_tcp.sendall(msg)

    def recv_message(self):
        while True:
            try:
                message = self.client_tcp.recv(1024).decode("utf-8")
                if message == 'NICK':
                    self.client_tcp.send(nickname.encode('utf-8'))
                else:
                    print(message)
            except ConnectionResetError:
                print("Ошибка, конец соединения")
                self.client_tcp.close()
                break


if __name__ == "__main__":
    SERVER_IP = "26.36.124.241"  # IP адрес сервера
    SERVER_PORT = 55555  # Порт, используемый сервером

    nickname = input("Введите свой ник: ")

    all_chats = [1, 2]

    try:
        client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_tcp.connect((SERVER_IP, SERVER_PORT))

        message_binder = MessageConnection(client_tcp)
    except ConnectionRefusedError:
        print("Не удалось подключится к серверу или сервер неактивен")
        exit(0)

    print("Старт клиента сообщений")
    try:
        receive_thread = threading.Thread(target=message_binder.recv_message)
        receive_thread.start()

        write_thread = threading.Thread(target=message_binder.send_message)
        write_thread.start()

        while True:
            pass

    except KeyboardInterrupt:
        print("Прекращение работы клиента сообщений")
        exit(0)
