import os

TCP = ['Reno', 'SACK']
QUEUE = ['DropTail', 'RED']

ns_command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "
STEP = 0.5


# parse each line in trace file into a dictionary
def parse(line):
    contents = line.split()
    ret = {'event': contents[0], 'time': float(contents[1]), 'from_node': contents[2], 'to_node': contents[3],
           'pkt_type': contents[4], 'pkt_size': int(contents[5]), 'flow_id': contents[7], 'src_addr': contents[8],
           'dst_addr': contents[9], 'seq_num': contents[10], 'pkt_id': contents[11]}
    return ret


def getLatency(var, q):
    f = open(var + "-" + q + "_output.tr")
    lines = f.readlines()
    f.close()

    output = open('exp3_' + var + '_' + q + '_delay.dat', 'w')

    start_time1 = {}
    end_time1 = {}
    total_duration1 = total_duration2 = 0.0
    total_packet1 = total_packet2 = 0
    start_time2 = {}
    end_time2 = {}
    clock = 0.0

    for line in lines:
        record = parse(line)
        # CBR
        if record['flow_id'] == "0":
            if record['event'] == "+" and record['from_node'] == "4":
                start_time1.update({record['seq_num']: record['time']})
            if record['event'] == "r" and record['to_node'] == "5":
                end_time1.update({record['seq_num']: record['time']})
        # TCP
        if record['flow_id'] == "1":
            if record['event'] == "+" and record['from_node'] == "0":
                start_time2.update({record['seq_num']: record['time']})
            if record['event'] == "r" and record['to_node'] == "0":
                end_time2.update({record['seq_num']: record['time']})

        if (record['time'] - clock > STEP):
            # cbr
            packets = {x for x in start_time1.viewkeys() if x in end_time1.viewkeys()}
            for i in packets:

                duration = end_time1.get(i) - start_time1.get(i)
                if (duration > 0):
                    total_duration1 += duration
                    total_packet1 += 1
            # tcp
            packets = {x for x in start_time2.viewkeys() if x in end_time2.viewkeys()}
            for i in packets:
                duration = end_time2.get(i) - start_time2.get(i)
                if duration > 0:
                    total_duration2 += duration
                    total_packet2 += 1

            if total_packet1 == 0:
                delay1 = 0
            else:
                delay1 = total_duration1 / total_packet1 * 1000

            if total_packet2 == 0:
                delay2 = 0
            else:
                delay2 = total_duration2 / total_packet2 * 1000

            output.write(str(clock) + '\t' + str(delay1) + '\t' + str(delay2) + '\n')
            # Clear counter
            clock += STEP
            start_time1 = {}
            start_time2 = {}
            end_time1 = {}
            end_time2 = {}
            total_duration1 = total_duration2 = 0.0
            total_packet1 = total_packet2 = 0

    output.write(str(clock) + '\t' + str(delay1) + '\t' + str(delay2) + '\n')
    output.close()


def getThroughput(var, q):
    f = open(var + "-" + q + "_output.tr")
    lines = f.readlines()
    f.close()

    output = open('exp3_' + var + '_' + q + '_throughput.dat', 'w')

    clock = 0.0
    sum1 = sum2 = 0

    for line in lines:
        record = parse(line)
        if record['flow_id'] == "0" and record['event'] == "r" and record['to_node'] == "5":
            # CBR
            sum1 += record['pkt_size']
        if record['flow_id'] == "1" and record['event'] == "r" and record['to_node'] == "3":
            # TCP
            sum2 += record['pkt_size']

        if (record['time'] - clock > STEP):
            res1 = sum1 * 8 / STEP / 1000000
            res2 = sum2 * 8 / STEP / 1000000

            output.write(str(clock) + "\t" + str(res1) + "\t" + str(res2) + "\n")

            clock += STEP
            sum1 = sum2 = 0

    output.write(str(clock) + "\t" + str(res1) + "\t" + str(res2) + "\n")
    output.close()


# Generate trace files
for var in TCP:
    for q in QUEUE:
        os.system(ns_command + "exp3.tcl " + var + " " + q)

# Calculate Throughput and Latency
for var in TCP:
    for q in QUEUE:
        getThroughput(var, q)
        getLatency(var, q)

os.system('rm *.tr')
