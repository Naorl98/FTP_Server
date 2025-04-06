# FTP Server - Cybersecurity Project

## Overview
This project implements a custom UDP-based FTP server designed to securely and reliably handle file upload and download operations over a network. It simulates core FTP functionalities while introducing additional reliability mechanisms and error recovery to handle packet loss, out-of-order delivery, and client interruptions.

## Key Features
- **UDP-based Communication**: Built on UDP for performance, with reliability mechanisms.
- **Upload & Download**: Handles full file upload/download with support for retransmission.
- **Error Handling**: Recovers from partial transfers and packet loss with retry logic.
- **Dynamic Client Handling**: Manages multiple clients and maintains session context.
- **Logging & Acknowledgment**: Supports sequence-aware acknowledgment and completion signals.

## Project Structure
- `FTPserver.py`: The main server-side logic for handling file transfers over UDP.
- `files/files.txt`: Maintains list of uploaded/available files.

## Technologies Used
- **Language**: Python 3
- **Libraries**: `socket`, `os`, `time`

## How to Run
1. Make sure Python 3 is installed.
2. Place the `FTPserver.py` file and create a `files/` directory.
3. Run the server:
```bash
python FTPserver.py
```
4. Connect a compatible client to send commands (UPLOAD, DOWNLOAD, etc.).

## Notes
- Server uses port `30190` on `127.0.0.1` by default.
- All file operations are logged and acknowledgments are handled using custom protocol design.

## Author
Developed by Naor as part of a Cybersecurity Engineering Project.
