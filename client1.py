import socket
import sys

class Client:
    def __init__(self, host, port, request_file):
        self.host = host
        self.port = port
        self.request_file = request_file

    def run(self):
        try:
            with open(self.request_file, 'r') as file:
                requests = file.readlines()
                print(f"Loaded {len(requests)} requests")
        except IOError:
            print(f"Error: Could not open file {self.request_file}")
            return

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <request_file>")
        sys.exit(1)
    Client(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    
    client = Client(host, port, request_file)
    client.run()