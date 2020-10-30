# Create a Simulator object
set ns [new Simulator]

# Pairs of TCP variants
set variant1 [lindex $argv 0]
set variant2 [lindex $argv 1]

# CBR rate
set rate [lindex $argv 2]

# CBR start time
set tcp1StartTime [lindex $argv 3]

# TCP2 start time
set tcp2StartTime [lindex $argv 4]

# index
set i [lindex $argv 5]

# Open the trace file
set tf [open ${variant1}_${variant2}_output-${rate}-${i}.tr w]
$ns trace-all $tf

# Define a 'finish' procedure
proc finish {} {
	global ns tf
	$ns flush-trace
	#close the Trace file
	close $tf
	exit 0
}

# Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

# Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n4 $n3 10Mb 10ms DropTail
$ns duplex-link $n6 $n3 10Mb 10ms DropTail

# Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null

# Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set rate_ ${rate}mb

# Setup a TCP conncection
if {$variant1 eq "Reno"} {
	set tcp1 [new Agent/TCP/Reno]
} elseif {$variant1 eq "NewReno"} {
	set tcp1 [new Agent/TCP/Newreno]
} elseif {$variant1 eq "Vegas"} {
	set tcp1 [new Agent/TCP/Vegas]
}

$tcp1 set class_ 1
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1

if {$variant2 eq "Reno"} {
	set tcp2 [new Agent/TCP/Reno]
} elseif {$variant2 eq "Vegas"} {
	set tcp2 [new Agent/TCP/Vegas]
}

$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2

# Setup a FTP Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1

set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2

# Schedule events for the CBR and FTP agents
$ns at 0.0 "$cbr start"
$ns at $tcp1StartTime "$ftp1 start"
$ns at $tcp2StartTime "$ftp2 start"
$ns at 25.0 "$ftp2 stop"
$ns at 25.0 "$ftp1 stop"
$ns at 25.0 "$cbr stop"

# Call the finish procedure after  seconds of simulation time
$ns at 25.0 "finish"

# Run the simulation
$ns run
