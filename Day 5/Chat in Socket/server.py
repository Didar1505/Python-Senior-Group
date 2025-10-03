import socket
import threading

hostname = socket.gethostname()
port = 12345

clients = []
usernames = []

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = usernames[index]
                broadcast(f"{username} has left the chat.".encode(), client)
                usernames.remove(username)

def handle_client(client:socket.socket):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = usernames[index]
                broadcast(f"{username} has left the chat.".encode(), client)
                usernames.remove(username)
                break
            broadcast(message, client)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f"{username} has left the chat.".encode(), client)
            usernames.remove(username)
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((hostname, port))
    server.listen()
    
    print(f"Server started on: {hostname}:{port}")

    while True:
        client, address = server.accept()
        print(f"Connected with: {str(address)}")

        client.send("GET_USERNAME".encode())
        username = client.recv(1024).decode()
        usernames.append(username)
        clients.append(client)

        print(f"Username of the client is: {username}")
        broadcast(f"{username} has joined the chat".encode(), client)
        client.send(f"Connected to the server".encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == '__main__':
    start_server()