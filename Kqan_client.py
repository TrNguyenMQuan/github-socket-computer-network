import socket
import os
import threading
import time
from tkinter import *
import tkinter as tk
from tkinter import filedialog
import keyboard


# HOST = "10.0.7.136"
HOST = "127.0.0.1"
PORT = 9999
FORMAT = "utf-8"
ADDR = (HOST, PORT)
DOWNLOAD_FILE_NAME = "input.txt"
file_path = os.path.join(os.getcwd(), DOWNLOAD_FILE_NAME)
BUFFERSIZE = 1024 * 1024 * 10
NUMBER_OF_THREADS = 4

window = None
file_listbox = None
status_label = None
pending_file = []
chunks = []
lock = threading.Lock()


def scanFileAfter5Secs(source_file_name):
    position = 0
    with open(source_file_name, "wb") as file:
        pass
    while True:
        try:
            with open(source_file_name, 'r') as file:
                file.seek(position)

                while True:
                    data = file.readline()

                    if not data:
                        break
                    if data != "\n":
                        pending_file.append(data.strip("\n"))
                position = file.tell()  

                if pending_file:
                    displayGUI(pending_file)
        except Exception as error:
            print(f"Error scanning input file: {error} ")

        time.sleep(5)


def displayGUI(list_new_files):
    global file_listbox, status_label
    for file_requested in pending_file:
        file_listbox.insert(END, file_requested)
    status_label.config(text=f"Status: Detected {len(list_new_files)} new file(s)")


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

def downloadFile():
    global status_label
    try:
        while True:
            while pending_file:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                #send type of request
                client.sendall(f"FILE".encode("utf_8"))
                request = client.recv(7).decode("utf_8")
                if request != "FILE-OK":
                    print("fail to download file")
                    return
                #send file requested
                file_requested = pending_file.pop(0)
                client.sendall(file_requested.encode(FORMAT))
                print(f"Downloading {file_requested}........")
        
                file_size = int(client.recv(BUFFERSIZE).decode(FORMAT))
                file_size = int(file_size)
                print(file_size)
                #open dialog to select folder to save file
                download_folder_path = filedialog.askdirectory(title="Chọn thư mục để lưu file")
                if not download_folder_path:
                    print("No folder selected")
                    return
                output_file = os.path.join(download_folder_path, os.path.basename(ensure_unique_filename(file_requested, download_folder_path)))
                
                part = file_size // NUMBER_OF_THREADS
                remain_data = file_size % NUMBER_OF_THREADS

                with open(output_file, "wb") as file:
                    file.write(b'\0' * file_size)

                for i in range(NUMBER_OF_THREADS):
                    start = part * i
                    end = start + part - 1
                    if i == NUMBER_OF_THREADS - 1:
                        end += remain_data
                    t = threading.Thread(target=handleDownLoadChunk, args=(file_requested, start, end, i + 1))
                    t.start()
                
                main_thread = threading.main_thread()
                for t in threading.enumerate():
                    if t is main_thread or t.name == "scanFileAfter5Secs" or t.name == "downloadFile":
                        # print(t)
                        continue
                    t.join()

                # print(len(chunks))
                with open(output_file, "r+b") as file:
                    for chunk in chunks:
                        file.seek(chunk["start"])   
                        file.write(chunk["data"])
                chunks.clear()

                print(f"File {file_requested} downloaded successfully \n")
                client.close()
                
            status_label.config(text="Status: No new files to download")
            time.sleep(1)


    except KeyboardInterrupt:
        client.close()
 
def ensure_unique_filename(file_path, download_folder_path): # Ensure the filename is unique by appending a number if the file already exists
    base, ext = os.path.splitext(file_path)
    counter = 1
    file_name = os.path.basename(file_path)
    unique_file_path = os.path.join(os.path.basename(download_folder_path),file_name)
    
    while os.path.exists(unique_file_path):
        unique_file_path = f"{base}_{counter}{ext}"
        counter += 1
    
    return unique_file_path

def handleGreeting():
    socket_greeting = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_greeting.connect(ADDR)
    socket_greeting.sendall(f"GREETING".encode("utf_8"))
    
    request = socket_greeting.recv(11).decode("utf_8")
    if request != "GREETING-OK":
        print("fail to communicate with server")
        return
    print("Connected successfully ! \n")   
    file_name, file_size = socket_greeting.recv(1024).decode(FORMAT).split(":")
    file_data = socket_greeting.recv(int(file_size))
    with open(file_name, "wb") as file:
        file.write(file_data)
    

    socket_greeting.close()

def setupGUI():
    global window, status_label, file_listbox

    window = Tk()
    window.title("File Transfer Client")
    window.resizable(False, False)
    window.attributes('-topmost', True)

    Label(window, text="Newly Added Files:").pack(pady=5)

    file_listbox = Listbox(window, width=50, height=15, justify="center")
    file_listbox.pack(pady=10)

    status_label = Label(window, text="Status: Waiting for updates...", anchor="w")
    status_label.pack(fill=X, pady=5)


def runClient():
    try: 
        handleGreeting()
    except Exception as error:
        exit(0)
    threading.Thread(target=scanFileAfter5Secs, daemon=True, args=(file_path,), name="scanFileAfter5Secs").start()
    threading.Thread(target=downloadFile, daemon=True, args=(), name="downloadFile").start()

    window.mainloop() 


def main():
    setupGUI()
    runClient()


if __name__ == "__main__":
    main()



# file đã download
# file không có trong thư mục server_data