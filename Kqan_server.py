import os 
import socket
import keyboard
import threading

DIRECTORY_OF_DATA = ".\Server_data"
DATA_FILE_NAME = "list_of_names.txt"
ORIGIN_DIRECTORY = os.getcwd()
HOST = "127.0.0.1"
PORT = 9999
BUFFSIZE = 1024 * 1024
FORMAT = "utf-8"

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, DIRECTORY_OF_DATA)
os.chdir(path)


def convertFileSize(file_size):
    unit = ""
    if file_size < 1024:
        unit = f"{int(file_size)}{unit} B"
    elif file_size < 1024**2:
        unit = f"{int(file_size / 1024)} KB"
    elif file_size < 1024**3: 
        unit = f"{int(file_size / 1024**2)} MB"
    else:
        unit = f"{int(file_size / 1024**3)} GB"
    return unit

def listFileInPath():
    list_file = []
    for name in os.listdir():
        file_size =  os.path.getsize(name)
        object = {
            name : convertFileSize(file_size)
        }
        list_file.append(object)
    return list_file

def printListFile(source_file_name, list_file):
    with open(source_file_name, "w") as f:
        for file in list_file:
            for key, value in file.items():
                f.write(f"{key}     {value}\n")

def handleGreeting(socket):
    socket.sendall("GREETING-OK".encode("utf_8"))
    list_file = listFileInPath()
    os.chdir(ORIGIN_DIRECTORY)
    printListFile(DATA_FILE_NAME, list_file)

    file_size = os.path.getsize(DATA_FILE_NAME)
    with open(DATA_FILE_NAME, "rb") as file:
        file_data = file.read()
    
    socket.sendall(f"{DATA_FILE_NAME}:{file_size}".encode("utf_8"))
    socket.sendall(file_data)
    os.chdir(path)

    socket.close()

def handleDownloadFile(socket_download_file):
    socket_download_file.sendall("FILE-OK".encode("utf_8"))
    file_name = socket_download_file.recv(BUFFSIZE).decode("utf_8")
    file_size = os.path.getsize(file_name)
    print(f"Sending {file_name} with size {file_size}")
    socket_download_file.sendall(str(file_size).encode("utf_8"))

def handleDownLoadChunk(socket_download_chunk):
    socket_download_chunk.sendall("CHUNK-OK".encode("utf_8"))

    file_name, start, end = socket_download_chunk.recv(BUFFSIZE).decode("utf_8").split(":")
 
    start = int(start)
    end = int(end)
    chunk_size = end - start + 1
    sent_data = 0

    with open(file_name, "rb") as file:
        while sent_data < chunk_size:
            file.seek(start + sent_data)
            data = file.read(min(chunk_size - sent_data, BUFFSIZE))
            socket_download_chunk.sendall(data)
            sent_data += len(data)

    socket_download_chunk.close()

def handle_client(client_socket, addr):
    print(f"Connected to {addr}")
    try:
        request = client_socket.recv(BUFFSIZE).decode("utf_8")

        if request == "GREETING":
            handleGreeting(client_socket)
        elif request == "FILE":
            handleDownloadFile(client_socket)
        elif request == "CHUNK":
            handleDownLoadChunk(client_socket)
    except KeyboardInterrupt:
        client_socket.close()


def runServer(HOST, PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Server is runing... ")
    try:
        while True:
            server_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(server_socket, addr))
            thread.start()
    except KeyboardInterrupt:
        server.close()

def main():
    runServer(HOST, PORT)

if __name__ == "__main__":
    main()