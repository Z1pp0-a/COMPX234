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

