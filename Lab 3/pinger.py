#!/usr/bin/python

from socket import *
from optparse import OptionParser
import os, sys, struct, time, string, select, binascii



# Stats
send_count = 0
recv_count = 0
rtt_min = sys.maxint
rtt_max = 0.0
rtt_list = []
remote_host = None

DUMMY_PORT = 1

# Print out the buffer
def print_buffer(buf):
    ba = bytearray(buf)

    for b in ba:
        sys.stdout.write("%02X " % b)
    print



class ICMP:
    """
    ICMP Header

    bits
    0-7     Type
    8-15    Code
    16-31   Checksum
    32-64   Type/Code dependent
    """

    def __init__(self, **kwargs):

        self.type     = kwargs.get("type",     0)
        self.code     = kwargs.get("code",     0)
        self.checksum = kwargs.get("checksum", 0)
        self.extra    = kwargs.get("extra",    struct.pack("I", 0))
        self.data     = kwargs.get("data",     0)

    def _checksum(self, data):
        csum = 0
        countTo = (len(data) / 2) * 2
        count = 0
        while count < countTo:
            thisVal = ord(data[count+1]) * 256 + ord(data[count])
            csum = csum + thisVal
            csum = csum & 0xffffffffL
            count = count + 2
        if countTo < len(data):
            csum = csum + ord(data[len(data) - 1])
            csum = csum & 0xffffffffL
        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)

        # Get the right checksum, and put in the header
        if sys.platform == 'darwin':
            answer = htons(answer) & 0xffff
        else:
            answer = htons(answer)

        return answer        


    def pack(self):
        ret = struct.pack("bbH", self.type, self.code, self.checksum)
        ret += self.extra
        ret += self.data

        self.checksum = self._checksum(ret)

        ret = struct.pack("bbH", self.type, self.code, self.checksum)
        ret += self.extra
        ret += self.data

        return ret

    def decode(self):
        # Unpack the first 4 bytes into the appropriate locations
        (self.type, self.code, self.checksum) = struct.unpack("bbH", self.data[:4])


class ECHO_REQUEST(ICMP):
    def __init__(self,  **kwargs):
        ICMP.__init__(self)

        self.type    = 8 # ICMP_ECHO_REQUEST
        self.code    = 0
        self.id      = kwargs.get("id",      0)
        self.seq_num = kwargs.get("seq_num", 0)
        self.data    = kwargs.get("data",    0)

    def pack(self):
        self.extra = struct.pack("HH", self.id, self.seq_num)
        return ICMP.pack(self)


class ECHO_RESPONSE(ICMP):
    def __init__(self, **kwargs):
        ICMP.__init__(self)
        self.type    = 0
        self.code    = 0
        self.data    = kwargs.get("data",    0)

        self.decode()

    def decode(self):
        ICMP.decode(self)
        self.extra, self.seq_num = struct.unpack("HH", self.data[4:8])

        if 0 != self.type:
            print dir(type(self))
            raise Exception("Attempted to unpack the wrong data into a ECHO_RESPONSE")



def my_ping(host, count, timeout=1.0):

    # Create the raw socket
    icmp = getprotobyname("icmp")
    try:
        sock = socket(AF_INET, SOCK_RAW, icmp)
    except error, (errno, msg):
        if 1 == errno:
            print "Cannot create socket.  Please ensure you are running as root"
            sys.exit(-1)
        else:
            raise

    # Create the ICMP header
    data = string.lowercase

    addr = gethostbyname(host)
    print "Sending ping to %s(%s): %i data bytes" % (host, addr, len(data))


    # Send N pings
    for i in xrange(0, count):

        hdr = ECHO_REQUEST(data=data, seq_num=(i+1))
        buff = hdr.pack()

        # Send it
        global send_count
        send_count += 1
        sock.sendto(buff, (host, DUMMY_PORT))

        # Wait for a response
        startedSelect = time.time()
        whatReady = select.select([sock], [], [], timeout)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            print "Timed out"
            return

        # Note when we recieved it
        timeReceived = time.time()

        recv_packet, addr = sock.recvfrom(1024)

        # recv_packet is a full IP packet.  So we are going to 
        # skip the IP header, so let's pull out the length

        hdr_len = 0x0F & ord(recv_packet[0])
        hdr_len *= 4 # Stored in the packet is the number of 32-bit words

        icmp_data = recv_packet[hdr_len:]

        # Parse the response
        try:
            resp = ECHO_RESPONSE(data=icmp_data)
        except:
            print("Got an unhandled response back")
            continue

        global recv_count
        recv_count += 1

        rtt = (timeReceived - startedSelect) * 1000

        print("%i bytes from %s: icmp_seq=%i time=%02f ms" % 
            (
                len(icmp_data), 
                addr[0], 
                resp.seq_num,
                rtt
            )
        )

        # Save min/max
        global rtt_max
        global rtt_min
        global rtt_list
        if rtt > rtt_max:
            rtt_max =  rtt
        if rtt < rtt_min:
            rtt_min = rtt

        rtt_list.append(rtt)


        # Sleep for a second if called in a loop
        if count > 1:
            time.sleep(1.0)

    # Close the socket
    sock.close()


def print_stats():

    global send_count
    global recv_count
    global remote_host
    global rtt_max
    global rtt_min

    rtt_sum = 0
    for rtt in rtt_list:
        rtt_sum += rtt

    rtt_avg = rtt_sum / len(rtt_list)

    print """\
--- %s ping statistics ---
%i packets transmitted, %i packets received, %f%% packet loss
round-trip min/avg/max = %f/%f/%f
""" % (
    remote_host, 
    send_count, 
    recv_count, 
    ((1-recv_count/send_count)*100),
    rtt_min,
    rtt_max,
    rtt_avg)


def main():


    parser = OptionParser()
    parser.add_option("-n", "", dest="num_packets",
                      default=1, action="store",
                      type="int",
                      help="Number of pings to send")

    (options, args) = parser.parse_args()

    # Error check the arguments
    if len(args) != 1:
        parser.print_help()
        sys.exit(-1)

    # Ping the remote host
    global remote_host
    remote_host = args[0]
    delay = my_ping(remote_host, options.num_packets)
        
    print_stats()

"""
This is used so that main() will only be called if it is called
directly from the command line.

If you were to import <filename>, you could then call any function
in this file, and avoid calling main()

main() could be a test harness for a set of library code.  So you 
can test your library standalone, but still use it from other code

If you don't have this, all code at the "top" level will get called as soon
as you import this file.


aka: good habit
"""
if __name__ == "__main__":
    main()
