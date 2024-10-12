import socket
import pyaudio
import asyncio
import numpy as np


class Client(object):
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class Server(object):
    def __init__(self, output_addresses, server_port, output_port):
        self.addreses = []
        self.output_addresses = output_addresses
        self.output_port = output_port
        self.HOST = "26.36.124.241"  # Standard loopback interface address (localhost)
        self.PORT = server_port  # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 4096
        print("Server starts")

    async def read_request(self):
        self.server.bind((self.HOST, self.PORT))
        self.data, self.address = self.server.recvfrom(self.CHUNK)
        print(f"Connected to: {self.address}")
        cl = Client(address=self.address)

        while True:
            self.data, self.address = self.server.recvfrom(self.CHUNK)

            if not self.data:
                break

            self.send_request()

    def send_request(self):
        self.server.sendto(self.data, (self.output_addresses[0], self.output_port))

    def close_server(self):
        print("Server ends")
        self.server.close()


if __name__ == "__main__":
    list_of_users = ["26.181.96.20", "26.36.124.241"]
    free_server_ports = [32731, 13764, 50001, 45632]
    output_client_ports = [32783, 12833, 12454, 59317]
    socket_list = []
    for i in range(len(list_of_users)):
        list_output_users = list_of_users.copy().pop(i)
        socket_list.append(Server(list_output_users, free_server_ports[i], output_client_ports[i]))
    ioloop = asyncio.get_event_loop()
    tasks = []
    for j in socket_list:
        tasks.append(ioloop.create_task(j.read_request()))
    ioloop.run_until_complete(asyncio.wait(tasks))

    ioloop.close()
    #server_obj = Server()
    #server_obj.read_request()
