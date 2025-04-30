import socket
import threading
import time
from collections import defaultdict

class Server:
    def __init__(self, port):
        self.port = port
        self.tuple_space = {}
        self.lock = threading.Lock()
        self.stats = {
            'total_clients': 0,
            'total_operations': 0,
            'total_reads': 0,
            'total_gets': 0,
            'total_puts': 0,
            'total_errors': 0,
        }
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"Server started on port {self.port}")
        
        # Start stats reporting thread
        stats_thread = threading.Thread(target=self.report_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                self.stats['total_clients'] += 1
                print(f"New connection from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            self.server_socket.close()
    
    def report_stats(self):
        while self.running:
            time.sleep(10)
            with self.lock:
                num_tuples = len(self.tuple_space)
                if num_tuples > 0:
                    avg_key_size = sum(len(k) for k in self.tuple_space) / num_tuples
                    avg_value_size = sum(len(v) for v in self.tuple_space.values()) / num_tuples
                    avg_tuple_size = avg_key_size + avg_value_size
                else:
                    avg_key_size = avg_value_size = avg_tuple_size = 0
                
                print("\n=== Server Stats ===")
                print(f"Tuples: {num_tuples}")
                print(f"Avg tuple size: {avg_tuple_size:.2f} chars")
                print(f"Avg key size: {avg_key_size:.2f} chars")
                print(f"Avg value size: {avg_value_size:.2f} chars")
                print(f"Total clients: {self.stats['total_clients']}")
                print(f"Total operations: {self.stats['total_operations']}")
                print(f"READs: {self.stats['total_reads']}, GETs: {self.stats['total_gets']}, PUTs: {self.stats['total_puts']}")
                print(f"Errors: {self.stats['total_errors']}")
                print("===================\n")
    
    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                # Parse the request
                try:
                    msg_size = int(data[:3])
                    cmd = data[4]
                    remaining = data[5:].strip()
                    
                    if cmd == 'R':  # READ
                        key = remaining
                        response = self.handle_read(key)
                    elif cmd == 'G':  # GET
                        key = remaining
                        response = self.handle_get(key)
                    elif cmd == 'P':  # PUT
                        parts = remaining.split(' ', 1)
                        if len(parts) == 2:
                            key, value = parts
                            response = self.handle_put(key, value)
                        else:
                            response = "000 ERR invalid PUT format"
                    else:
                        response = "000 ERR invalid command"
                    
                    client_socket.send(response.encode('utf-8'))
                except Exception as e:
                    response = "000 ERR invalid request format"
                    client_socket.send(response.encode('utf-8'))
        except ConnectionResetError:
            pass
        finally:
            client_socket.close()
    
    def handle_read(self, key):
        with self.lock:
            self.stats['total_operations'] += 1
            self.stats['total_reads'] += 1
            
            if key in self.tuple_space:
                value = self.tuple_space[key]
                response = f"{len(key)+len(value)+18:03d} OK ({key}, {value}) read"
                return response
            else:
                self.stats['total_errors'] += 1
                return f"{len(key)+24:03d} ERR {key} does not exist"
    
    def handle_get(self, key):
        with self.lock:
            self.stats['total_operations'] += 1
            self.stats['total_gets'] += 1
            
            if key in self.tuple_space:
                value = self.tuple_space.pop(key)
                response = f"{len(key)+len(value)+21:03d} OK ({key}, {value}) removed"
                return response
            else:
                self.stats['total_errors'] += 1
                return f"{len(key)+24:03d} ERR {key} does not exist"
    
    def handle_put(self, key, value):
        with self.lock:
            self.stats['total_operations'] += 1
            self.stats['total_puts'] += 1
            
            if key in self.tuple_space:
                self.stats['total_errors'] += 1
                return f"{len(key)+24:03d} ERR {key} already exists"
            else:
                self.tuple_space[key] = value
                return f"{len(key)+len(value)+18:03d} OK ({key}, {value}) added"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
        if not (50000 <= port <= 59999):
            raise ValueError("Port must be between 50000 and 59999")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    server = Server(port)
    server.start()