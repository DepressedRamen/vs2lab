"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    _data=dict()
    _data={
        "Kevin": "123-456-7890",
        "Tim": "456-789-0123",
        "Chris": "789-012-3456",
        "Maxi": "012-345-6789",
        "Lex": "234-567-8901",
        "Max": "345-678-9012",
        "Tom": "456-789-0123",
        "Hanka": "567-890-1234",
        "Victoria": "678-901-2345",
        "Ailana": "789-012-3456",
        "Katrin": "890-123-4567",
        "Karsten": "901-234-5678",
        "Joachim": "012-345-6789",
        "Gertrud": "123-456-7890",
        "Moritz": "234-567-8901",
        "David": "345-678-9012",
        "Mohammed": "456-789-0123",
        "Abdel": "567-890-1234",
        "Christian": "678-901-2345",
        "Patrick": "789-012-3456",
        "Johannes": "890-123-4567",
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        self._logger.info("Server started")
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    connection.send(data + "*".encode('ascii'))  # return sent data plus an "*"
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

    def receiveGet(self): 
        self.sock.listen(1)
        self._logger.info("Server started")
        
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
                try:
                    # pylint: disable=unused-variable
                    (connection, address) = self.sock.accept()  # returns new socket and address of client
                    while True:  # forever
                        data = connection.recv(1024)  # receive data from client
                        if not data:
                            break  # stop if client stopped
                        name = data.decode('utf-8')
                        if name == "getall": #return complete directoy
                            self._logger.info('GET_ALL')
                            phone_list = []
                            for name, number in self._data.items(): #iterate through dictionary and append to list
                                phone_list.append(f'{name, number}')
                            phone_list_str = "\n".join(phone_list)      
                            connection.send(phone_list_str.encode('utf-8')) #send list as string
                        else: #return number for given name
                            self._logger.info(f'GET {name}')
                            connection.send(self._data.get(name,'not found').encode('utf-8')) 
                except socket.timeout:
                    pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def close(self):
        """ Close socket """
        self.sock.close()
        
    def send(self,msg_in='Tim'):
        """ Send message to server """
        self.logger.info("Client sent: " + msg_in)
        self.sock.send(msg_in.encode('utf-8')) # send message to server
        data=self.sock.recv(1024)
        self.logger.info("Client received: " + str(data))
        msg_out=data.decode('utf-8') # decode message from server
        print("\n"+msg_out+"\n") # print message
        return msg_out

    def get(self,msg_in=''):
        """ Get number for name """
        if msg_in=='': #if no name is given, ask for name
            msg_in=input("Enter name: ") # ask for name 
        return self.send(msg_in)
    
    def getall(self):
        """ Get all numbers"""
        return self.send('getall')
