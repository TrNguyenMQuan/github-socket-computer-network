import os 
import socket
DIRECTORY_OF_DATA = ".\Data"
DATA_FILE_NAME = "list of files name.txt"


# -----------------------------------------------------
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
        
# -----------------------------------------------------


def runServer(HOST, PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("Server is runing... ")

    client_socket, addr = server.accept()
    print(f"connected to {addr}")
    client_socket.send(f"Hello, you are connecting to server at {(HOST, PORT)}".encode("utf_8"))

    
    # this code is used to combine with the main code
    list_file = listFileInPath(DIRECTORY_OF_DATA)
    
    printListFile(DATA_FILE_NAME, list_file)
    
    with open(DATA_FILE_NAME, "rb") as file:
        file_size = os.path.getsize(DATA_FILE_NAME)
        file_data = file.read()
        client_socket.send(str(file_size).encode("utf_8"))
        client_socket.sendall(file_data)

    print(client_socket.recv(1024).decode("utf_8"))

    client_socket.close()
    server.close()
    

def main():
    # directory_path = '.\data'
    # list_file = listFileInPath(directory_path)
    # for file in list_file:
    #     for key, value in file.items():
    #         print(f"{key} {value}")

    runServer("localhost", 9999)

if __name__ == "__main__":
    main()