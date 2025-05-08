import socket
import sys

class Client:
    def __init__(self, host, port, request_file):
        self.host = host
        self.port = port
        self.request_file = request_file

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <request_file>")
        sys.exit(1)
    Client(sys.argv[1], int(sys.argv[2]), sys.argv[3])