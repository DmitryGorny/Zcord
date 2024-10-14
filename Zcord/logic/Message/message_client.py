import socket
import threading


class MessageConnection(object):
    def __init__(self, client_tcp):
        self.client_tcp = client_tcp

    def send_message(self):
        while True:
            msg = f"{nickname}: {input()}"
            self.client_tcp.sendall(msg.encode("utf-8"))

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
    SERVER_IP = "26.124.194.150"  # IP адрес сервера
    SERVER_PORT = 55555  # Порт, используемый сервером

    nickname = input("Введите свой ник: ")

    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_tcp.connect((SERVER_IP, SERVER_PORT))

    message_binder = MessageConnection(client_tcp)

    print("Старт клиента сообщений")
    try:
        receive_thread = threading.Thread(target=message_binder.recv_message)
        receive_thread.start()

        write_thread = threading.Thread(target=message_binder.send_message)
        write_thread.start()
    except KeyboardInterrupt:
        print("Прекращение работы клиента сообщений")
