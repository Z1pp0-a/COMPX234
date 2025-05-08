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
                
                if data.startswith('P '):  # 简单PUT协议
                    _, key, value = data.split(' ', 2)
                    response = self.handle_put(key, value)
                    client_socket.send(response.encode())
        finally:
            client_socket.close()

    def handle_put(self, key, value):
        with self.lock:
            if key in self.tuple_space:
                return "024 ERR key already exists"
            self.tuple_space[key] = value
            return f"{len(key)+len(value)+18:03d} OK ({key}, {value}) added"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    Server(int(sys.argv[1])).start()