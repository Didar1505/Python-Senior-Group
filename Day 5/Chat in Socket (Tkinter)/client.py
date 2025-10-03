import tkinter as tk
from tkinter import messagebox
import socket
import json
from threading import Thread

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Client setup
HOST = config['ip']
PORT = config['port']
BUFSIZ = 1024
ADDR = (HOST, PORT)

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect(ADDR)

# GUI setup
root = tk.Tk()
root.title('Chat')
root.geometry('450x450')
root.resizable(False, False)
root.option_add('*Font', 'Calibri 11')
root.option_add('*Background', 'white')

messages_frame = tk.Frame(root)
my_msg = tk.StringVar()
scrollbar = tk.Scrollbar(messages_frame)
msg_list = tk.Listbox(messages_frame, height=20, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tk.Entry(root, width=62, textvariable=my_msg)
entry_field.bind("<Return>", lambda event: send())
entry_field.pack()
send_button = tk.Button(root, text="Send", width=15, command=lambda: send())
send_button.pack()

def receive():
    while True:
        try:
            msg = CLIENT.recv(BUFSIZ).decode("utf8")
            n = 60
            for i in range(0, len(msg), n):
                msg_list.insert(tk.END, msg[i:(i + n)])
        except OSError:
            break

def send(event=None):
    msg = my_msg.get()
    my_msg.set('')
    CLIENT.send(bytes(msg, 'utf8'))
    if msg == '{quit}':
        CLIENT.close()
        root.quit()

def on_closing(event=None):
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        my_msg.set('{quit}')
        send()
        CLIENT.close()
        root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start receive thread
RECEIVE_THREAD = Thread(target=receive)
RECEIVE_THREAD.start()

# Start main loop
root.mainloop()