import socket
import threading

HOST = '10.220.52.74' #local host
PORT = 9999

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

def send_msg(client_socket):
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
             break
        
        client_socket.send(msg.encode('utf-8'))

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,PORT))

    welcomemsg = client.recv(1024).decode('utf-8')

    receive_thread = threading.Thread(target=receive_msg, args=(client,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_msg, args=(client,))
    send_thread.start()

if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()


