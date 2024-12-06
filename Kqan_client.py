import socket
import os
import threading
import time
from tkinter import *
import keyboard

HOST = "127.0.0.1"
PORT = 9999
FORMAT = "utf-8"
DOWNLOAD_FILE_NAME = "input.txt"
SIZE = 1024 

window = None
file_listbox = None
status_label = None
pending_file = []


def scanFileAfter5Secs(source_file_name):
    position = 0
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


def downloadFile(client: socket.socket):
    global status_label
    try:
        while True:
            while pending_file:
                file_requested = pending_file.pop(0)
                client.sendall(file_requested.encode(FORMAT))
                file_size = int(client.recv(SIZE).decode(FORMAT))
                print(f"Downloading {file_requested}........")

                with open(f"dowloaded_{file_requested}", "wb") as file:
                    temp = 0
                    while temp < file_size:
                        data_received = client.recv(min(SIZE, file_size))
                        file.write(data_received)
                        temp += len(data_received)

                print(f"File {file_requested} downloaded successfully \n")
            
            status_label.config(text="Status: No new files to download")
            time.sleep(5)

    except KeyboardInterrupt:
        client.close()
    finally:
        client.close()


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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    try:
        print("Connected successfully ! \n")    
    except Exception as error:
        print(f"Something's wrong with {error}")
        client.close()
        exit(0)
    
    threading.Thread(target=scanFileAfter5Secs, daemon=True, args=(DOWNLOAD_FILE_NAME,)).start()
    threading.Thread(target=downloadFile, daemon=True, args=(client,)).start()

    window.mainloop() 


def main():
    setupGUI()
    runClient()


if __name__ == "__main__":
    main()
