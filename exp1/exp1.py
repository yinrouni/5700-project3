import os
import random
from math import sqrt

TCP_Variant = ['Reno']

NS = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# parse each line in trace file into a dictionary
def parse(line):
    contents = line.split()
    ret = {'event': contents[0], 'time': float(contents[1]), 'from_node': contents[2], 'to_node': contents[3],
           'pkt_type': contents[4], 'pkt_size': int(contents[5]), 'flow_id': contents[7], 'src_addr': contents[8],
           'dst_addr': contents[9], 'seq_num': contents[10], 'pkt_id': contents[11]}
    return ret


def getThroughput(var, rate, i):
    """The function that get the throughput
    Args:
        var: TCP variants
        rate: CBR rate
        i: index
    Returns: 
        float return the throughput of TCP
    """
    # trece file name
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()
    # set initial data
    start_time = 200.0
    end_time = 0.0
    recvdSize = 0
    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "-" and record['from_node'] == "0":
                # get TCP flow start time
                if (record['time'] < start_time):
                    start_time = record['time']

            # get TCP flow end time
            if record['event'] == "r" and record['to_node'] == "3":
                recvdSize += record['pkt_size'] * 8
                end_time = record['time']
    # calculate troughput and return
    return recvdSize / (end_time - start_time) / 1000000


def getDropRate(var, rate, i):
    """The function that get the packet drop rate
    Args:
        var: TCP variants
        rate: CBR rate
        i: index
    Returns: 
        float return the drop rate of TCP
    """
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()
    sendNum = recvdNum = 0
    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+":
                sendNum += 1
            if record['event'] == "r":
                recvdNum += 1
    # calculate drop rate and return it
    if sendNum == 0:
        return 0
    else:
        return float(sendNum - recvdNum) / float(sendNum)

# The help function of getLatency
def latencyHelp(cxt, start_time, end_time):
    for line in cxt:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+" and record['from_node'] == "0":
                start_time.update({record['seq_num']: record['time']})
            if record['event'] == "r" and record['to_node']== "0":
                end_time.update({record['seq_num']: record['time']})

def getLatency(var, rate, i):
    """The function that get the latency of TCP
    Args:
        var: TCP variants
        rate: CBR rate
        i: index
    Returns: 
        float return the drop rate of TCP
    """
    # trace file name
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    # read data
    lines = f.readlines()
    f.close()
    # set initial data
    start_time = {}
    end_time = {}
    total_duration = 0.0
    total_packet = 0
    latencyHelp(lines, start_time, end_time)

    packets = set()
    for p in start_time.keys():
        if p in end_time.keys():
            packets.add(p)

    for i in packets:
        start = start_time[i]
        end = end_time[i]
        duration = end - start
        if duration > 0:
            total_duration += duration
            total_packet += 1
    # calculate drop rate and return it
    if total_packet == 0:
        return 0
    return total_duration / total_packet * 1000

# get mean and standard deviation in the result
def dataProcess(data):
    sum = 0
    cnt = 0
    for d in data:
        if d != 0:
            cnt += 1
            sum += d
    if (cnt == 0):
        return 0, 0
    mean = sum / cnt
    diffSqr = 0
    for d in data:
        if d != 0:
            diffSqr += (d - mean) ** 2
    stddev = sqrt(diffSqr / cnt)
    return mean, stddev


# Generate trace file
for i in range(0, 2):
    for rate in range(1, 11):
        for var in TCP_Variant:
            # Vary relative start time of 2 flows
            startTime = random.random()
            endTime = 18

            # excute the ns command
            os.system(
                NS + "exp1.tcl " + var + " " + str(rate) + " " + str(startTime) + " " + str(
                    endTime) + " " + str(i))


for var in TCP_Variant:
    f= open('exp11_' + var + '.dat', 'w')
    header = 'cbr\tthroughput\tthroughput_stddev\tlatency\tlatency_stddev\tpdr\tpdr_stddev\n'
    f.write(header)
    for rate in range(1, 11):
        throughput = []
        droprate = []
        latency = []
        for i in range(0, 2):
            throughput.append(getThroughput(var, rate, i))
            droprate.append(getDropRate(var, rate, i))
            latency.append(getLatency(var, rate, i))

        # get mean and stddev result    
        throughputRes = '\t'.join(map(str, dataProcess(throughput)))
        latencyRes = '\t'.join(map(str, dataProcess(latency)))
        droprateRes = '\t'.join(map(str, dataProcess(droprate)))

        res = str(rate) + '\t' + throughputRes + '\t' + latencyRes + '\t' + droprateRes + '\n'
        f.write(res)

    f.close()

os.system("rm *.tr")
