### Abstract

### 1. Introduction
The Transmission Control Protocol (TCP) is one of the main protocols of the Internet protocol suite. TCP is
 connection-oriented, and a connection between client and server is established before data can be sent. It provides
  reliable, in-order and error-checked delivery of a stream of bytes. The final main aspect of TCP is congestion
   control. It uses a number of mechanisms to achieve high performance and congestion collapse. The mechanisms
    control the rate of data entering the network, keeping the data flow below a rate that would trigger a collapse
    . TCP uses a network congestion-avoidance algorithms that includes various aspects of an AIMD scheme, along with
     other schemes including slow start anf congestion window, to achieve congestion avoidance. The TCP congestion
     -avoidance algorithm is the primary basis for congestion control in the Internet. There are several variation
      and version of the algorithm. 
      
      In this paper, we are going to analyze the performance of these different TCP variants (Reno, NewReno, Tahoe
       Vegas and SACK).

