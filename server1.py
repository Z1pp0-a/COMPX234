import socket
import threading

class Server:
    def __init__(self,port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True

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

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                cmd, *parts = data.split(' ', 2)
                if cmd == 'P' and len(parts) == 2:
                    response = self.handle_put(*parts)
                elif cmd == 'G':
                    response = self.handle_get(parts[0])
                elif cmd == 'R':
                    response = self.handle_read(parts[0])
                else:
                    response = "000 ERR invalid command"
                
                client_socket.send(response.encode())
        finally:
            client_socket.close()

    def handle_put(self, key, value):
        with self.lock:
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