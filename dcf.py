#!/usr/bin/python
'''
Grady Denton & Shane Bennett for proj3 in cnt5505 data comm
'''

#***Check to make sure we need all these***
#from __future__ import division
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

#ceiling division
def ceildiv(a, b):
  return -(-a // b)

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
      packet = [int(x) for x in packet]

      while(numNodes < packet[1] + 1):
        numPktPerNode.append(0)
        waiting_qwee.append(deque())
        numNodes = numNodes + 1

      #count number of packets sent by each node
      ++numPktPerNode[packet[1]]

      packet.append(9999)  #time_to_backoff
      packet.append(0)  #num_backoffs

      waiting_qwee[packet[1]].append(packet)
    #^^^^^^^^^^^^^^^^End of Reading File^^^^^^^^^^^^^^^^

    #increment this by "wait time" whenever a packet must wait to send
    #per node statistic
      totalLatencyPerNode = [0] * numNodes

    #**** waiting_qwee format *****************
      #waiting_qwee[i][0][0] : pkt_id           *
      #waiting_qwee[i][0][1] : src_node         *
      #waiting_qwee[i][0][2] : dst_node         *
      #waiting_qwee[i][0][3] : pkt_size         *
      #waiting_qwee[i][0][4] : time             *
      #waiting_qwee[i][0][5] :                  *
      #waiting_qwee[i][0][6] : num_backoffs     *
      #******************************************

      #******************** Real Meaty Code ********************
    #networkState[nodeID] = [currentStatusType, timeTillNextThing, slotsLeft, normal/freezed/backoff]
    networkState = [[0, 0, 0, 0] for i in range(numNodes)]
    #currentStatusType
      #0 -- waiting for packet from application
      #1 -- waiting for DIFS
      #2 -- waiting for slots
      #3 -- waiting for packet transmission
      #4 -- waiting for packet ACK

    #Printout statements we need
      #Node x had y more slots when the channel became busy!

    #set the next event for each node to be when first packet for that node arrives
    for i in range(numNodes):
      if(waiting_qwee[i]):
        networkState[i][1] = waiting_qwee[i][0][4]
      else:
        networkState[i][1] = 999999999

    isBusy = 0	#whether medium is currently sending
    numSending = 0 #how many node currently transmitting
    collision = 0 #whether we collided
    time = 0
    #******************** A Wild Main Loop Appears! ********************
    while(1):
      #------------find the next event------------
      #if medium isn't busy then any event can win
      #but node starting to send takes least precedence
      collision = 0
      shortestTime = 999999999
      for i in range(numNodes):
        if(waiting_qwee[i]):
          if(not isBusy):
            if(networkState[i][1] < shortestTime):
              shortestTime = networkState[i][1]
              nodeWhoGetsTurn = i
            elif(networkState[i][1] == shortestTime and networkState[nodeWhoGetsTurn][0] == 2):
              nodeWhoGetsTurn = i             
          else: #isBusy
            if(networkState[i][1] < shortestTime and (networkState[i][0] != 1 or networkState[i][0] != 2) ):
              shortestTime = networkState[i][1]
              nodeWhoGetsTurn = i
      #if no more events we are done
      if(shortestTime == 999999999):
        break
      #update current time
      oldtime = time
      time = time + networkState[nodeWhoGetsTurn][1]

      #|||||||Process the Event|||||||
      #if node is starting to wait for DIFS
      if(networkState[nodeWhoGetsTurn][0] == 0):
        if(networkState[nodeWhoGetsTurn][2] != 0):
          of.write("Time: {} Node {} had {} more slots when the channel became busy!\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1]), networkState[nodeWhoGetsTurn][2])
        of.write("Time: {} Node {} started waiting for DIFS\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1]))
      #if node has finished waiting for DIFS
      elif(networkState[nodeWhoGetsTurn][0] == 1):
        #check if node already picked slots
        if(networkState[nodeWhoGetsTurn][2] == 0):
          networkState[nodeWhoGetsTurn][1] = binExpBackoff(waiting_qwee[nodeWhoGetsTurn][0][6], slotTime, totalLatencyPerNode, waiting_qwee[nodeWhoGetsTurn][0][1])
          ++waiting_qwee[nodeWhoGetsTurn][0][6]
        else:
          networkState[nodeWhoGetsTurn][1] = networkState[nodeWhoGetsTurn][2]
          networkState[nodeWhoGetsTurn][2] = 0
        #if node was not interrupted
        if(networkState[nodeWhoGetsTurn][3] == 0):
          of.write("Time: {} Node {} finished waiting for DIFS and started waiting for {} slots\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1], networkState[nodeWhoGetsTurn][1]/slotTime))
        #if node was freezed
        elif(networkState[nodeWhoGetsTurn][3] == 1):
          of.write("Time: {} Node {} finished waiting for DIFS and started waiting for {} slots (counter was frozen)\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1], networkState[nodeWhoGetsTurn][1]/slotTime))
          networkState[nodeWhoGetsTurn][3] = 0
        #if node did backoff
        elif(networkState[nodeWhoGetsTurn][3] == 2):
          of.write("Time: {} Node {} finished waiting for DIFS and started waiting for {} slots (back off after collision)\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1], networkState[nodeWhoGetsTurn][1]/slotTime))
      #if node has finished waiting for slots
      elif(networkState[nodeWhoGetsTurn][0] == 2):
        of.write("Time: {} Node {} finished waiting and is ready to send the packet.\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1]))
      #if node has finished waiting for transmission
      elif(networkState[nodeWhoGetsTurn][0] == 3):
        if(collision)
          of.write("Time: {} Node {} has detected a collision\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1], waiting_qwee[nodeWhoGetsTurn][0][3]))
      #if node has finished waiting for ACK
      elif(networkState[nodeWhoGetsTurn][0] == 3):
        of.write("Time: {} Node {} sent {} bits\n".format(time, waiting_qwee[nodeWhoGetsTurn][0][1], waiting_qwee[nodeWhoGetsTurn][0][3]))

      #--------------UPDATE NETWORKSTATE--------------
      #update all the other nodes
      for i in range(numNodes):
        if(waiting_qwee[i] and i != nodeWhoGetsTurn):
            if(isBusy):
              if(networkState[i][1] == 0 and networkState[i][1] == 3 and networkState[i][1] == 4):
                networkState[i][1] = networkState[i][1] - (time-oldtime)
            else: #if not Busy
              networkState[i][1] = networkState[i][1] - (time-oldtime)
              if(networkState[nodeWhoGetsTurn][0] == 2):
                if(networkState[i][0] == 2):
                  networkState[i][2] = (ceildiv(networkState[i][1],slotTime)) * slotTime
                  networkState[i][0] = 0
                  networkState[i][1] = 0
                elif(networkState[i][0] == 1):
                  networkState[i][0] = 0
                  networkState[i][1] = 0
      #update the node who got the turn
      if(networkState[nodeWhoGetsTurn][0] == 0):	#if done waiting for packet
        networkState[nodeWhoGetsTurn][0] = 1
        networkState[nodeWhoGetsTurn][1] = difsTime
      elif(networkState[nodeWhoGetsTurn][0] == 1):	#if done waiting for DIFS
        networkState[nodeWhoGetsTurn][0] = 2
      elif(networkState[nodeWhoGetsTurn][0] == 2):	#if done waiting for slots
        networkState[nodeWhoGetsTurn][0] = 3
        networkState[nodeWhoGetsTurn][1] = ceildiv(waiting_qwee[nodeWhoGetsTurn][0][3],dataRate)
        networkState[nodeWhoGetsTurn][2] = 0
        isBusy = 1
        ++sending
        if(sending > 0)
          collision = 1
      elif(networkState[nodeWhoGetsTurn][0] == 3):	#if done waiting for transmission
        if(collision) #do binary backoff and reset to waiting for DIFS
          networkState[nodeWhoGetsTurn][2] = binExpBackoff(waiting_qwee[nodeWhoGetsTurn][0][6], slotTime, totalLatencyPerNode, waiting_qwee[nodeWhoGetsTurn][0][1])
          ++waiting_qwee[nodeWhoGetsTurn][0][6]
          networkState[nodeWhoGetsTurn][0] = 0
          networkState[nodeWhoGetsTurn][0] = 0
          --sending
          if(sending == 0)
            collision = 0
            isBusy = 0
        else #no collision
          networkState[nodeWhoGetsTurn][0] = 4
          networkState[nodeWhoGetsTurn][1] = sifsTime + ackTime
      elif(networkState[nodeWhoGetsTurn][0] == 4):	#if done waiting for ACK
        waiting_qwee[nodeWhoGetsTurn].popleft()
        networkState[nodeWhoGetsTurn][0] = 0
        isBusy = 0
        if waiting_qwee[nodeWhoGetsTurn]:
          if(waiting_qwee[nodeWhoGetsTurn][0][4] <= time):
            networkState[nodeWhoGetsTurn][1] = 0
          else:
            networkState[nodeWhoGetsTurn][1] = time - waiting_qwee[nodeWhoGetsTurn][0][4]
        else:
          networkState[nodeWhoGetsTurn][1] = 999999999

    #of.write("Time: {} Packet: {}: {} {} {} {} start sending{}\n".format(p[4], p[0], p[1], p[2], p[3], p[4], p[5]))
    #of.write("Packet Size: {}  NumSuccess: {}  TimeLastPacketFinished: {} \n".format(packetSize, numSuccess, timeLastPacketFinished))

statfile = outDir + "/" + outfile + ".stats"

#**** Output some statistics here ****
#throughput = (timeMediaUtilized * dataRate) / totalTime
#fracMediaFree = (totalTime - timeMediaUtilized) / totalTime
#avgLatencyPerNode = totalLatencyPerNode[i] / numPktPerNode[i]
#with open(statfile, 'w') as sf:
  #sf.write("{},{}\n".format(offerdLoad,throughput))