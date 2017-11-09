#!/usr/bin/python
'''
Grady Denton & Shane Bennet for proj2 in cnt5505 data comm
'''
from __future__ import division
import argparse
import os
from random import *

# Function definitions
def next_time(curr_time):
  curr_gap = randint(0, 2*gap)
  return curr_time + Tx_time + curr_gap

def des_node(src_node):
  destination = randint(0, num_node-1)
  while destination == src_node:
    destination = randint(0, num_node-1)
  return destination


# set up arguments
parser = argparse.ArgumentParser(prog='generator', description='Generate simulated traffic and outputs to file.')
parser.add_argument("-n","--num_node", help="number of nodes that Tx & Rx", default="2")
parser.add_argument("-P","--pkt_size", help="packet size", default="1")
parser.add_argument("-l","--offered_load", help="offered load 0.01&to&10", default="1")
parser.add_argument("-p","--num_pkts_per_node", help="number of packets per node", default="1")
parser.add_argument("-s","--seed", help="seed for random function", default=None)
parser.add_argument("-o","--outfile", help="traffic file", default=os.path.join(os.getcwd(), "traffic"))
args = parser.parse_args()

# check arguments

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

# MAIN FUNCTION

# Vars
outPath = outDir + "/" + outfile
global num_node
num_node = int(args.num_node)
pkt_size = int(args.pkt_size)
offered_load = float(args.offered_load)
num_pkts_per_node = int(args.num_pkts_per_node)
if args.seed == None:
  mySeed = args.seed
else:
  mySeed = int(args.seed)
tot_packets = num_node * num_pkts_per_node
global gap
gap = int((pkt_size * num_node / offered_load) - pkt_size)
global Tx_time
Tx_time = pkt_size
global packet_table
packet_table = []

# do stuff
seed(mySeed)
for i in range(num_node):
  curr_time = randint(0, 2*gap)
  packet_table.append([i, i, des_node(i), pkt_size, curr_time])
  for j in range(1, num_pkts_per_node):
    curr_time = next_time(curr_time)
    packet_table.append([i+j*num_node, i, des_node(i), pkt_size, curr_time])

# finish
packet_table.sort(key=lambda x: int(x[4]))
with open(outPath, 'w') as of:
  of.write("{} {}\n".format(tot_packets,offered_load))
  for row in packet_table:
    of.write("{} {} {} {} {}\n".format(row[0], row[1], row[2], row[3], row[4]))
