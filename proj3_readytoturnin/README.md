# wifi
Simulation of 802.11 DCF MAC protocol and 802.11 with RTS/CTS

Make scripts executable:
$ chmod a+x generator.py

Generator Script
$ ./generator.py -h
usage: generator [-h] [-n NUM_NODE] [-P PKT_SIZE] [-l OFFERED_LOAD]
[-p NUM_PKTS_PER_NODE] [-s SEED] [-o OUTFILE] [-e]

Generate simulated traffic and outputs to file.

optional arguments:
-h, --help            show this help message and exit
-n NUM_NODE, --num_node NUM_NODE
number of nodes that Tx & Rx
-P PKT_SIZE, --pkt_size PKT_SIZE
packet size
-l OFFERED_LOAD, --offered_load OFFERED_LOAD
offered load 0.01&to&10
-p NUM_PKTS_PER_NODE, --num_pkts_per_node NUM_PKTS_PER_NODE
number of packets per node
-s SEED, --seed SEED  seed for random function
-o OUTFILE, --outfile OUTFILE
traffic file
-e, --exponential     exponential distribution

Simulators

$ ./dcf.py -h
usage: DCF [-h] [-t TRAFFICFILE] [-o OUTFILE]

Simulates the 802.11 DCF MAC protocol for a given traffic file.

optional arguments:
-h, --help                                            show this help message and exit
-t TRAFFICFILE, --trafficfile TRAFFICFILE             traffic file
-o OUTFILE, --outfile OUTFILE                         output file

$ ./rts_cts.py -h
usage: DCF [-h] [-t TRAFFICFILE] [-o OUTFILE]

Simulates the 802.11 DCF MAC protocol for a given traffic file.

optional arguments:
-h, --help                                            show this help message and exit
-t TRAFFICFILE, --trafficfile TRAFFICFILE             traffic file
-o OUTFILE, --outfile OUTFILE                         output file

To compile statistics from the stat files:
create a csv file and concatenate the stat files ex:
$ echo "offerdLoad,throughput,numOfTransmissions,numOfCollisions,fracMediaFree,numPktPerNode,avgLatencyPerNode" > rts_ctsExpo.csv
$ cat output/rts_cts/expo/*.stats >> rts_ctsExpo.csv

For better efficiency use the parrallel package to maximize all available cpu cores:

parallel --bar --no-notice ./rts_cts.py -t traffic/expo/traffic{} -o output/rts_cts/expo/out{} :::: load_seq.txt
