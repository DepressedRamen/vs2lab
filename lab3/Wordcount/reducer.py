import sys
import time
import zmq
import pprint
import constWC

pp = pprint.PrettyPrinter(indent=4)
context = zmq.Context()


me = str(sys.argv[1])
port = ""

#bind to corresponding port
if me == "1":
    port = constWC.REDUCE1
elif me == "2":
    port = constWC.REDUCE2

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://" + constWC.HOST + ":" + port)
print("Reducer "+me+" connected to port "+ port)

#receive data from mapper and count the words
map = {}
while True:
    s = receiver.recv_string()
    if s not in map:
        map[s] = 1
    else:
        map[s] += 1
    print("###########################")
    pp.pprint(map)