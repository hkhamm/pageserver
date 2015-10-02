"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible.

  Serves HTML and CSS files from the directory where the program is run.
"""

import socket  # Basic TCP/IP communication on the internet
import random  # To pick a port at random, giving us some chance to pick a port not in use
import _thread  # Response computation runs concurrently with main program
import os
import re


def listen(portnum):
    """
    Create and listen to a server socket.
    Args:
       portnum: Integer in range 1024-65535; temporary use ports
           should be in range 49152-65535.
    Returns:
       A server socket, unless connection fails (e.g., because
       the port is already in use).
    """
    # Internet, streaming socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to port and make accessible from anywhere that has our IP address
    serversocket.bind(('', portnum))
    serversocket.listen(1)  # A real server would have multiple listeners
    return serversocket


def serve(sock, func):
    """
    Respond to connections on sock.
    Args:
       sock:  A server socket, already listening on some port.
       func:  a function that takes a client socket and does something with it
    Returns: nothing
    Effects:
        For each connection, func is called on a client socket connected
        to the connected client, running concurrently in its own thread.
    """
    while True:
        print("Attempting to accept a connection on {}".format(sock))
        (clientsocket, address) = sock.accept()
        _thread.start_new_thread(func, (clientsocket,))


def respond(sock):
    """
    Respond (only) to GET
    """
    sent = 0
    request = sock.recv(1024)  # We accept only short requests
    request = str(request, encoding='utf-8', errors='strict')

    if request != "":
        print("\nRequest was {}\n".format(request))

    parts = request.split()

    if len(parts) > 1 and "." in parts[1]:
        ext = parts[1].split(".")

    pattern = re.compile('/[\w]*[.](?=html|css)') # /a-zA-Z0-9_*.(html|css)

    valid_request = False
    if len(parts) > 1 and parts[0] == "GET":
        valid_request = True

    if valid_request and parts[1] == "/":
        transmit("HTTP/1.0 200 OK\n\n", sock)
        msg = get_msg("./index.html")
    elif (valid_request and parts[1][1:] in os.listdir("./") and
          pattern.match(parts[1])):
        transmit("HTTP/1.0 200 OK\n\n", sock)
        msg = get_msg("." + parts[1])
    else:
        transmit("HTTP/1.0 404 Not Found\n\n", sock)
        msg = get_msg("./404.html")

    transmit(msg, sock)

    sock.close()

    return


def transmit(msg, sock):
    """It might take several sends to get the whole buffer out"""
    sent = 0
    while sent < len(msg):
        buff = bytes(msg[sent:], encoding="utf-8")
        sent += sock.send(buff)


def get_msg(filename):
    f = open(filename, 'r')
    return read_file(f)


def read_file(file):
    msg = ""
    for line in file:
        msg = msg + line
    return msg


def main():
    port = random.randint(5000, 8000)
    sock = listen(port)
    print("Listening on port {}".format(port))
    print("Socket is {}".format(sock))
    serve(sock, respond)


main()
