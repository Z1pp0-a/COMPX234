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

        def receive_file(self, filename, file_size, udp_port, server_addr):
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.settimeout(1)
            start = 0
            end = min(1024, file_size)
            with open(filename, 'wb') as file:
                while start < file_size:
                    request = f"FILE {filename} GET START {start} END {end}"
                    retries = 0
                    while True:
                        try:
                            udp_socket.sendto(request.encode('utf-8'), (server_addr[0], udp_port))
                            response, _ = udp_socket.recvfrom(4096)
                            response = response.decode('utf-8')
                            if response.startswith("FILE " + filename + " OK "):
                                parts = response.split(" ")
                                start = int(parts[3])
                                end = int(parts[5])
                                data = base64.b64decode(parts[7])
                                file.write(data)
                                break
                        except socket.timeout:
                            retries += 1
                            if retries > 5:
                                print(f"Failed to download {filename} after multiple retries")
                                return
                            time.sleep(0.5 * retries)
                    start = end
                    end = min(end + 1024, file_size)

            close_request = f"FILE {filename} CLOSE"
            retries = 0
            while True:
                try:
                    udp_socket.sendto(close_request.encode('utf-8'), (server_addr[0], udp_port))
                    response, _ = udp_socket.recvfrom(1024)
                    response = response.decode('utf-8')
                    if response.startswith("FILE " + filename + " CLOSE_OK"):
                        break
                except socket.timeout:
                    retries += 1
                    if retries > 5:
                        print(f"Failed to close connection for {filename} after multiple retries")
                        break
                    time.sleep(0.5 * retries)

            udp_socket.close()
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <host> <port> <request_file>")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be a number")
        sys.exit(1)

    request_file = sys.argv[3]

    client = UDPFileClient(host, port, request_file)
    client.run()