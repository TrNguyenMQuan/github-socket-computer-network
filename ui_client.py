from tkinter import*
from tkinter import ttk
from PIL import ImageTk, Image

IP = "127.0.0.1"
PORT = 65432
SEVER_ADDRESS = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

def write_into_input_file():
    file_name = entry.get()

    if file_name:
        try:
            with open("input.txt", "a", encoding= FORMAT) as f: 
                f.write(file_name + "\n")  

            label_status.config(text=f"File '{file_name}' has been added to file_names.txt")
            
            entry.delete(0, END)
        except Exception as e:
            label_status.config(text=f"Error: {e}")
    else:
        label_status.config(text="Please enter a file name.")

window = Tk()
window.geometry("400x450")
window.title('File Transfer Window')
window['bg'] = "#F5F7F8"
window.attributes("-topmost", TRUE)
window.resizable(False, False)

image_import = Image.open("D:\GitDemo\github-socket-computer-network\image_download.png").resize((128,128))
img = ImageTk.PhotoImage(image_import)
image_download = Label(window, image = img, bd = 0)
image_download.place(x = 136, y = 46)

notice = Label(window, text = "Input file name you want to download below",
               font = ("Poppins", 12), fg = 'black', bd = 0)
notice.place(x = 55, y = 207)

entry = Entry(window, width = 36, font = ("Poppins", 12))
entry.place(x = 40, y = 240)

download_button = Button(window, text = "Download", font = ("Poppins", 12), command = write_into_input_file)
download_button.place(x = 150, y = 290)

label_status = Label(window, text="", fg = 'red')
label_status.place(relx=0.5, y=350, anchor="center")



window.mainloop()




