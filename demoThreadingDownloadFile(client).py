import os
import threading
import socket
HOST = "localhost"
PORT = 9999
ADDR = (HOST, PORT)
BUFFERSIZE = 1024*1024*10
lock = threading.Lock()

chunks = []

def handleDownLoadChunk(file_name, start, end, index):
    socket_download_chunk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_download_chunk.connect(ADDR)
    socket_download_chunk.sendall(f"CHUNK".encode("utf_8"))
    
    request = socket_download_chunk.recv(8).decode("utf_8")
    if request != "CHUNK-OK":
        print("Fail to download chunk")
        return
    
    socket_download_chunk.sendall(f"{file_name}:{start}:{end}".encode("utf_8"))
    chunk_size = end - start + 1
    chunk_data = b""
    data_recv = 0

    while data_recv < chunk_size:
        data = socket_download_chunk.recv(min(BUFFERSIZE, chunk_size - data_recv))
        data_recv += len(data)
        chunk_data += data
        print(f"downloading {file_name} part {index} : {int((data_recv * 100) / chunk_size)} % \n")
    
    chunk = {
        "start" : start,
        "end" : end,
        "data" : chunk_data
    }
    with lock:
        chunks.append(chunk)

    socket_download_chunk.close()

def handleDownloadFile(file_name):
    socket_download_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_download_file.connect(ADDR)
    socket_download_file.sendall(f"FILE".encode("utf_8"))

    request = socket_download_file.recv(7).decode("utf_8")
    if request != "FILE-OK":
        print("fail to download file")
        return
    
    socket_download_file.sendall(file_name.encode("utf_8"))
    file_size = socket_download_file.recv(BUFFERSIZE).decode("utf_8")
    file_size = int(file_size)
    print(file_size)

    number_of_threads = 20
    part = file_size // number_of_threads
    remain_data = file_size % number_of_threads

    with open(file_name, "wb") as file:
        file.write(b'\0' * file_size)

    for i in range(number_of_threads):
        start = part * i
        end = start + part - 1
        if i == number_of_threads - 1:
            end += remain_data
        t = threading.Thread(target=handleDownLoadChunk, args=(file_name, start, end, i + 1)).start()
    
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()

    with open(file_name, "r+b") as file:
        for chunk in chunks:
            file.seek(chunk["start"])   
            file.write(chunk["data"])  
    
    socket_download_file.close()  



def handleGreeting():
    socket_greeting = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_greeting.connect(ADDR)
    socket_greeting.sendall(f"GREETING".encode("utf_8"))
    
    request = socket_greeting.recv(11).decode("utf_8")
    if request != "GREETING-OK":
        print("fail to communicate with server")
        return

    print("Finished greeting")
    socket_greeting.close()
    

def main():
    handleDownloadFile("[HaDoanTV.Com]DRGv1.39.101466.0.ON.rar")
    

if __name__ == "__main__":
    main()