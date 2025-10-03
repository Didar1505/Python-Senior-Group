# client.py
import socket
import threading

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'GET_USERNAME':
                # Server is requesting the username
                client_socket.send(username.encode('utf-8'))
            else:
                # Print the received message
                print(message)
        except:
            # An error occurred, likely the server has closed the connection
            print("An error occurred. Disconnected from server.")
            client_socket.close()
            break

# Function to send messages to the server
def send_messages(client_socket, username):
    while True:
        # Wait for user input
        message = input(f"You ({username}):")
        # Format the message with the username
        formatted_message = f"{username}: {message}"
        try:
            # Send the message to the server
            client_socket.send(formatted_message.encode('utf-8'))
        except:
            # Handle connection error
            print("Failed to send message. Connection might be closed.")
            client_socket.close()
            break

# Main function to start the client
def start_client():
    global username
    # Ask the user for their username
    username = input("Choose your username: ")

    # Create a new socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the server
        hostname = socket.gethostname()
        port=12345
        client.connect((hostname, port))
    except:
        print("Unable to connect to the server.")
        return

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # Start the main thread to send messages
    send_messages(client, username)

if __name__ == "__main__":
    start_client()
