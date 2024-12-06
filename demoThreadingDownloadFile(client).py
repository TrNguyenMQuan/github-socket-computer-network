import threading 
import time 
import socket
import os
HOST = 'localhost'
PORT = 9999
ADDR = (HOST, PORT)
BUFSIZE = 1024*1024
lock = threading.Lock()
chunks = []

def downloadChunks(client, file_name, start, end):
    with lock:
        # done = False
        # cnt = 1
        # while done == False:
        #     client.sendall(f"{start}:{end}".encode("utf_8"))
        #     chunk_size = end - start + 1
        #     chunk_data = client.recv(chunk_size)
        #     if len(chunk_data) == chunk_size:
        #         print("Download success\n")
        #         done = True
        #         with open(file_name, "r+b") as file:
        #             file.seek(start)
        #             file.write(chunk_data)
        #     else:
        #         print(f"failed {cnt} times")
        #         cnt += 1
        
        chunk_size = end - start + 1
        client.sendall(f"{start}:{end}".encode("utf_8"))
        data_list = []
        size_recv = 0
        
        while(size_recv < chunk_size):
            data = client.recv(BUFSIZE)
            data_list.append(data)
            size_recv += len(data)

        # print(f"{len(data_list)} - size\n")
        chunk_data = b"".join(data_list)
        chunk = {
                "start" : start,
                "end" : end,
                "data" : chunk_data
            }
        chunks.append(chunk)
        
        

    

def runClient():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    file_size = int (client.recv(1024).decode("utf_8"))
    file_name = "logo.png"
    number_of_threads = 4
    print(file_size)
    part = int((file_size) / number_of_threads)
    remain_data = file_size % number_of_threads
    with open(file_name, "wb") as file:
        file.write(b'\0' * file_size)

    
    for i in range(number_of_threads):
        start = part * i
        end = start + part - 1
        if (i == number_of_threads - 1):
            end += remain_data
        print(start, end)
        t = threading.Thread(target=downloadChunks, args=(client, file_name, start, end), daemon= True)
        t.start()

    main_thread = threading.current_thread() 
    for t in threading.enumerate(): 
        if t is main_thread: 
            continue
        t.join() 

    print("Check")

    for chunk in chunks:
        with open(file_name, "r+b") as file:
            file.seek(chunk["start"])   
            file.write(chunk["data"])
    # print(chunks)  

    print(os.path.getsize(file_name))
    client.close()

def main():
    runClient()

if __name__ == "__main__":
    main()