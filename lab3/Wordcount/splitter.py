import zmq
import random
import constWC
import re
import time
import sys


context=zmq.Context()
push_socket = context.socket(zmq.PUSH)
push_socket.bind("tcp://" + constWC.HOST + ":" + constWC.SPLITTERPORT)

print("Splitter starts")

#open file, read lines and save as list
content=[]
with open("words.txt") as file:
  for line in file.readlines():
     content.append(line.strip())

#wait for all mappers to connect
time.sleep(20)

#iterate over lines
for i,line in enumerate(content):
  #lines in lowercase and wihtout special characters
  line = line.lower()
  line = re.sub('[!@#$:,.„“,?]', '', line)
  #send line to the mappers
  print(line)
  push_socket.send_string(line)

