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
def processQue(packet_queu, time, numSuccess):
  while(packet_queu and (int(packet_queu[0][4]) + int(packet_queu[0][3]) <= time or time == -1)):
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
	if(numOfBackoffs = 0)
		timeToWait = randint(0, 15*slotTime)
	elif(numOfBackoffs >=6)
		timeToWait = randint(0, 1024*slotTime)
	else
		timeToWait = randint(0, (32 * (2 ** (numOfBackoffs-1))) * slotTime)
		#!!!!Will this actually be changed!?!?
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
waiting_qwee = deque()
outPath = outDir + "/" + outfile

numOfCollisions = 0
timeMediaUtilized = 0	#increment this by (pkt_size/dataRate) when a packet successfully sends
totalTime = 0 #set this equal to the time the last packet successfully finishes transmission
numOfTransmissions = 0 #increment each time a packet attempts transmission
numPktPerNode = []
totalLatencyPerNode = [] #increment this by "wait time" whenever a packet must wait to send

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
	  #**** line format *****
	  #packet[0] : pkt_id   *
	  #packet[1] : src_node *
	  #packet[2] : dst_node *
	  #packet[3] : pkt_size *
	  #packet[4] : time     *
	  #**********************
		
      packet = line.split()
      time = int(packet[4])
      packet.append("")
	  
		#increase list sizes if necessary
			while(len(numPktPerNode) < packet[1] + 1)
				numPktPerNode.append(0)
				totalLatencyPerNode.append(0)
				
			#count how many packets each node sends
			++numPktPerNode[packet[1]]
	
	  
      #wait DIFS time
			time = time + difsTime
			
			#process what should have happened
      numSuccess = processQue(sending_qwee, time, numOfTransmissions, numOfCollisions, timeMediaUtilized)

      # ***** Changed for csma
      # copy waiting queu to sending queu
      if not packet_queu and waiting_queu:
        packet_queu = deepcopy(waiting_queu)
        waiting_queu.clear()
        if len(packet_queu) > 1:
          for p in packet_queu:
            #print packet sending message
            of.write("Time: {} Packet: {}: {} {} {} {} start sending{}\n".format(p[4], p[0], p[1], p[2], p[3], p[4], p[5]))
            p[5] = ": collision"
        elif len(packet_queu) == 1:
          for p in packet_queu:
            #print packet sending message
            of.write("Time: {} Packet: {}: {} {} {} {} start sending{}\n".format(p[4], p[0], p[1], p[2], p[3], p[4], p[5]))
        numSuccess = processQue(packet_queu, time, numSuccess)

      # processing current packet
      if packet_queu:
        packet[4] = int(packet_queu[0][4]) + packetSize
        waiting_queu.append(packet)
      else:
        packet_queu.append(packet)
      # ***** end changed for csma

    #finish off the queu
    if waiting_queu:
        timeLastPacketFinished = int(waiting_queu[-1][4]) + packetSize
    else:
        timeLastPacketFinished = int(packet_queu[-1][4]) + packetSize
    numSuccess = processQue(packet_queu, -1, numSuccess)
    if len(waiting_queu) > 1:
        for p in waiting_queu:
          #print packet sending message
          of.write("Time: {} Packet: {}: {} {} {} {} start sending{}\n".format(p[4], p[0], p[1], p[2], p[3], p[4], p[5]))
          p[5] = ": collision"
    numSuccess = processQue(waiting_queu, -1, numSuccess)

    of.write("Packet Size: {}  NumSuccess: {}  TimeLastPacketFinished: {} \n".format(packetSize, numSuccess, timeLastPacketFinished))

statfile = outDir + "/" + outfile + ".stats"

#**** Output some statistics here ****
#throughput = (timeMediaUtilized * dataRate) / totalTime
#fracMediaFree = (totalTime - timeMediaUtilized) / totalTime
#avgLatencyPerNode = totalLatencyPerNode[i] / numPktPerNode[i]
with open(statfile, 'w') as sf:
  sf.write("{},{}\n".format(offerdLoad,throughput))