## **Documentation: Terminal Based Chat Application**

## Overview

This Python script facilitates a simple chat application with both server and client components. The server component manages multiple client connections, broadcasting messages to all connected clients, while the client component allows users to connect to the server, send and receive messages, and handle user interactions. The application utilizes sockets for communication, threading for concurrent operations, and basic error handling to ensure stability and responsiveness.

## Features

- **Client-Server Communication**: The script uses TCP sockets to enable communication between clients and the server.
- **User Validation**: Users are required to provide a valid username adhering to specific criteria (letters, numbers, and underscores, 3 to 20 characters long).
- **Message Broadcasting**: The server broadcasts messages from clients to all other connected clients.
- **Threaded Handling**: Both the client and server use threading to handle multiple operations concurrently, such as receiving and sending messages.
- **Graceful Exit**: Users can exit the chat session with a command, and the server will handle client disconnections gracefully.
- **Error Handling**: Comprehensive error handling ensures robustness and provides feedback in case of unexpected issues.

## Dependencies

This script relies on the following Python modules:

- **`socket`**: For network communication using TCP/IP.
- **`threading`**: For handling concurrent operations in both client and server.
- **`sys`**: For system-specific parameters and functions.
- **`re`**: For regular expression-based username validation.

These modules are part of the Python Standard Library, so no additional installations are required beyond Python itself.

## Usage

To run the chat application, you need to start both the server and client components. Below are the instructions for using each component:

### Starting the Server

1. Save the server code into a file, e.g., `server.py`.
2. Run the server script from the command line:

   ```sh
   python server.py
   ```

3. The server will start listening for incoming connections on `127.0.0.1` (localhost) on port `5555`.

### Starting the Client

1. Save the client code into a file, e.g., `client.py`.
2. Run the client script from the command line:

   ```sh
   python client.py
   ```

3. The client will prompt for a username. Enter a valid username and start chatting.

## Interactive Commands

Once connected, users can interact with the chat application using the following commands:

- **Send Message**: Type a message and press Enter to send it to all other connected users.
- **Exit Chat**: Type `/exit` to leave the chat session. This will notify other users that you have left the chat.

## Special Commands

- **Username Validation**: When a client connects, they must provide a valid username that conforms to the following pattern: `^[a-zA-Z0-9_]{3,20}$`. This pattern ensures usernames are between 3 and 20 characters long and contain only alphanumeric characters and underscores.
  
- **Message Broadcasting**: Messages sent by a client are broadcasted to all other connected clients. This functionality is handled by the server and ensures that every message is visible to all participants except the sender.

- **Connection Handling**: The server manages client connections and handles unexpected disconnections or errors gracefully. It uses threading to handle multiple clients concurrently and ensure smooth operation.

## Conclusion

This chat application script provides a foundational framework for real-time communication between multiple users. By leveraging Python's socket and threading modules, it enables a robust and interactive chat environment. The server handles incoming client connections and broadcasts messages, while the client allows users to send and receive messages effectively. The application includes basic validation, error handling, and graceful exit features, making it a solid starting point for more complex chat systems or real-time communication applications.

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### **Disclaimer:**
Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.
