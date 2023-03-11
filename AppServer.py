import socket
import os
import time

filesNames = []

packet_max = 1024
ip = "127.0.0.1"
port = 30190
files_names = "files\\files.txt"


def getall():
    allnames = open(files_names, 'r')
    lines = []
    line = allnames.readline()
    count = 0
    while line:
        line = allnames.readline()
        if line[:-1] != "files.txt":
            lines.append(line[:-1] + "?")
            count += 1
    allnames.close()
    lines.sort()
    send = ""
    for i in range(count):
        send += lines[i]
    return send


def ifExist(name):
    link = open(files_names, 'r')
    line = "a"
    while line:
        line = link.readline()
        if line[:-1] == name:
            link.close()
            return True
    link.close()
    return False


def download(cs):
    print("In download")
    global packet_max
    try:
        name = cs.recv(1024)
        filename = name.decode()
        f = open("files\\" + filename, 'br')
        file_stats = os.stat("files\\" + filename)
        size = file_stats.st_size
        print("Send file: " + filename + ", size = " + str(size))
        cs.send(str(size).encode())
        count = 0
        offset = 0
        while count < size:
            s = cs.sendfile(f, offset, packet_max)
            count += s
            if (size - count) - packet_max < 0:
                packet_max = size - count
        msg = cs.recv(packet_max)
        if msg[:3].decode() == "FIN":
            print("Finish - file sent and received")
            return
    except socket.timeout:
        print("Time Out")
        return
    except socket.error as e:
        print("Socket error - ", e)
        return
    except Exception as c:
        print(f"ERROR: {c}")
        return


def upload(csocket):
    global packet_max
    print("in upload")
    try:
        name = csocket.recv(1024)
        filename = name.decode()
        if ifExist(filename):
            print("File exist")
            csocket.send("ERR1".encode())
            return
        else:
            print("Send OK")
            csocket.send("OK".encode())
        f = open("files\\" + filename, 'w')
        files = open(files_names, 'a')
        files.write(filename + "\n")
        files.close()
        size = int(csocket.recv(1024).decode())
        csocket.send("OK".encode())

        count = 0
        while count < size:
            buf = csocket.recv(packet_max).decode()
            if buf.encode() == "STOP":
                time.sleep(0.02)
                buf = csocket.recv(packet_max).decode()
                if buf == "BYE":
                    print("Client choose to stop")
                    return
                if buf == "CON":
                    print("Client choose to continue")
                    continue
            else:
                count += len(buf)
                f.write(buf)
                if (size - count) - packet_max < 0:
                    packet_max = size - count
        print("Receive file, send ack all")
        csocket.send("ACK_ALL".encode())
        return
    except socket.timeout:
        print("Time Out")
    except socket.error as e:
        print("Socket error - ", e)
    except Exception as c:
        print(f"ERROR: {c}")


def tcpmenu(cient_socket):
    global packet_max
    mysocket.settimeout(5)
    while True:
        try:
            msg = client.recv(packet_max)
            if msg.decode() == "UP":
                upload(client)
                packet_max = 1024
            elif msg.decode() == "DO":
                allfiles = getall()
                allfiles = "ALL" + allfiles
                cient_socket.send(allfiles.encode())
                print("Send ALL")
                download(client)
                packet_max = 1024
            elif msg.decode() == "FN":
                print("Client " + str(client) + " leave the server")
                return
        except socket.timeout:
            print("Time Out")
        except socket.error as e:
            print("Socket error - ", e)
        except Exception as c:
            print(f"ERROR: {c}")


if __name__ == "__main__":
    if not ifExist("files.txt"):
        names = open(files_names, 'a')
        names.write("files.txt\n")
        names.close()
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.bind((ip, port))
    print('The server is ready')
    mysocket.settimeout(None)
    mysocket.listen(5)
    while True:
        try:
            client, address = mysocket.accept()
            tcpmenu(client)
            mysocket.settimeout(None)
        except socket.error as e:
            print("Socket error - ", e)
