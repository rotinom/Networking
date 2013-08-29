
from optparse import OptionParser
from datetime import datetime
import os, sys, socket, time, SocketServer

# Handle a http get request
def handle_get(command):
    get, path, version = command.split()

    # Get the absolute path
    path = os.getcwd() + path

    # Does the path exist?
    if not os.path.exists(path):
        not_found = http_header(404)
        return str(not_found)

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
        not_found = http_header(404)
        return str(not_found)

    # Open and read the file
    data = open(path, "rb").readlines()
    reply = "".join(data)

    modified_time = datetime.fromtimestamp(os.path.getmtime(path))

    header = http_header(200, len(reply), modified_time)
    reply = str(header) + reply
    return reply




class http_header:
    """
    This class represents the header for a http response
    """

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


# Handler for the HTTP connections
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

# Start a multi-threaded server using the SocketServer architecture
def start_threaded():
    try:
        # Start our TCP server
        server = SocketServer.TCPServer(("localhost", 80), HttpHandler)
        server.serve_forever()
    except:
        print "Could not bind to socket"


# Start a simple, single-threaded server
def start_simple():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to localhost, and set the timeout
    try:
        serverSocket.bind(("localhost", 80))
    except:
        print "Unable to bind socket"
        sys.exit(-1)

        #Establish the connection
        print 'Ready to serve...'

    while True:
        serverSocket.listen(5)

        # accept the connection
        connectionSocket, addr = serverSocket.accept()


        data = connectionSocket.recv(1024)
        if len(data) == 0:
            return

        command = data.split("\n")[0]
        if command.startswith("GET"):
            results = handle_get(command)
            connectionSocket.send(results)

        connectionSocket.close()


# Main entry point
if __name__ == "__main__":

    print os.getcwd()

    parser = OptionParser()
    parser.add_option("-t", "--threaded", dest="threaded",
                      default=False, action="store_true",
                      help="start multi-threaded server")

    parser.add_option("-s", "--simple", dest="simple",
                      default=False, action="store_true",
                      help="start single-threaded server")

    (options, args) = parser.parse_args()

    if options.threaded:
        start_threaded()
    elif options.simple:
        start_simple()
