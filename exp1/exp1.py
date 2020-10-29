import os
import random
from math import sqrt

TCP_Variant = ['Reno', 'NewReno', 'Tahoe', 'Vegas']

ns_command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# parse each line in trace file into a dictionary
def parse(line):
    contents = line.split()
    ret = {'event': contents[0], 'time': float(contents[1]), 'from_node': contents[2], 'to_node': contents[3],
           'pkt_type': contents[4], 'pkt_size': int(contents[5]), 'flow_id': contents[7], 'src_addr': contents[8],
           'dst_addr': contents[9], 'seq_num': contents[10], 'pkt_id': contents[11]}
    return ret


def getThroughput(var, rate, i):
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()
    start_time = 200.0
    end_time = 0.0
    recvdSize = 0
    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            # print(line)
            if record['event'] == "+" and record['from_node'] == "0":
                if (record['time'] < start_time):
                    start_time = record['time']

            if record['event'] == "r":
                recvdSize += record['pkt_size'] * 8
                end_time = record['time']
    # print('DEBUG:' + str(recvdSize) + ' ' + str(end_time) + ' ' + str(start_time))
    return recvdSize / (end_time - start_time) / 1000000


def getDropRate(var, rate, i):
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
    if sendNum == 0:
        return 0
    else:
        return float(sendNum - recvdNum) / float(sendNum)


def getLatency(var, rate, i):
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()
    start_time = {}
    end_time = {}
    total_duration = 0.0
    total_packet = 0
    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+" and record['from_node'] == "0":
                start_time.update({record['seq_num']: record['time']})
            if record['event'] == "r" and record['to_node']== "0":
                end_time.update({record['seq_num']: record['time']})
    packets = {x for x in start_time.viewkeys() if x in end_time.viewkeys()}
    for i in packets:
        start = start_time[i]
        end = end_time[i]
        duration = end - start
        if duration > 0:
            total_duration += duration
            total_packet += 1
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
    mean = sum / cnt
    diffSqr = 0
    for d in data:
        if d != 0:
            diffSqr += (d - mean) ** 2
    stddev = sqrt(diffSqr / cnt)
    return mean, stddev


# Generate trace file
for var in TCP_Variant:
    for rate in range(1, 11):
        for i in range(0, 10):
            # Vary relative start time of 2 flows
            startTime = random.random() * 20
            # print(startTime)
            endTime = 100
            # print(startTime, endTime)
            os.system(
                ns_command + "exp1.tcl " + var + " " + str(rate) + " " + str(startTime) + " " + str(
                    endTime) + " " + str(i))


for var in TCP_Variant:
    f= open('exp11_' + var + '.dat', 'w')
    header = 'cbr\tthroughput\tthroughput_stddev\tlatency\tlatency_stddev\tpdr\tpdr_stddev\n'
    f.write(header)
    for rate in range(1, 11):
        throughput = []
        droprate = []
        latency = []
        for i in range(0, 10):
            throughput.append(getThroughput(var, rate, i))
            droprate.append(getDropRate(var, rate, i))
            latency.append(getLatency(var, rate, i))
        # print(throughput)
        throughputRes = '\t'.join(map(str, dataProcess(throughput)))
        latencyRes = '\t'.join(map(str, dataProcess(latency)))
        droprateRes = '\t'.join(map(str, dataProcess(droprate)))

        res = str(rate) + '\t' + throughputRes + '\t' + latencyRes + '\t' + droprateRes + '\n'
        f.write(res)

    f.close()

os.system("rm *.tr")
