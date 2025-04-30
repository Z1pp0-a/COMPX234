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
                    
                    # Parse the request
                    try:
                        parts = line.split(' ', 2)
                        if len(parts) < 2:
                            print(f"Invalid request: {line}")
                            continue
                        
                        operation = parts[0]
                        key = parts[1]
                        
                        if operation == "PUT":
                            if len(parts) != 3:
                                print(f"Invalid PUT request: {line}")
                                continue
                            value = parts[2]
                            if len(key) + len(value) > 970:
                                print(f"Request too long, ignoring: {line}")
                                continue
                            request_msg = f"{len(operation)+len(key)+len(value)+4:03d} P {key} {value}"
                        elif operation == "GET":
                            if len(key) > 999:
                                print(f"Key too long, ignoring: {line}")
                                continue
                            request_msg = f"{len(key)+4:03d} G {key}"
                        elif operation == "READ":
                            if len(key) > 999:
                                print(f"Key too long, ignoring: {line}")
                                continue
                            request_msg = f"{len(key)+4:03d} R {key}"
                        else:
                            print(f"Unknown operation: {operation}")
                            continue
                        
                        # Send request and get response
                        sock.sendall(request_msg.encode('utf-8'))
                        response = sock.recv(1024).decode('utf-8')
                        
                        # Parse and display response
                        if len(response) >= 3:
                            try:
                                msg_size = int(response[:3])
                                status = response[4:7]
                                message = response[7:].strip()
                                
                                if status == "OK ":
                                    print(f"{line}: OK {message}")
                                elif status == "ERR":
                                    print(f"{line}: ERR {message}")
                                else:
                                    print(f"Unknown response: {response}")
                            except ValueError:
                                print(f"Invalid response format: {response}")
                        else:
                            print(f"Invalid response: {response}")
                    except Exception as e:
                        print(f"Error processing request '{line}': {e}")
            except ConnectionRefusedError:
                print(f"Could not connect to server at {self.host}:{self.port}")
            except Exception as e:
                print(f"Error: {e}")

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