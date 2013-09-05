#!/usr/bin/python

from socket import *
from optparse import OptionParser
import os, sys, struct, time, string, select, binascii



ICMP_ECHO_REQUEST = 8
def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = ord(str[count+1]) * 256 + ord(str[count])
        csum = csum + thisVal
        csum = csum & 0xffffffffL
        count = count + 2
    if countTo < len(str):
        csum = csum + ord(str[len(str) - 1])
        csum = csum & 0xffffffffL
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



DUMMY_PORT = 1S

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
    32-64   Rest of header
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






def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start
        #Fetch the ICMP header from the IP packet
        #Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        #Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    #Both LISTS and TUPLES consist of a number of objects
    #which can be referenced by their position number within the object

def ping(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
#SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    #Fill in start
    #Create Socket here
    #Fill in end

    myID = os.getpid() & 0xFFFF  #Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def my_ping(host, timeout=1.0):

    # Create the raw socket
    icmp = getprotobyname("icmp")
    try:
        sock = socket(AF_INET, SOCK_RAW, icmp)
    except error, (errno, msg):
        if 1 == errno:
            print "Cannot create socket.  Please run this as root"
            sys.exit(-1)
        else:
            raise
    sock.settimeout(0.1)


    # Create the ICMP header
    hdr = ECHO_REQUEST(data=string.lowercase)
    buff = hdr.pack()
    print_buffer(buff)


    addr = gethostbyname(host)
    sock.sendto(buff, (host, DUMMY_PORT))

# def OLD_PING(host, timeout=1):
#     #timeout=1 means: If one second goes by without a reply from the server,
#     #the client assumes that either the client's ping or the server's pong is lost

#     dest = socket.gethostbyname(host)
#     print "Pinging " + dest + " using Python:"
#     print ""

#     #Send ping requests to a server separated by approximately one second
#     while True :
#         delay = doOnePing(dest, timeout)
#         print delay
#         time.sleep(1)

#     return delay


def main():

    my_ping("localhost")

    sys.exit(-1)
    if len(sys.argv) != 2:
        print "Usage: %s <hostname>" % sys.argv[0]
        sys.exit(-1)

    parser.add_option("-n", "", dest="num_packets",
                      default=4, action="store",
                      help="Number of pings to send")

    (options, args) = parser.parse_args()

    remote_host = sys.arg[1]

    for i in xrange(0, options.num_packets):
        delay = ping(remote_host)
        time.sleep(1.0)


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
