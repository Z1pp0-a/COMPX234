import socket
import threading
import os
import base64
import random

class  UDPFileServer:
    def __init__(self,port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET_,socket.SOCK_STREAM)
        self.server_socket.bind('0.0.0.0',self.port)
        self.server_socket.listen(5)
        print(f"SErver started on port {self.port}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"New connection from{addr}")
            client_thread = threading.Thread(target=self.handle_client,args=(client_socket,))
            client_thread.start()
    
    def handle_client(self,client_socket):
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if request.startwith("DOWNLOAD"):
                filename = request.split("  ")[1]
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    udp_port = random.randint(50000,51000)
                    response = f"OK{filename}SIZE{file_size}PORT{udp_port}"
                    client_socket.send(response.encode('utf-8'))
                    self.transfer_file(filename,file_size,udp_port,client_socket.getpeername())
                else:
                    response = f"ERR{filename}NOT_FOUND"
                    client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client:{e}")
        finally:
            client_socket.close()
            