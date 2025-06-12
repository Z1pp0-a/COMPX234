import socket
import base64
import time
import sys

class UDPFileClient:
    def __init__(self, host, port, request_file):
        self.host = host
        self.port = port
        self.request_file = request_file
 