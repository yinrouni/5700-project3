import os
import random
from math import sqrt

Pairs_Of_TCP_Variants = ['Reno_Reno']

NS = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

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

    start_time1 =200.0 
    start_time2 = 200.0
    end_time1 = 0.0
    end_time2 = 0.0
    recvdSize1 = 0
    recvdSize2 = 0
    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+" and record['from_node'] == "0":
                if (record['time'] < start_time1):
                    start_time1 = record['time']
                
            if record['event'] == "r":
                recvdSize1 += record['pkt_size'] * 8
                end_time1 = record['time']
        
        if record['flow_id'] == "2":
            if record['event'] == "+" and record['from_node'] == "4":
                if (record['time'] < start_time2):
                    start_time2 = record['time']
                
            if record['event'] == "r":
                recvdSize2 += record['pkt_size'] * 8
                end_time2 = record['time']
                    
    
    throughput1 = recvdSize1 / (end_time1 - start_time1) / 1000000
    throughput2 = recvdSize2 / (end_time2 - start_time2) / 1000000
    return str(throughput1) + '\t' + str(throughput2)

def getDropRate(var, rate, i):
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()

    sendNum1 = recvdNum1 = 0
    sendNum2 = recvdNum2 = 0

    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+":
                sendNum1 += 1
            if record['event'] == "r":
                recvdNum1 += 1
        if record['flow_id'] == "2":
            if record['event'] == "+":
                sendNum2 += 1
            if record['event'] == "r":
                recvdNum2 += 1

    if sendNum1 == 0:
        droprate1 = 0
    else:
        droprate1 = float(sendNum1 - recvdNum1) / float(sendNum1)

    if sendNum2 == 0:
        droprate2 = 0
    else:
        droprate2 = float(sendNum2 - recvdNum2) / float(sendNum2)

    return str(droprate1) + '\t' + str(droprate2)



def getLatency(var, rate, i):
    filename = var + "_output-" + str(rate) + "-" + str(i) + ".tr"
    f = open(filename)
    lines = f.readlines()
    f.close()
    start_time1 = {}
    end_time1 = {}
    start_time2 = {}
    end_time2 = {}
    total_duration1 = total_duration2 = 0.0
    total_packet1 = total_packet2 = 0
    

    for line in lines:
        record = parse(line)
        if record['flow_id'] == "1":
            if record['event'] == "+" and record['from_node'] == "0":
                start_time1.update({record['seq_num'] : record['time']})
            if record['event'] == "r" and record['to_node'] == "0":
                end_time1.update({record['seq_num'] : record['time']})
                
        if record['flow_id'] == "2":
            if record['event'] == "+" and record['from_node'] == "4":
                start_time2.update({record['seq_num'] : record['time']})
            if record['event'] == "r" and record['to_node'] == "4":
                end_time2.update({record['seq_num'] : record['time']})

    packets = {}
    for p in start_time1.keys():
        if p in end_time1.keys():
            packets.add(p)
    for i in packets:
        start = start_time1[i]
        end = end_time1[i]
        duration = end - start
        if duration > 0:
            total_duration1 += duration
            total_packet1 += 1

    packets = {}
    for p in start_time2.keys():
        if p in end_time2.keys():
            packets.add(p)
    for i in packets:
        start = start_time2[i]
        end = end_time2[i]
        duration = end - start
        if(duration > 0):
            total_duration2 += duration
            total_packet2 += 1
            
            
    if total_packet1 == 0:
        latency1 = 0
    else:
        latency1 = total_duration1 / total_packet1 * 1000
    
    if total_packet2 == 0:
        latency2 = 0
    else:
        latency2 = total_duration2 / total_packet2 * 1000

    return str(latency1) + '\t' + str(latency2)

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
for var in Pairs_Of_TCP_Variants:
    for rate in range(1, 11):
        for i in range(0,10):
            tcp1_start_time = random.random()
            tcp2_start_time = random.random() * 12
            tcps = var.split('_')
            os.system(NS + "exp2.tcl " + tcps[0] + " " + tcps[1] + " " + str(rate) + " " + \
                str(tcp1_start_time) + " " +str(tcp2_start_time) + " " + str(i))


for var in Pairs_Of_TCP_Variants:
    tcps = var.split('_')
    f_throughput = open('exp2_' + var + '_throughput.dat', 'w')
    f_droprate = open('exp2_' + var + '_droprate.dat', 'w')
    f_latency = open('exp2_' + var + '_latency.dat', 'w')
    header_throughput = 'CBR\t'+tcps[0]+'_throughput\t'+tcps[0]+'_throughput_stddev\t'+tcps[1]+'_throughput\t'+tcps[1]+'_throughput_stddev\n'
    header_droprate = 'CBR\t'+tcps[0]+'_droprate\t'+tcps[0]+'_droprate_stddev\t'+tcps[1]+'_droprate\t'+tcps[1]+'_droprate_stddev\n'
    header_latency = 'CBR\t'+tcps[0]+'_latency\t'+tcps[0]+'_latency_stddev\t'+tcps[1]+'_latency\t'+tcps[1]+'_latency_stddev\n'

    f_throughput.write(header_throughput)
    f_droprate.write(header_droprate)
    f_latency.write(header_latency)

    for rate in range(1, 11):
        throughput1 = []
        throughput2 = []
        droprate1 = []
        droprate2 = []
        latency1 = []
        latency2 =[]
        for i in range(0, 10):
            throughput = getThroughput(var, rate, i).split('\t')
            droprate = getDropRate(var, rate, i).split('\t')
            latency = getLatency(var, rate, i).split('\t')

            throughput1.append(float(throughput[0]))
            throughput2.append(float(throughput[1]))
            droprate1.append(float(droprate[0]))
            droprate2.append(float(droprate[1]))
            latency1.append(float(latency[0]))
            latency2.append(float(latency[1]))
        
        throughput1_res = '\t'.join(map(str, dataProcess(throughput1)))
        throughput2_res = '\t'.join(map(str, dataProcess(throughput2)))
        droprate1_res = '\t'.join(map(str, dataProcess(droprate1)))
        droprate2_res = '\t'.join(map(str, dataProcess(droprate2)))
        latency1_res = '\t'.join(map(str, dataProcess(latency1)))
        latency2_res = '\t'.join(map(str, dataProcess(latency2)))

        throughput_res = str(rate) + '\t' + throughput1_res + '\t' + throughput2_res + '\n'
        droprate_res = str(rate) + '\t' + droprate1_res + '\t' + droprate2_res + '\n'
        latency_res = str(rate) + '\t' + latency1_res + '\t' + latency2_res + '\n'

        f_throughput.write(throughput_res)
        f_droprate.write(droprate_res)
        f_latency.write(latency_res)
    f_throughput.close
    f_droprate.close
    f_latency.close    
os.system("rm *.tr")

