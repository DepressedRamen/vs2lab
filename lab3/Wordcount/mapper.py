import sys
import time
import zmq
import constWC

context=zmq.Context()

me = str(sys.argv[1])

#receive from splitter
receiver=context.socket(zmq.PULL)
receiver.connect("tcp://" + constWC.HOST + ":" + constWC.SPLITTERPORT)
print("Mapper "+me+" connected to port "+ constWC.SPLITTERPORT)

#reducer
red1 = context.socket(zmq.PUSH)
red1.connect("tcp://" + constWC.HOST + ":" + constWC.REDUCE1)
red2 = context.socket(zmq.PUSH)
red2.connect("tcp://" + constWC.HOST + ":" + constWC.REDUCE2)

print("Mapper "+ me + " started, waiting for data")
sendTo1 = 0
sendTo2 = 0
#receive data from splitter
while True:
    s = receiver.recv_string()
    #if word starts with a-m send to red1 else send to red2
    for word in s.split():
        if 97 <= ord(word[0].lower()) <= 109:
            red1.send_string(word)
            sendTo1+=1
        else:
            red2.send_string(word)
            sendTo2+=1
        print(f"Send to Reducer 1: {sendTo1} | Send to Reducer 2: {sendTo2}")
    