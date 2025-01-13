import rpc
import logging
import time

from context import lab_logging

### OUR CODE ###
def callback(msg):
    print("Received message from server")
    print("Content of the message:" ,msg.value)
### OUR CODE 

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)
i = 0 
while (i<20): #printing output to show that the client is still active
    print("client is waiting")
    time.sleep(1)
    i += 1

cl.stop()


