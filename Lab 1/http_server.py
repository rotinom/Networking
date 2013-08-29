
# import os, sys
# from socket import *
# serverSocket = socket(AF_INET, SOCK_STREAM)

# while True:
#     #Establish the connection
#     print 'Ready to serve...'
#     connectionSocket, addr =
#     try:
#         #Fill in start
#         #Fill in end
#         message = #Fill in start #Fill in end filename = message.split()[1]
#         f = open(filename[1:])
#         outputdata = #Fill in start #Fill in end #Send one HTTP header line into socket
#         #Fill in start
#         #Fill in end
#         #Send the content of the requested file to the client
#         for i in range(0, len(outputdata)):
#             connectionSocket.send(outputdata[i])
#         connectionSocket.close()
#     except IOError:
#         pass
#         #Send response message for file not found
#     #Fill in start #Fill in end
#     #Close client socket #Fill in start #Fill in end
#     serverSocket.close()


from optparse import OptionParser
import SocketServer
from datetime import datetime
import os, sys, socket


def handle_get(command):
    get, path, version = command.split()

    # Get the absolute path
    path = os.getcwd() + path

    # Does the path exist?
    if not os.path.exists(path):
        not_found = http_response(404)
        # self.request.sendall(str(not_found))
        return str(not_found)
        return

    # Did we get a directory, try to find 
    # index.htm, or index.html
    if os.path.isdir(path):
        for index in ["index.htm", "index.html"]:
            temp_index = os.path.join(path, index)
            if os.path.exists(temp_index):
                path = temp_index
                break

    # We couldn't find the given file
    if not os.path.isfile(path):
        not_found = http_response(404)
        # self.request.sendall(str(not_found))
        return str(not_found)
        return

    # Open and read the file
    data = open(path, "rb").readlines()
    reply = "".join(data)

    header = http_response(200, len(reply))
    reply = str(header) + reply
    # self.request.sendall(reply+"\n\n")
    return reply




class http_response:
    def __init__(self, code, length=0, modified=datetime.now()):
        self._code = code
        self._length = length
        self._modified = modified

        self._code_map = {}
        self._code_map[404] = "404 Not Found"
        self._code_map[200] = "200 OK"

    def __str__(self):
        ret = []
        ret.append("HTTP/1.1 %s" % self._code_map[self._code])
        ret.append("Connection: close")
        ret.append("Date: %s" % self._format_date(datetime.now()))
        ret.append("Server: Dave Weber's Simple HTTP Server")
        ret.append("Last-Modified: %s" % self._format_date(self._modified))
        ret.append("Content-Length: %i" % self._length)
        ret.append("Content-Type: text/html")
        return "\n".join(ret) + "\n\n"

    def _format_date(self, date):
        return date.strftime("%a, %d %b %Y %H:%M:%S %Z")

class HttpHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        sock = self.request
        self._data = sock.recv(1024).strip()

        if len(self._data) == 0:
            return

        command = self._data.split("\n")[0]
        if command.startswith("GET"):
            results = handle_get(command)
            self.request.sendall(results)


def start_threaded():

    try:
        # Start our TCP server
        server = SocketServer.TCPServer(("localhost", 80), HttpHandler)
        server.serve_forever()
    except:
        print "Could not bind to socket"

def start_simple():

    serverSocket = socket.socket(AF_INET, SOCK_STREAM)

    # Bind to localhost, and set the timeout
    serverSocket.bind("localhost")
    serverSocket.settimeout(0.1)

    while True:
        #Establish the connection
        print 'Ready to serve...'
        # try:
        serverSocket.listen()
        # except:
        #     continue

        connectionSocket, addr = serverSocket.accept()

        if len(self._data) == 0:
            return

        command = self._data.split("\n")[0]
        if command.startswith("GET"):
            results = handle_get(command)
            connectionSocket.send(results)

        connectionSocket.close()



# Main entry point
if __name__ == "__main__":

    print os.getcwd()

    parser = OptionParser()
    parser.add_option("-t", "--threaded", dest="threaded",
                      default=True, action="store_true",
                      help="start multi-threaded server")

    parser.add_option("-s", "--simple", dest="simple",
                      default=True, action="store_true",
                      help="start single-threaded server")

    (options, args) = parser.parse_args()

    if options.threaded:
        start_threaded()
    elif options.simple:
        start_simple()
