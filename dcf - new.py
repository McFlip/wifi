#!/usr/bin/python
'''
Grady Denton & Shane Bennett for proj3 in cnt5505 data comm
'''

#***Check to make sure we need all these***
from __future__ import division
import argparse
import os
from collections import deque
from copy import deepcopy
from random import *

#*** Function definitions ***
def processQue(sending_qwee, time, numOfTransmissions, numOfCollisions, timeMediaUtilized):
  while(sending_qwee and (int(packet_qwee[0][4]) + int(packet_qwee[0][3]) <= time or time == -1)):
    if packet_queu[0][5] == ": collision":
      finish = "finish sending: failed"
    else:
      finish = "finish sending: successfully transmitted"
      numSuccess = numSuccess + 1
    of.write("Time: {} Packet: {}: {} {} {} {} {}\n".format(int(packet_queu[0][4]) + int(packet_queu[0][3]), packet_queu[0][0], packet_queu[0][1], packet_queu[0][2], packet_queu[0][3], packet_queu[0][4], finish))
    packet_queu.popleft()
  return numSuccess

#returns a time 0 to 15 at first
#numBackOffs increments when an ack is not received
def binExpBackoff(numOfBackoffs, slotTime, totalLatencyPerNode, src_node):
  if(numOfBackoffs == 0):
    timeToWait = randint(0, 15*slotTime)
  elif(numOfBackoffs >=6):
    timeToWait = randint(0, 1024*slotTime)
  else:
    timeToWait = randint(0, (32 * (2 ** (numOfBackoffs-1))) * slotTime)
    #!!!!Will this value actually be changed!?!?
  totalLatencyPerNode[src_node] = totalLatencyPerNode[src_node] + timeToWait
  return timeToWait

#*** set up arguments ***
parser = argparse.ArgumentParser(prog='DCF', description='Simulates the 802.11 DCF MAC protocol for a given traffic file.')
parser.add_argument("-t","--trafficfile", help="traffic file", default=os.path.join(os.getcwd(), "traffic"))
parser.add_argument("-o","--outfile", help="output file", default=os.path.join(os.getcwd(), "DCF.out"))
args = parser.parse_args()

#*** check arguments ***
trafficfile = os.path.expanduser(args.trafficfile)
if not os.path.exists(trafficfile):
  parser.error('The trafficfile file does not exist!')
if not os.path.isfile(trafficfile):
  parser.error('The trafficfile file is not a file!')
if not os.access(trafficfile, os.R_OK):
  parser.error('The trafficfile file is not readable!')

outfile = os.path.basename(os.path.expanduser(args.outfile))
outDir = os.path.dirname(os.path.expanduser(args.outfile))
if not outDir:
  outDir = os.getcwd()
if not os.path.exists(outDir):
  parser.error('The out dir does not exist!')
if not os.path.isdir(outDir):
  parser.error('The out dir is not a directory!')
if not os.access(outDir, os.W_OK):
  parser.error('The outDir dir is not writable!')

#****** MAIN FUNCTION ******

#*** Vars ***
sending_qwee = deque()
waiting_qwee = [deque()]
outPath = outDir + "/" + outfile

numNodes = 0
numOfCollisions = 0
timeMediaUtilized = 0	#increment this by (pkt_size/dataRate) when a packet successfully sends
totalTime = 0 #set this equal to the time the last packet successfully finishes transmission
numOfTransmissions = 0 #increment each time a packet attempts transmission
numPktPerNode = []
totalLatencyPerNode = [] #increment this by "wait time" whenever a packet must wait to send
currTime = 0 #current time

dataRate = 6	#Mbps, 6 bits are sent per microsecond
ackTime = 44	#us
slotTime = 9	#us
difsTime = 28	#us
sifsTime = 10	#us

# do stuff
with open(outPath, 'w') as of:
  with open(trafficfile, 'r') as tf:
    stats = tf.readline()
    stats = stats.split()
    numPackets = int(stats[0])
    #offerdLoad = float(stats[1])

    for line in tf:
    #**** line format *************
    #packet[0] : pkt_id           *
    #packet[1] : src_node         *
    #packet[2] : dst_node         *
    #packet[3] : pkt_size         *
    #packet[4] : time             *
    #packet[5] : time_to_backoff  *
    #packet[6] : num_backoffs     *
    #******************************

      packet = line.split()
      
      while(numNodes < packet[1] + 1):
        numPktPerNode.append(0)
        waiting_qwee.append(deque())
        numNodes = numNodes + 1
      
      #count number of packets sent by each node
      ++numPktPerNode[packet[1]]
      
      packet.append(9999)  #time_to_backoff 
      packet.append(0)  #num_backoffs
      
      waiting_qwee[packet[1]].append(packet)
    #^^^^End of Reading File^^^^
     
    #set list size
    totalLatencyPerNode.append('0' * 100)

    
    #******************** Main Loop Starts Here ********************
    isBusy = 0
    multipleEvents = 0
    time = max_int
    nextEventType = 0 
      #0 -- Node x started waiting for DIFS
      #1 -- Node x finished waiting for DIFS and started waiting for y slots
      #2 -- Node x finished waiting and is ready to send the packet.
      #3 -- Node x had y more slots when the channel became busy!
      #4 -- Node x sent z bits
    while(1)
      #find the next event
      oldtime = time
      time = waiting_qwee[i][0][4]
      for(i = 0; i < numNodes; ++i)
        if(waiting_qwee[i][0][4] < time
          time = waiting_qwee[i][0][4]
          slotDone = 0
        elif(not isBusy and (oldTime + waiting_qwee[i][0][5])) < time)
          time = oldTime + waiting_qwee[i][0][5]
          slotsDone = 1
        elif(waiting_qwee[i][0][4] == time)
          multipleEvents = 1
          
      multipleEvents = 0
        
    
      if(isBusy)
        
      else
        lowestSlots = 9999
        #all nodes waiting countdown
        for(i = 0; i < numNodes; ++i):
          if(waiting_qwee[i][0][5] < lowestSlots)
            lowestSlots = waiting_qwee[i][0][5]
            nextEvent = i
        for(i = 0; i < numNodes; ++i): 
          waiting_qwee[i][0][5] = waiting_qwee[i][0][5] - lowestSlots
        for(i = 0; i < numNodes; ++i):
          if(waiting_qwee[i][0][5] == 0)
            sending_qwee.append(waiting_qwee[i][0])
            isBusy = 1
    #Node x started waiting for DIFS
    of.write("Time: {} Node {} started waiting for DIFS\n".format(time, packet[1]))
    
    #wait DIFS time
    time = time + difsTime
    packet[5] = binExpBackoff(packet[6], slotTime, totalLatencyPerNode, src_node)


  #of.write("Time: {} Packet: {}: {} {} {} {} start sending{}\n".format(p[4], p[0], p[1], p[2], p[3], p[4], p[5]))
  #of.write("Packet Size: {}  NumSuccess: {}  TimeLastPacketFinished: {} \n".format(packetSize, numSuccess, timeLastPacketFinished))

statfile = outDir + "/" + outfile + ".stats"

#**** Output some statistics here ****
#throughput = (timeMediaUtilized * dataRate) / totalTime
#fracMediaFree = (totalTime - timeMediaUtilized) / totalTime
#avgLatencyPerNode = totalLatencyPerNode[i] / numPktPerNode[i]
with open(statfile, 'w') as sf:
  sf.write("{},{}\n".format(offerdLoad,throughput))