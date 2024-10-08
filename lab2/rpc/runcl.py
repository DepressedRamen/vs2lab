import rpc
import logging

from context import lab_logging

def callback(msg):
    print("Received message from server")
    print("Content of the message:" ,msg.value)

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)
cl.stop()


