import socket
import json
from threading import Thread

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Server setup
clients = {}
addresses = {}
users_count = 0

HOST = config['ip']
PORT = config['port']

BUFSIZ = 1024
ADDR = (HOST, PORT)

# Create TCP/IP socket
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

def broadcast(msg, prefix=''):
    for sock in clients:
        sock.send(bytes(prefix, 'utf8') + msg)

def handle_client(client):
    global users_count
    users_count += 1
    name = 'User' + str(users_count)
    welcome = 'Welcome %s!' % name
    client.send(bytes(welcome, 'utf8'))
    msg = '%s has joined the chat!' % name
    broadcast(bytes(msg, 'utf8'))
    clients[client] = name
    
    with open('chat.txt', 'a', encoding='utf8') as file:
        file.write(msg + '\n')
    
    while True:
        try:
            msg = client.recv(BUFSIZ)
            if msg != bytes('{quit}', 'utf8'):
                broadcast(msg, name + ': ')
                with open('chat.txt', 'a', encoding='utf8') as file:
                    file.write(name + ': ' + msg.decode('utf8') + '\n')
            else:
                client.close()
                del clients[client]
                broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                with open('chat.txt', 'a', encoding='utf8') as file:
                    file.write(name + ' has left the chat.' + '\n')
                break
        except:
            break

def get_new_connections():
    while True:
        client, client_address = SERVER.accept()
        print('%s:%s has connected.' % client_address)
        client.send(bytes(str(client_address) + ' has connected', 'utf8'))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

if __name__ == '__main__':
    # Initialize chat.txt with template
    with open('template.txt', 'r', encoding='utf8') as template:
        with open('chat.txt', 'w', encoding='utf8') as chat:
            chat.write(template.read())
            
    SERVER.listen(5)
    print('Waiting for connection...')
    ACCEPT_THREAD = Thread(target=get_new_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()