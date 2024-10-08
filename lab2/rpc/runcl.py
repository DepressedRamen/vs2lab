import rpc
import logging

from context import lab_logging

def callback(msg):
    print("Ergebnis in Callback-Funktion")
    print("Inhalt der Nachricht :" ,msg.value)

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)
cl.stop()


