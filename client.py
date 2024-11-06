import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

HOST = '10.220.44.200'  
PORT = 9999

local_document = ""  # The local document content
update_delay = 100  # Delay in milliseconds

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket, status_bar):
    global local_document
    while True:
        try:
            # Receive the document update from the server
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message:
                # Merge the server update into the local document
                merge_document(text_widget, server_message)
                status_bar.config(text=f"Connected with server: {HOST}")
        except Exception as e:
            status_bar.config(text="Disconnected")
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to merge server updates with the local document
def merge_document(text_widget, server_update):
    global local_document
    cursor_position = text_widget.index(tk.INSERT)

    if server_update != local_document:
        local_document = server_update
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, local_document)

        text_widget.mark_set(tk.INSERT, cursor_position)

# Function to send only the changed portion of the document to the server
def send_partial_update(client_socket, text_widget):
    global local_document
    current_content = text_widget.get(1.0, tk.END).strip()
    
    if current_content != local_document:
        client_socket.sendall(current_content.encode())
        local_document = current_content

# Function to detect keypresses and schedule updates to the server
def on_key_release(event, client_socket, text_widget):
    if hasattr(on_key_release, "after_id"):
        text_widget.after_cancel(on_key_release.after_id)

    on_key_release.after_id = text_widget.after(update_delay, send_partial_update, client_socket, text_widget)

# Function to save the document locally
def save_document(text_widget):
    current_content = text_widget.get(1.0, tk.END).strip()
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if save_path:
        with open(save_path, "w") as file:
            file.write(current_content)
        print(f"Document saved to {save_path}")

# Adds line numbers to the text widget
def add_line_numbers(text_widget, line_number_widget):
    line_numbers = '\n'.join(str(i) for i in range(1, int(text_widget.index('end').split('.')[0])))
    line_number_widget.config(state='normal')
    line_number_widget.delete(1.0, 'end')
    line_number_widget.insert('end', line_numbers)
    line_number_widget.config(state='disabled')

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        root = tk.Tk()
        root.title("Collaborative Code Editor")

        # Create main frames for layout
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill='both')

        # Line numbers frame
        line_numbers = tk.Text(main_frame, width=4, padx=4, takefocus=0, border=0, background='lightgrey', state='disabled')
        line_numbers.pack(side='left', fill='y')

        # Code editor text widget with font settings
        text_widget = tk.Text(main_frame, wrap='none', font=('Courier New', 12), undo=True)
        text_widget.pack(expand=True, fill='both', side='left')

        # Scrollbars
        y_scroll = ttk.Scrollbar(root, orient='vertical', command=text_widget.yview)
        y_scroll.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=y_scroll.set)

        # Status bar to show connection status
        status_bar = tk.Label(root, text=f"Connected with server: {HOST}", bd=1, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')

        # Menu for save functionality
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save File", command=lambda: save_document(text_widget))
        menu_bar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menu_bar)

        # Bind key release events to schedule document updates to the server
        text_widget.bind("<KeyRelease>", lambda event: on_key_release(event, client, text_widget))
        
        # Update line numbers
        text_widget.bind("<KeyRelease>", lambda event: add_line_numbers(text_widget, line_numbers))

        # Start a thread to receive the document from the server
        receive_thread = threading.Thread(target=update_document_from_server, args=(text_widget, client, status_bar))
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
