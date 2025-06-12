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