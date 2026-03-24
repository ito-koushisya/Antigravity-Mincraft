import socket
import struct
import time

class MCRcon:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.request_id = 0

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.host, self.port))
        self.login()

    def login(self):
        self.send(3, self.password)
        input_type, input_id, input_body = self.read()
        if input_id == -1:
            raise Exception("Authentication failed")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def command(self, cmd):
        self.send(2, cmd)
        input_type, input_id, input_body = self.read()
        return input_body

    def send(self, type, body):
        self.request_id += 1
        # Packet size = size(ID + Type + Body + Null + Null) = 4 + 4 + len + 1 + 1
        # But pack struct expects: Size (int), ID (int), Type (int), Body (str), Null (char), Null (char)
        # Size field itself is not included in size.
        # Wait, the int is 4 bytes.
        # Packet format:
        # Length: int (4 bytes, signed, little endian)
        # Request ID: int (4 bytes, signed, little endian)
        # Type: int (4 bytes, signed, little endian)
        # Payload: byte[] (null terminated)
        # 2-byte pad: \x00\x00
        
        body_bytes = body.encode('utf-8')
        length = 4 + 4 + len(body_bytes) + 2
        
        packet = struct.pack('<iii', length, self.request_id, type) + body_bytes + b'\x00\x00'
        self.socket.send(packet)

    def read(self):
        # Read length
        header = self.socket.recv(4)
        if len(header) < 4:
            return 0, 0, ""
        length = struct.unpack('<i', header)[0]
        
        # Read payload
        data = b''
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if not chunk:
                break
            data += chunk
            
        if len(data) < length:
            raise Exception("Incomplete packet")
            
        request_id, type = struct.unpack('<ii', data[:8])
        body = data[8:-2].decode('utf-8') # -2 to strip null bytes
        return type, request_id, body
