import constRPC
import threading
import time

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list, callback):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        
        msgrcv_ack = self.chan.receive_from(self.server) # type: ignore
        print("Ergebnis der Ack-Antwort: ", msgrcv_ack[1])

        thread = AsyncAppend(self.chan, self.server, callback) #make append obj.
        thread.start()      #start thread
        i = 0 
        while (not thread.done): #printing output to show that the client is still active
            print("client is waiting")
            time.sleep(1)
        thread.join()            
        
        """msgrcv = self.chan.receive_from(self.server)  # wait for response
        return msgrcv[1]  # pass it to caller"""

class AsyncAppend(threading.Thread):
    def __init__(self, chan, server, callback):
        threading.Thread.__init__(self)
        self.chan = chan
        self.server = server
        self.done = False
        self.callback = callback

    def run(self):
        print('asynch_append start receive')
        # wait for response --> Hier Thread
        msgrcv = self.chan.receive_from(self.server) # receive response
        print('asynch_append receive done') 
        self.done = True
        self.callback(msgrcv[1]) # call callback function

class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                # check what is being requested
                if constRPC.APPEND == msgrpc[0]:
                    # server received request
                    self.chan.send_to({client}, "acknowledge")
                    # wait 10 seconds to simulate prolonged processing time
                    for i in range(10):
                        print("Server is working")
                        time.sleep(1)
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore