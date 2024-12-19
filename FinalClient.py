import socket
import os
import threading
import time
from tkinter import *
import tkinter as tk
from tkinter import filedialog, messagebox
import keyboard
from concurrent.futures import ThreadPoolExecutor


HOST = "127.0.0.1"
PORT = 9999
FORMAT = "utf-8"
ADDR = (HOST, PORT)
SOURCE_FILE = "list_of_names.txt"
DOWNLOAD_FILE_NAME = "input.txt"
file_path = os.path.join(os.getcwd(), DOWNLOAD_FILE_NAME)
BUFFERSIZE = 1024 * 1024 * 10
NUMBER_OF_THREADS = 4

window = None
file_listbox = None
status_label = None
pending_file = []
chunks = []
downloaded_file = set()
source_file_name = set()
lock = threading.Lock()


def displayListSourceFile(SOURCE_FILE):
    try:
        with open(SOURCE_FILE, 'r') as file:
            print("[ List of file can download from server ]")
            while True:
                data = file.readline()

                if not data or data == "\n":
                    break

                print(data, end="")
                data = data.strip()
                parts = data.rsplit(" ", 2)
                if len(parts) >= 3:
                    name = ' '.join(parts[:-2]).strip()
                    source_file_name.add(name)
                
    except Exception as error:
        print(f"Error when reading file: {error}")
        file.close()
    finally:
        file.close()


def scanFileAfter5Secs(input_file):
    position = 0
    with open(input_file, "wb") as file:
        pass
    while True:
        try:
            list_new_file = []
            with open(input_file, 'r') as file:
                file.seek(position)

                while True:
                    data = file.readline()

                    if not data:
                        break

                    if data != "\n" and data.strip() in source_file_name:
                        list_new_file.append(data.strip("\n"))
                        pending_file.append(data.strip("\n"))
                    elif data != "\n" and data.strip() not in source_file_name:
                        list_new_file.append("Invalid file name")
                position = file.tell()  

                if list_new_file:
                    displayGUI(list_new_file)
        except Exception as error:
            print(f"Error scanning input file: {error} ")
            file.close()
        finally:
            file.close()

        time.sleep(5)


def displayGUI(list_new_files):
    global file_listbox, status_label
    for file_requested in list_new_files:
        file_listbox.insert(END, file_requested)
    status_label.config(text=f"Status: Detected {len(list_new_files)} new file(s)")


def showDuplicateFileWarning(file_requested):
    if file_requested in downloaded_file:
        option = messagebox.askyesno(
            title = "File Already Downloaded",
            message = f"File: '{file_requested}' has already been downloaded. \n"
                        "Do you want to download it again ?"
        )
        return option
    

def handleDownLoadChunk(file_name, start, end, index, output_file):
    socket_download_chunk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_download_chunk.connect(ADDR)
    socket_download_chunk.sendall(f"CHUNK".encode("utf_8"))
    
    request = socket_download_chunk.recv(8).decode("utf_8")
    if request != "CHUNK-OK":
        print("Fail to download chunk")
        return
    
    socket_download_chunk.sendall(f"{file_name}:{start}:{end}".encode("utf_8"))
    chunk_size = end - start + 1
    data_recv = 0

    with open(output_file, "r+b") as file:
        file.seek(start)
        while data_recv < chunk_size:
            data = socket_download_chunk.recv(min(BUFFERSIZE, chunk_size - data_recv))
            data_recv += len(data)
            file.write(data)
            time.sleep(0.5)
            print(f"Downloading {file_name} part {index} {(data_recv * 100) // chunk_size} %")

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
                    print("Fail to download file")
                    return
                #send file requested
                file_requested = pending_file.pop(0)
                if showDuplicateFileWarning(file_requested) == False:
                    print(f"Skipping {file_requested}")
                    continue

                client.sendall(file_requested.encode(FORMAT))

                print(f"Downloading {file_requested}........")
        
                file_size = int(client.recv(BUFFERSIZE).decode(FORMAT))
                file_size = int(file_size)
            
                #open dialog to select folder to save file
                download_folder_path = filedialog.askdirectory(title="Select folder to save file")
                if not download_folder_path:
                    print("No folder selected")
                    return
                
                file_name_download = handleDuplicateFileName(file_requested, download_folder_path)
                output_file = os.path.join(download_folder_path, file_name_download)
                
                part = file_size // NUMBER_OF_THREADS
                remain_data = file_size % NUMBER_OF_THREADS

                with open(output_file, "wb") as file:
                    pass

                with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
                    futures = []
                    for i in range(NUMBER_OF_THREADS):
                        start = part * i
                        end = start + part - 1
                        if i == NUMBER_OF_THREADS - 1:
                            end += remain_data 
                        chunk_size = end - start + 1

                        futures.append(executor.submit(handleDownLoadChunk, file_requested, start, end, i + 1, output_file))


                    for future in futures:
                        future.result() 

                if (file_size == os.path.getsize(output_file)):
                    print(f"File {file_requested} downloaded successfully \n")
                else:
                    print(f"Fail to download {file_requested} \n")

                downloaded_file.add(file_requested)

                print(f"Ctrl + C to exit \n")
                client.close()
                
            status_label.config(text="Status: No new files to download")
            time.sleep(1)

    except KeyboardInterrupt:
        client.close()


def handleDuplicateFileName(file_name, download_folder_path):
    base_name, ext = os.path.splitext(file_name)
    list_numbers = set()
    
    for file in os.listdir(download_folder_path):
        if file == file_name:
            list_numbers.add(0)
            continue
        base_tmp, ext_tmp = os.path.splitext(file)
        base_tmpsplit = base_tmp.split()
        if base_tmpsplit[0] == base_name and ext_tmp == ext:
            list_numbers.add(int(base_tmpsplit[1][0]))
    count = 0
    while count in list_numbers:
        count += 1
    if count == 0:
        return file_name
    return f"{base_name}({count}){ext}"


def handleGreeting():
    socket_greeting = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_greeting.connect(ADDR)
    socket_greeting.sendall(f"GREETING".encode("utf_8"))
    
    request = socket_greeting.recv(11).decode("utf_8")
    if request != "GREETING-OK":
        print("Fail to communicate with server")
        return
    print("Connected successfully ! \n")   
    file_name, file_size = socket_greeting.recv(1024).decode(FORMAT).split(":")
    file_size = int(file_size)
    socket_greeting.sendall(f"ACK".encode())
    file_data = socket_greeting.recv(file_size)
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
        displayListSourceFile(SOURCE_FILE)
    except Exception as error:
        print(f"Error: {error}")
        exit(0)
    threading.Thread(target=scanFileAfter5Secs, daemon=True, args=(file_path,), name="scanFileAfter5Secs").start()
    threading.Thread(target=downloadFile, daemon=True, args=(), name="downloadFile").start()

    try:
        window.mainloop()
    except KeyboardInterrupt:
        print("Disconnected by Crtl + C")
        window.destroy()


def main():
    global window

    try:
        setupGUI()
        runClient()

    except KeyboardInterrupt:
        try:
            if window is not None and window.winfo_exists():
                window.quit() 
                window.destroy()
        except Exception as error:
            print(f"Error :{error}")
        finally:
            window = None
    except Exception as error:
        print(f": {error}")
    finally:
        if window is not None:
            try:
                window.quit() 
                window.destroy()
            except:
                pass


if __name__ == "__main__":
    main()