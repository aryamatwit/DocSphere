import socket
import threading

# Define the server's IP address and port number
HOST = '10.220.52.74' #local host
PORT = 9999

# Function to handle communication with the server
def receive_msg(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                print(f"\n{msg}")
            else:
                break
        except:
            print("[ERROR] Lost connection to the server.")
            break

# Function to send messages to the server
def send_msg(client_socket):
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
             break
        
        client_socket.send(msg.encode('utf-8'))

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,PORT))

        welcomemsg = client.recv(1024).decode('utf-8')

        receive_thread = threading.Thread(target=receive_msg, args=(client,))
        receive_thread.start()

        send_thread = threading.Thread(target=send_msg, args=(client,))
        send_thread.start()
        
    except socket.error as errormsg:
        print(f"Failed to connect to the server: {errormsg}")

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()


