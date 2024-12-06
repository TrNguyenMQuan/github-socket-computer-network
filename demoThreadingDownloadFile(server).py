import time
import threading
import socket
import os

HOST = "localhost"
PORT = 9999
ADDR = (HOST, PORT)
BUFSIZE = 1024*1024
chunks = []
lock = threading.Lock()

def sendChunks(client_socket, file_name, new_file_name):
    with lock:
        start, end = client_socket.recv(1024*2).decode("utf_8").split(":")
        # print((start, end))
        start = int(start)
        end = int(end)
        chunk_size = end - start + 1
        sent_data = 0
        while sent_data < chunk_size:
            with open(file_name, "rb") as file:
                file.seek(start + sent_data)
                chunk_data = file.read(min(chunk_size, BUFSIZE))
                client_socket.sendall(chunk_data)
                sent_data += min(chunk_size, BUFSIZE)
                # print(chunk_data)
                
                
                # chunk = {
                #     "start" : start,
                #     "end" : end,
                #     "data" : chunk_data
                # }
                # chunks.append(chunk)
            
    

def runServer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(1)
    print(f"server is running... ")

    client_socket, addr = server.accept()
    file_name = "logo.png"
    file_size = os.path.getsize(file_name)
    client_socket.send(str(file_size).encode("utf_8"))
    
    new_file = "1" + file_name
    with open(new_file, "wb") as file:
        file.write(b'\0' * file_size)
    
    

    number_of_threads = 4
    for i in range(number_of_threads):
        t = threading.Thread(target=sendChunks, args=(client_socket, file_name, new_file), daemon= True)
        t.start()

    main_thread = threading.current_thread() 
    for t in threading.enumerate(): 
        if t is main_thread: 
            continue
        t.join() 

    # for chunk in chunks:
    #     with open(new_file, "r+b") as file:
    #         file.seek(chunk["start"])   
    #         file.write(chunk["data"])  

    client_socket.close()
    server.close()

def main():
    runServer()

if __name__ == "__main__":
    main()