import socket
import base64
import time
import sys

class UDPFileClient:
    def __init__(self, host, port, request_file):
        self.host = host
        self.port = port
        self.request_file = request_file

        def run(self):
            try:
               with open(self.request_file, 'r') as file:
                    filenames = file.readlines()
            except IOError:
                print(f"Error: Could not open file {self.request_file}")
                return

            for filename in filenames:
                filename = filename.strip()
                if not filename:
                    continue
                self.download_file(filename)

        def download_file(self, filename):
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcp_socket.connect((self.host, self.port))
                request = f"DOWNLOAD {filename}"
                tcp_socket.send(request.encode('utf-8'))
                response = tcp_socket.recv(1024).decode('utf-8')
                if response.startswith("OK "):
                    parts = response.split(" ")
                    file_size = int(parts[3])
                    udp_port = int(parts[5])
                    self.receive_file(filename, file_size, udp_port, tcp_socket.getpeername())
                elif response.startswith("ERR "):
                    print(f"{filename}: {response}")
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
            finally:
                tcp_socket.close()        