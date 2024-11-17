# Collaborative Document Editor - User Manual

Welcome to the **Collaborative Document Editor**! This tool enables multiple users to edit a shared document in real-time while also facilitating communication via a built-in chat system. This manual provides step-by-step instructions to get started and details the features of the editor.

---

## Table of Contents

1. [Features](#features)  
2. [System Requirements](#system-requirements)  
3. [Installation](#installation)  
4. [Usage Instructions](#usage-instructions)  
   - [Starting the Server](#starting-the-server)  
   - [Connecting Clients](#connecting-clients)  
5. [Features Overview](#features-overview)  
6. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)  
7. [Future Enhancements](#future-enhancements)

---

## Features

- Real-time collaborative editing with multiple users.
- Built-in chat system for communication during collaboration.
- View and edit pre-existing documents.
- Save documents locally in standard text file formats.
- View chat history and document changes when joining.
- User identification with a unique username.
- Auto-updated list of active users.
- Secure, centralized synchronization managed by a server.

---

## System Requirements

- **Python**: Version 3.7 or higher  
- **Tkinter**: Pre-installed with Python (used for the client GUI)  
- **Network**: Both server and clients must be on the same network or connected via a valid IP.  

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-link>
   cd collaborative-document-editor
   ```

2. **Install Dependencies**:
   - The project relies on standard Python libraries (no additional installations required).

3. **Run the Server**:
   ```bash
   python server.py
   ```

4. **Run the Client**:
   ```bash
   python client.py
   ```

---

## Usage Instructions

### Starting the Server
1. Navigate to the directory containing `server.py`.
2. Run the server script:
   ```bash
   python server.py
   ```
3. The server will start listening for incoming client connections on `localhost` (default port: `9999`).  
   You can modify the port in the code if needed.

### Connecting Clients
1. Navigate to the directory containing `client.py`.
2. Run the client script:
   ```bash
   python client.py
   ```
3. Enter a unique username when prompted.
4. The client will connect to the server and display:
   - A text editor for collaboration.
   - A chat panel on the right.
   - A user list at the top showing active users.

5. To start collaborating:
   - Begin typing in the text editor.
   - Use the chat panel to communicate.

---

## Features Overview

### Real-Time Editing
- Any changes made by a user are instantly updated for all connected clients.
- Users can insert or delete text, with changes synchronized across all sessions.

### Chat System
- Type messages in the chat entry box and press Enter to send.
- View all messages in the chat panel, including history when joining late.

### File Management
- **Open Existing Files**: Clients can upload files for editing (requires server integration).  
- **Save Files**: Save the current document locally using the "Save" option in the File menu.

### User List
- Displays the usernames of all connected users.
- Updates dynamically as users join or leave.

### Synchronization
- Ensures all edits and chat messages are synchronized via the server, maintaining consistency across clients.

---

## Common Issues and Troubleshooting

1. **Server Connection Issues**:
   - Ensure the server is running and accessible via the provided IP and port.
   - Verify network settings (clients and server must be on the same network or connected via public IP).

2. **Username Already Taken**:
   - Choose a unique username when connecting to the server.

3. **GUI Freezing**:
   - Avoid closing the server while clients are connected.
   - Restart the client if it becomes unresponsive.

4. **Document Not Updating**:
   - Check the server logs for errors.
   - Ensure the client has a stable network connection.

5. **Chat Messages Not Displaying**:
   - Verify that the server is properly broadcasting messages.
   - Check for disconnections in the server logs.

---

## Future Enhancements

- Transition client-side implementation to a VS Code extension using TypeScript.
- Add syntax highlighting and collaborative coding features.
- Implement user authentication for enhanced security.
- Integrate version control to allow users to roll back changes.
- Enhance performance with an asynchronous server model.

---

For any issues or feedback, feel free to contact the development team. Enjoy collaborating! 😊