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
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.host, self.port))
                print(f"Connected to server at {self.host}:{self.port}")
            except ConnectionRefusedError:
                print(f"Could not connect to server at {self.host}:{self.port}")
        
        for line in requests:
            line = line.strip()
            if line.startswith("PUT"):
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    _, key, value = parts
                    msg = f"{len(key)+len(value)+4:03d} P {key} {value}"
                    sock.sendall(msg.encode())
                    response = sock.recv(1024).decode()
                    print(f"{line}: {response}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <request_file>")
        sys.exit(1)
    Client(sys.argv[1], int(sys.argv[2]), sys.argv[3])

    client = Client(host, port, request_file)
    client.run()