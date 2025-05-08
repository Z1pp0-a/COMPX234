import socket
import threading

class Server:
    def __init__(self,port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        self.stats = {
            'total_clients': 0,
            'total_operations': 0,
            'total_reads': 0,
            'total_gets': 0,
            'total_puts': 0,
            'total_errors': 0
        }

    def start(self):
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"Server started on port {self.port}")
        
        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
        finally:
            self.server_socket.close()
        threading.Thread(target=self.report_stats, daemon=True).start()

    def report_stats(self):
        while self.running:
            time.sleep(10)
            print(f"\nServer Stats: {self.stats}\n")

def handle_client(self, client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            try:
                msg_size = int(data[:3])
                cmd = data[4]
                remaining = data[5:].strip()
                
                if cmd == 'P':
                    parts = remaining.split(' ', 1)
                    if len(parts) == 2:
                        response = self.handle_put(*parts)
                    else:
                        response = "000 ERR invalid PUT format"
                # ...类似处理GET/READ...
            except Exception:
                response = "000 ERR invalid request"
            
            client_socket.send(response.encode())
    finally:
        client_socket.close()

    def handle_put(self, key, value):
        with self.lock:
            self.stats['total_operations'] += 1
            self.stats['total_puts'] += 1
            if key in self.tuple_space:
                return "024 ERR key already exists"
            self.tuple_space[key] = value
            return f"{len(key)+len(value)+18:03d} OK ({key}, {value}) added"
        
    def handle_get(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            value = self.tuple_space.pop(key)
            return f"{len(key)+len(value)+21:03d} OK ({key}, {value}) removed"

    def handle_read(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            value = self.tuple_space[key]
            return f"{len(key)+len(value)+18:03d} OK ({key}, {value}) read"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    Server(int(sys.argv[1])).start()