# TCP Chat App
## Overview
A Python-based **TCP chat application** supporting multiple clients with **broadcast (group chat)** and **unicast (private messages)**.  
Designed to provide a **reliable, real-time chat experience** using socket programming and multithreading.

## Features

### Server
- Manages multiple clients with unique usernames.  
- Handles client connections, disconnections, and username validation.  
- Supports **broadcast** and **unicast** messaging.  
- Sends **join/leave notifications**.  
- Uses **threading with locks** to prevent race conditions.  
- Implements **error codes** for reliable communication:
  
       0 – Client exit
       1 – Server requests readiness
       1RDY – Client ready acknowledgment
       2 – Valid username
       3 – Invalid username
       4 – Recipient not found

### Client
- Connects to server with a unique username.  
- Sends/receives **broadcast** and **private messages**.  
- Handles **real-time simultaneous input/output** using `msvcrt`.  
- Supports **graceful exit** with `/quit` command.  
- Displays messages clearly using `safe_print()` with thread locks.  
- Responds to server **error codes**.

## Design Highlights
- **Multithreading:** Each client handled on a separate thread for concurrent communication.  
- **Publish–subscribe model:** Ensures proper message broadcast without duplication.  
- **Username management:** Dictionary-based storage for O(1) lookup and deletion.  
- **Error handling:** Try-except blocks to prevent crashes during socket operations.  
- **Handshake system:** Initial two-way handshake (`1`/`1RDY`) ensures proper message initiation.

## User Experience
- Clear prompts and notifications (join/leave, invalid usernames, missing recipients).  
- Real-time typing and message display without interruption.  
- Interactive and responsive terminal-based interface.

## Challenges & Solutions
- **Simultaneous I/O :** Terminal shared both input and output areas. Resolved using `msvcrt` and `kbhit` (input buffering).  
- **Race conditions:** Managed with `threading.Lock()`.  
- **Unique usernames:** Dictionary for O(1) lookup.  
- **Initial handshake:** Ensures correct transmission of initial server messages.

## Conclusion
- Supports **multiple clients**, **broadcast/unicast messaging**, and robust communication.  
- Learned **socket programming**, **multithreading**, live input logging, and error code design.  
- Future improvements: GUI, authentication, server-side message storage.

## Demonstration Link:
https://drive.google.com/file/d/1pQ0VWLMaBO7GVYnzYI628tDJrUVgkfjR/view?usp=sharing
