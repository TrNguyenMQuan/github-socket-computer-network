import socket
import os
from tqdm import tqdm
import threading

IP = "127.0.0.1"
PORT = 65432
SEVER_ADDRESS = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SEVER_ADDRESS)

file_requested = input("Enter the filename you want to download: ")
client.send(file_requested.encode(FORMAT))
file_size = int(client.recv(SIZE).decode(FORMAT))

def download_file(file_name, start_byte, end_byte):
    chunk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chunk.connect(SEVER_ADDRESS)

    chunk.send(file_name.encode(FORMAT))
    chunk.send(str(start_byte).encode(FORMAT))
    chunk.send(str(end_byte).encode(FORMAT))

bar = tqdm(range(file_size), f"Downloading {file_requested}", unit="B", unit_scale=True, unit_divisor=SIZE)
chunk_size = file_size // 4
threads = []
for i in range(4):
    start_byte = i * chunk_size
    end_byte = (i + 1) * chunk_size - 1 if i < 3 else file_size - 1
with open(f"downloaded_{file_requested}", "wb") as f:
    temp = 0
    while temp <= file_size:
        data_received = client.recv(min(SIZE, file_size))
        f.write(data_received)
        progress = (len(data_received) / file_size) * 100
        sys.stdout.write(f"\rDownloading: {progress:.2f}%")
        sys.stdout.flush()
        temp += len(data_received)

print(f"File {file_requested} dowloaded successfully !")
client.close()

