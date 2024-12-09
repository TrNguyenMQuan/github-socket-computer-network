import os
import socket
import threading
HOST = "localhost"
PORT = 9999
ADDR = (HOST, PORT)
BUFFSIZE = 1024*1024
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handleGreeting(socket_greeting):
    socket_greeting.sendall("GREETING-OK".encode("utf_8"))
    socket_greeting.close()

def handleDownloadFile(socket_download_file):
    socket_download_file.sendall("FILE-OK".encode("utf_8"))
    file_name = socket_download_file.recv(BUFFSIZE).decode("utf_8")
    file_size = os.path.getsize(file_name)
    socket_download_file.sendall(str(file_size).encode("utf_8"))
    socket_download_file.close()

def handleDownLoadChunk(socket_download_chunk):
    socket_download_chunk.sendall("CHUNK-OK".encode("utf_8"))
    print("downloading chunks")
    file_name, start, end = socket_download_chunk.recv(BUFFSIZE).decode("utf_8").split(":")
    print(f"{(file_name, start, end)}")
    start = int(start)
    end = int(end)
    chunk_size = end - start + 1
    sent_data = 0

    with open(file_name, "rb") as file:
        while sent_data < chunk_size:
            file.seek(start + sent_data)
            data = file.read(min(chunk_size - BUFFSIZE, BUFFSIZE))
            socket_download_chunk.sendall(data)
            sent_data += len(data)



    socket_download_chunk.close()

def handleClient(client):
    request = client.recv(BUFFSIZE).decode("utf_8")
    print(f"{request}          ")
    if request == "GREETING":
        handleGreeting(client)
    elif request == "FILE":
        handleDownloadFile(client)
    elif request == "CHUNK":
        handleDownLoadChunk(client)

    client.close()

def runServer():
    server.bind(ADDR)
    server.listen()

    while True:
        print("Server is running....")
        conn, addr = server.accept()    
        print(f"connecting to {addr}")
        t = threading.Thread(target=handleClient, args=(conn,)).start()

    server.close()
    
def main():
    runServer()


if __name__ == "__main__":
    main()