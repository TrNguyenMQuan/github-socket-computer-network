import os 
import socket
import keyboard

DIRECTORY_OF_DATA = ".\Data"
DATA_FILE_NAME = "list of files name.txt"
HOST = "127.0.0.1"
PORT = 9999
FORMAT = "utf-8"
SIZE = 1024

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(os.getcwd())


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

def listFileInPath(path):
    list_file = []
    for name in os.listdir(path):
        file_size =  os.path.getsize(os.path.join(path, name))
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
        

def runServer(HOST, PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Server is runing... ")

    client_socket, addr = server.accept()
    try:
        while True:
            file_requested = client_socket.recv(SIZE).decode(FORMAT)
            
            if not file_requested:
                print("Client disconnected")
                break

            file_size = os.path.getsize(file_requested)
            client_socket.send(str(file_size).encode(FORMAT))
            print(f"Client requested file: {file_requested} with {file_size}")

            with open(file_requested, "rb") as file:
                while True:
                    data_send = file.read(SIZE)

                    if not data_send:
                        break
                    
                    client_socket.sendall(data_send)

            print(f"File : {file_requested} sended successfully \n")
    except KeyboardInterrupt:
        client_socket.close()
    finally:
        client_socket.close()

def main():
    runServer(HOST, PORT)

if __name__ == "__main__":
    main()