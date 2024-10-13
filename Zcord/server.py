import socket
import pyaudio
import threading
import multiprocessing as mp
import numpy as np






class Client(object):
    def __init__(self, address):
        self.address = address

    def return_address(self):
        return self.address



class SpeakingServer(object):
    def __init__(self, ipToSend,portToSend):
        self.HOST = "26.181.96.20"
        self.PORT_TO_SEND = portToSend
        self.IP_TO_SEND = ipToSend
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 4096
        print("Speaking Server starts")

    def send_request(self, ListenServerObject):
        self.server.connect((self.HOST, self.PORT_TO_SEND))
        while True:
            try:

                self.server.sendto(ListenServerObject.data, (self.IP_TO_SEND, self.PORT_TO_SEND))
                print(f"Speaking server speaking to {self.IP_TO_SEND}, {self.PORT_TO_SEND}")
            except AttributeError:
                continue
    def close_server(self):
        print("Server ends")
        #self.f.close()
        self.server.close()

class ListeningServer(object):
    def __init__(self, portToListen, ipToListen):

        self.listOfUsers = [] #Массив объектов пользователей

        self.HOST = "26.181.96.20"  # Standard loopback interface address (localhost)
        self.IP_TO_LISTEN = ipToListen
        self.PORT_TO_LISTEN = portToListen  # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CHUNK = 4096
        print(f"Listening Server starts")

        #self.f = wave.open("output.wav", "wb")  # Открываем файл для записи в бинарном режиме


    def createServer(self):
        pass

    def read_request(self):
        #print(f"Listening server listening: {self.address}")
        #data, address = self.server.recvfrom(self.CHUNK)
        #self.listOfUsers.append(Client(address=self.address))

        self.server.bind((self.HOST, self.PORT_TO_LISTEN))

        while True:
            data, address = self.server.recvfrom(self.CHUNK)
            print(address)
            if address[0] == self.IP_TO_LISTEN:
                self.data, self.address = self.server.recvfrom(self.CHUNK)
                if not self.data:
                    break



            #proccess1 = mp.Process(target=self.checkAndSend, args=("26.181.96.20", ))

            #proccess1.start()

            #proccess1.join()


            #self.checkAndSend("26.181.96.20")

    #def checkAndSend(self, addToCheck): #Пока что работает только на 2 клиента
        #clientsToSend = list(filter(lambda x:x.return_address()[0] == addToCheck, self.listOfUsers))
                                                                # ^^^^ когд придет Саша, поставить !=
        #self.send_request(self.data, clientsToSend[0].return_address())


    def close_server(self):
        print("Server ends")
        #self.f.close()
        self.server.close()


if __name__ == "__main__":
    ListeningServer_obj = ListeningServer(65128, "26.181.96.20")
    process1 = mp.Process(target=ListeningServer_obj.read_request)
    process1.start()

    SpeakingServer_obj = SpeakingServer("26.181.96.20", 12833)
    process2 = mp.Process(target=SpeakingServer_obj.send_request(ListeningServer_obj))
    process2.start()
