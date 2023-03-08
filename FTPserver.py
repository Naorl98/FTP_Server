import socket
import select
import random
import time

ip = "127.0.0.1"
port = 30190
time_out = 10
packet_maxsize = 1024
files_names = "files\\files.txt"
all_clients = []
global f, buffer, seq_packet, larrived, index_packet, resp, changed


def ifExist(name):
    names = open(files_names, 'r')
    line = "a"
    while line:
        line = names.readline()
        if line[:-1] == name:
            names.close()
            return True
    names.close()
    return False


def finish(file, tochange, index_pac, buff):
    print("in finish")
    if tochange:
        buffersort = []
        for i in range(len(index_pac)):
            buffersort.append("")
        for j in range(len(index_pac)):
            buffersort[index_pac[j]] = buff[j]
        for q in range(len(buffersort)):
            file.write(buffersort[q])
    else:
        for i in range(len(buff)):
            file.write(buff[i])
    print("File received")


def down_finish(serve_sock, address, buff):
    data = ""
    tries = 3
    timescount = 0
    while data.encode() != "ACK-ALL":
        try:
            data = serve_sock.recvfrom(packet_maxsize)
            if data[:4].decode() == "ERR2":
                serve_sock.sendto(buff[int(data[4:])].encode(), address)
            elif data[:4].decode() == "ERR1":
                serve_sock.sendto("ACK_R".encode(), address)
        except ValueError:
            timescount += 1
            if timescount < tries:
                serve_sock.sendto("ACK_R", address)
            else:
                print("Client Error")
                return False
    return True


def download(server_socket, address):
    err = 0
    while err == 0:
        msgs, add = server_socket.recvfrom(packet_maxsize)
        if add != address:
            server_socket.sendto("WAIT".encode(), add)
        elif msg[0].decode() == "F":
            if not ifExist(msg[1:].decode()):
                server_socket.sendto("ERR1".encode(), add)
                break
            else:
                err = 1
    if err == 0:
        print("Wrong file")
        return
    f = open(msg[1:].decode(), "r")
    buffer_send = []
    index_send = []
    i = 0
    amount = f.__sizeof__() / packet_maxsize
    server_socket.sendto(str(amount).encode(), address)
    server_socket.settimeout(time_out)
    while True:
        if i == amount:
            end = down_finish(server_socket, address, buffer_send)
            if end:
                print("File send")
            break
        data = f.read(packet_maxsize)
        server_socket.sendto(data.encode(), address)
        buffer_send.append(data)
        index_send.append(i)
        i += 1
        time.sleep(0.01)

        if i == amount:
            seq = "L" + str(i)
            server_socket.sendto(seq.encode(), address)
        else:
            seq = "P" + str(i)
            server_socket.sendto(seq.encode(), address)


def upload(server_socket, address):
    print("in Upload")
    global f, buffer, seq_packet, larrived, index_packet, resp, changed
    seq_packet = 0
    changed = False
    larrived = False
    buffer = []
    index_packet = []
    resp = []
    count = 0
    pcount = 0
    filename = ""
    while count < 2:
        pro, add = server_socket.recvfrom(packet_maxsize)
        if add != address:
            server_socket.sendto("WAIT".encode(), add)
        elif pro[:1].decode() == "F":
            if ifExist(pro[1:].decode()):
                print("Error1 - with client: " + str(address))
                server_socket.sendto("ERR1".encode(), address)
                return
            else:
                server_socket.sendto("ACK".encode(), address)
                filename = pro[1:].decode()
                print("File - " + filename + " from client: " + str(address))
                count = count + 1
        elif pro[:1].decode() == "S":
            pcount = int(pro[1:].decode())
            print("File size - " + str(pcount))
            count = count + 1
    f = open("files\\" + filename, 'w')
    names = open(files_names, 'a')
    names.write(filename+"\n")
    names.close()
    print("open file")

    server_socket.sendto("ACK".encode(), address)
    server_socket.settimeout(time_out)
    while True:
        if seq_packet == pcount:
            print("go to finish upload")
            finish(f, changed, index_packet, buffer)
            server_socket.settimeout(None)
            larrived = False
            server_socket.sendto("ACK-ALL".encode(), address)
            break
        elif larrived and seq_packet < pcount:
            server_socket.sendto("ERR3".encode(), address)
        try:
            data, add = server_socket.recvfrom(packet_maxsize)
            if add == address:
                if data[:5].decode() == "ACK_R":
                    if pcount > seq_packet > 0:
                        lost = []
                        for i in range(pcount):
                            if i not in index_packet:
                                lost.append(i)
                        for i in range(len(lost)):
                            server_socket.sendto("ERR2".encode() + lost[i], address)
                            data, add = server_socket.recvfrom(packet_maxsize)
                            buffer.append(data.decode())
                            seq_packet = seq_packet + 1
                            if index_packet and lost[i] < index_packet[-1]:
                                changed = True
                            index_packet.append(lost[i])
                else:
                    buffer.append(data.decode())
                    seq_packet = seq_packet + 1
                    data, add = server_socket.recvfrom(packet_maxsize)
                    num = int(data[1:].decode())
                    if index_packet and num < index_packet[-1]:
                        changed = True
                    index_packet.append(num)
                    if data[:1].decode() == "L":
                        larrived = True
            else:
                server_socket.sendto("WAIT".encode(), add)
        except TimeoutError:
            print("Time Out")
            break
    seq_packet = 0
    index_packet = []
    buffer = []
    changed = False
    f.close()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((ip, port))
    print("Server is ready")

    while True:

        msg, c_add = server.recvfrom(1024)
        if msg[:3].decode() == "NEW":
            all_clients.append(c_add)
            server.sendto("ACK".encode(), c_add)
            print("New client - " + str(c_add) + "\n")
        elif msg[:2].decode() == "UP":
            if c_add in all_clients:
                server.sendto("ACK".encode(), c_add)
                print("send ACK")
                upload(server, c_add)
                msg = ""
            else:
                server.sendto("NACK".encode(), c_add)
                print("Send NACK")
        elif msg[:2] == "DO":
            if c_add in all_clients:
                server.sendto("ACK".encode(), c_add)
                print("send ACK")
                download(server, c_add)
                msg = ""

            else:
                server.sendto("NACK".encode(), c_add)
