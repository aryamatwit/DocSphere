import socket

import socket

HOST = '10.220.52.74' #local host
PORT = 9999

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,PORT))

    welcomemsg = client.recv(1024).decode('utf-8')

    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break

        client.send(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        print(f"Server: {response}")

    client.close()

if input("Would you like to connect to the server: ").lower() == 'yes':
    start_client()


