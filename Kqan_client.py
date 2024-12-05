
import os
import time
import socket
import threading

HOST = "localhost"
PORT = 9999
DATA_FILE_NAME = "list of file names.txt"
DOWNLOAD_FILE_NAME = "input.txt"
CHUNKS_FILE = 1024

pending_file = []

def scanInputAfter5Secs(source_file_name):
    position = 0
    while True:
        with open(source_file_name, "r") as file:
            file.seek(position)
            while True:
                data = file.readline()
                if not data:
                    break
                if data != "\n":
                    pending_file.append(data.strip("\n"))
            position = file.tell()
            print(len(pending_file))
        time.sleep(5)

def downloadFile(client: socket.socket):
    while True:
        print(len(pending_file))
        while pending_file:
            file_name = pending_file[0]
            pending_file.pop(0)
            print(f"downloading {file_name}........")
        time.sleep(5)

    

def runClient():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(f"connect successfully!")
    print(client.recv(1024).decode("utf_8"))
    

    threading.Thread(target=scanInputAfter5Secs, daemon=False, args=(DOWNLOAD_FILE_NAME,)).start()
    threading.Thread(target=downloadFile, daemon=False, args=(client, )).start()
    # scanInputAfter5Secs(DOWNLOAD_FILE_NAME)
    

def main():
    runClient()

if __name__ == "__main__":
    main()