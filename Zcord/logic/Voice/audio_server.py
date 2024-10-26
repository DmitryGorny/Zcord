import socket
import asyncio


class Client(object):
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address


class VoiceServer(object):
    def __init__(self, server_port, ip_to_output, port_to_output):
        self.HOST = "26.36.124.241"  # Standard loopback interface address (localhost)
        self.ip_to_output = ip_to_output
        self.server_port = server_port  # Port to listen on (non-privileged ports are > 1023)
        self.port_to_output = port_to_output
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 4096
        self.server.bind((self.HOST, self.server_port))
        print(f"Listening Server starts")
        self.first_packet()

    async def read_request(self):
        while True:
            self.data, self.address = self.server.recvfrom(self.CHUNK)
            if self.data[0:1] == b'0':
                print(f"{self.address} disconnect!")
                self.first_packet()
            self.data = self.data[1::]
            self.send_request()
            await asyncio.sleep(0)

    def first_packet(self):
        while True:
            data, address = self.server.recvfrom(self.CHUNK)
            if data[0:1] == b'1':
                print(f"Connect to: {address}")
                break

    def send_request(self):
        self.server.sendto(self.data, (self.ip_to_output, self.port_to_output))

    def close_server(self):
        print("Server ends")
        self.server.close()


async def main():
    listening_server_obj = VoiceServer(65128, "26.181.96.20", 22222)
    listening_server_obj1 = VoiceServer(54325, "26.36.124.241", 22223)
    task1 = asyncio.create_task(listening_server_obj.read_request())
    task2 = asyncio.create_task(listening_server_obj1.read_request())
    await task1
    await task2


if __name__ == "__main__":
    # Позже необходимо добавить работу с классом Client, а именно из него брать все апйишники и порты
    asyncio.run(main())
