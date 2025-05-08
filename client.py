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
        except IOError:
            print(f"Error: Could not open file {self.request_file}")
            return
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.host, self.port))
                print(f"Connected to server at {self.host}:{self.port}")
                
                for line in requests:
                    line = line.strip()
                    if not line:
                        continue
                        
                    operation = line.split(' ', 1)[0]
                    
                    if operation == "PUT":
                        parts = line.split(' ', 2)
                        if len(parts) == 3:
                            _, key, value = parts
                            msg = f"{len(key)+len(value)+4:03d} P {key} {value}"
                            sock.sendall(msg.encode())
                            response = sock.recv(1024).decode()
                            print(f"{line}: {response}")
                        else:
                            print(f"Invalid PUT request: {line}")
                            
                    elif operation == "GET":
                        key = line.split(' ', 1)[1]
                        msg = f"{len(key)+4:03d} G {key}"
                        sock.sendall(msg.encode())
                        response = sock.recv(1024).decode()
                        print(f"{line}: {response}")
                        
                    elif operation == "READ":
                        key = line.split(' ', 1)[1]
                        msg = f"{len(key)+4:03d} R {key}"
                        sock.sendall(msg.encode())
                        response = sock.recv(1024).decode()
                        print(f"{line}: {response}")
                        
                    else:
                        print(f"Unknown operation: {operation}")
                        
            except ConnectionRefusedError:
                print(f"Could not connect to server at {self.host}:{self.port}")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <request_file>")
        sys.exit(1)
    
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be a number")
        sys.exit(1)
    
    request_file = sys.argv[3]
    client = Client(host, port, request_file)
    client.run()