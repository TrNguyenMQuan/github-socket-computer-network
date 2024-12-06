import socket
import os
import threading


IP = "127.0.0.1"
PORT = 65432
SEVER_ADDRESS = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
    
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SEVER_ADDRESS)
server.listen()
print(f"Sever is waiting connection from client on {IP}:{PORT}")

conn, address = server.accept()

file_requested = conn.recv(SIZE).decode(FORMAT)
file_size = os.path.getsize(file_requested)
conn.send(str(file_size).encode(FORMAT))

print(f"Client requested file: {file_requested} with {file_size}")

with open(file_requested, "rb") as f:
    while True:
        data_sended = f.read(SIZE)

        if not data_sended:
            break

        conn.sendall(data_sended)
    
print(f"File: {file_requested} send successfully !")

conn.close()
