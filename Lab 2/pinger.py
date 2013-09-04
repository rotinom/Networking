#!/usr/bin/python

# We will need the following module to generate randomized lost packets import random
from socket import *
from datetime import *
import os, sys, string, random

port = 12000
num_pings = 10


def server():
    # Create a UDP socket
    # Notice the use of SOCK_DGRAM for UDP packets
    sock = socket(AF_INET, SOCK_DGRAM) # Assign IP address and port number to socket
    sock.bind(('', port))
    sock.settimeout(0.250) # Timeout every so often so we can kill w/ ctrl-c

    while True:
        # Receive the client packet along with the address it is coming from
        try:
            message, address = sock.recvfrom(1024)

            # If rand is less is than 4, we consider the packet lost and do not respond
            if random.randint(0, 10) < 4:
                continue

            # Otherwise, the server responds
            sock.sendto(message.upper(), address)

        # Ignore timeouts
        except timeout:
            continue

def timedelta_to_ms(delta):

    days    = float(delta.days)
    seconds = float(delta.seconds)
    us      = float(delta.microseconds)

    # Convert days to milliseconds
    milliseconds = days * 24.0 * 60.0 * 60.0 * 1000.0

    # Convert microseconds to milliseconds
    milliseconds += us / 1000.0

    return milliseconds


def ping(host):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(1.0)

    results = [None] * num_pings

    for i in xrange(0, num_pings):
        results[i] = None

        # Send the packet
        sent_time = datetime.now()
        msg = "Ping %i %s" % (i+1, sent_time)
        sock.sendto(msg, (host, port))

        # Wait for a response
        try:
            data, remote_addr = sock.recvfrom(1024)
            recv_time = datetime.now()
            elapsed_time = recv_time-sent_time

            results[i] = elapsed_time

            print "%s time %sms" % (data, timedelta_to_ms(elapsed_time))
        except timeout:
            print "Request timed out"
            

    # Post-process our times
    min = timedelta.max
    max = timedelta.min
    total_time = timedelta()
    lost_count = 0

    for res in results:
        if None == res:
            lost_count += 1
            continue

        if res > max:
            max = res

        if res < min:
            min = res

        total_time += res

    # Clean up min/max
    if min == timedelta.max:
        min = timedelta()

    if max == timedelta.min:
        max = timedelta()

    # Figure out our stats
    recv_count = num_pings - lost_count
    lost_percent = (float(lost_count)/float(num_pings)) * 100.0
    avg_time = timedelta_to_ms(total_time)/recv_count

    print "\tPackets: Sent = %i, Received = %i, Lost = %i (%i%% loss)," % \
        (num_pings, recv_count, lost_count, lost_percent)
    print "\tMinimum = %ims, Maximum = %ims, Average = %ims" % \
        (timedelta_to_ms(min), timedelta_to_ms(max), avg_time)




def main():
    if len(sys.argv) == 1:
        server()
    else:
        ping(sys.argv[1])


if __name__ == "__main__":
    main();