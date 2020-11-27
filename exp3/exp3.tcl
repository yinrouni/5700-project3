# Create a Simulator object
set ns [new Simulator]

# TCP var
set tcp_var [lindex $argv 0]
# Queue var
set q_var [lindex $argv 1]

# Open the trace file
set tf [open ${tcp_var}-${q_var}_output.tr w]
$ns trace-all $tf

# Define a 'finish' procedure
proc finish {} {
	global ns tf
	$ns flush-trace
	close $tf
	exit 0
}

# create 6 nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#create links between the nodes
if {$q_var eq "DropTail"} {
	$ns duplex-link $n1 $n2 10Mb 10ms DropTail
	$ns duplex-link $n2 $n3 10Mb 10ms DropTail
	$ns duplex-link $n5 $n2 10Mb 10ms DropTail
	$ns duplex-link $n3 $n4 10Mb 10ms DropTail
	$ns duplex-link $n3 $n6 10Mb 10ms DropTail
} elseif {$q_var eq "RED"} {
	$ns duplex-link $n1 $n2 10Mb 10ms RED
	$ns duplex-link $n2 $n3 10Mb 10ms RED
	$ns duplex-link $n5 $n2 10Mb 10ms RED
	$ns duplex-link $n3 $n4 10Mb 10ms RED
	$ns duplex-link $n3 $n6 10Mb 10ms RED
}

#set queue size
$ns queue-limit	$n1 $n2 10
$ns queue-limit	$n5 $n2 10
$ns queue-limit	$n2 $n3 10
$ns queue-limit	$n3 $n4 10
$ns queue-limit	$n3 $n6 10

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set rate_ 6mb
$cbr set fid_ 0
$cbr set packet_size_ 1000
$cbr set random_ false

#Setup a TCP conncection
if {$tcp_var eq "Reno"} {
	set tcp [new Agent/TCP/Reno]
	set sink [new Agent/TCPSink]
} elseif {$tcp_var eq "SACK"} {
	set tcp [new Agent/TCP/Sack1]
	set sink [new Agent/TCPSink/Sack1]
}
$tcp set class_ 1
$ns attach-agent $n1 $tcp
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1
$tcp set window_ 100

#setup a FTP Application
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0.0 "$ftp start"
$ns at 60.0 "$cbr start"
$ns at 120.0 "$cbr stop"
$ns at 180.0 "$ftp stop"

#Call the finish procedure after  seconds of simulation time
$ns at 182.0 "finish"

#Run the simulation
$ns run