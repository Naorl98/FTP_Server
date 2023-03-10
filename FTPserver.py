import socket
import os

ip = "127.0.0.1"
port = 30190
time_out = 5
packet_maxsize = 1024
files_names = "files\\files.txt"
global f, buffer, seq_packet, larrived, index_packet, resp, changed


def recivepac(s, c):
    err = 0
    msgs = ""
    while err == 0:
        try:
            msgs, add = s.recvfrom(packet_maxsize)
            if add != c:
                s.sendto("WAIT".encode(), add)
            else:
                err = 1
        except TimeoutError:
            print("time out")
    return msgs

#
# def window(i, num, co):
#     global count_of_waiting, count_size, max_wait, packet_maxsize
#     sum = 0
#     if i == 1:
#         count_of_waiting += 1
#         if count_of_waiting > max_wait:
#             count_size += 1
#             max_wait *= 2
#             packet_maxsize *= 2
#             sum = co - num
#             sum /= 2
#             sum = num + sum
#             return 0, sum
#     else:
#         while count_of_waiting < max_wait / 2:
#             max_wait /= 2
#             count_size -= 1
#             packet_maxsize /= 2
#             sum += 1
#         return 1, sum


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


def getall():
    names = open(files_names, 'r')
    lines = []
    line = names.readline()
    count = 0
    while line:
        line = names.readline()
        if line[:-1] != "files.txt":
            lines.append(line[:-1] + "?")
            count += 1
    names.close()
    lines.sort()
    send = ""
    for i in range(count):
        send += lines[i]
    return send


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
    print("Finish send packets")
    data = "".encode()
    tries = 3
    timescount = 0
    while data.decode() != "ACK-ALL":
        try:
            data, zero = recivepac(serve_sock, address)
            if data[:3].decode() == "BYE":
                print("Client - " + str(address) + " send BYE")
                return False
            elif data[:4].decode() == "ERR2":
                serve_sock.sendto(buff[int(data[4:])].encode(), address)
            elif data[:4].decode() == "ERR3":
                serve_sock.sendto("ACK_R".encode(), address)
        except TimeoutError:
            serve_sock.settimeout(None)
            timescount += 1
            if timescount < tries:
                serve_sock.sendto("ACK_R", address)
                print("Time finished - again")
            else:
                print("To much tries")
                serve_sock.sendto("BYE", address)
                return False
    return True


def download(server_socket, address):
    print("In download")
    msgs, zero = recivepac(server_socket, address)
    print("*****************************")
    print("Got file name: " + msgs.decode())
    df = open("files\\" + msgs.decode(), "r")
    buffer_send = []
    index_send = []
    i = 0
    file_stats = os.stat("files\\" + msgs.decode())
    amount = int(file_stats.st_size / packet_maxsize) + 1
    server_socket.sendto(str(amount).encode(), address)
    msgs, zero = recivepac(server_socket, address)
    print("Got from client: " + str(address) + " - " + msgs.decode())
    if msgs.decode() != "ACK":
        return
    server_socket.settimeout(time_out)
    while True:
        print("hi")
        if i == amount:
            end = down_finish(server_socket, address, buffer_send)
            if end:
                print("File sent")
                server_socket.settimeout(None)
                break
            else:
                print("Error to send file")
        data = df.read(packet_maxsize)
        server_socket.sendto(data.encode(), address)
        buffer_send.append(data)
        index_send.append(i)
        i += 1

        if i == amount:
            seq = "L" + str(i)
            server_socket.sendto(seq.encode(), address)
        else:
            seq = "P" + str(i)
            server_socket.sendto(seq.encode(), address)
        print("Send Packet: " + str(seq))
    df.close()


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
        pro = recivepac(server_socket, address)
        if pro[:1].decode() == "F":
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
    names.write(filename + "\n")
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
            data = recivepac(server_socket, address)
            if data[:5].decode() == "ACK_R":
                if pcount > seq_packet > 0:
                    lost = []
                    for i in range(pcount):
                        if i not in index_packet:
                            lost.append(i)
                    for i in range(len(lost)):
                        server_socket.sendto(("ERR2" + str(lost[i])).encode(), address)
                        data = recivepac(server_socket, address,)
                        buffer.append(data.decode())
                        seq_packet = seq_packet + 1
                        if index_packet and lost[i] < index_packet[-1]:
                            changed = True
                        index_packet.append(lost[i])
            else:
                info = data.decode()
                data = recivepac(server_socket, address)
                if data[:1].decode() == "L" or data[:1].decode() == "P":
                    buffer.append(info)
                    seq_packet = seq_packet + 1
                    num = int(data[1:].decode())
                    if index_packet and num < index_packet[-1]:
                        changed = True
                    index_packet.append(num)
                    if data[:1].decode() == "L":
                        larrived = True
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
        if not ifExist("files.txt"):
            names = open(files_names, 'a')
            names.write("files.txt\n")
            names.close()
        msg, c_add = server.recvfrom(1024)
        if msg[:3].decode() == "NEW":
            server.sendto("ACK".encode(), c_add)
            print("New client - " + str(c_add) + "\n")
        elif msg[:2].decode() == "UP":
            server.sendto("ACK".encode(), c_add)
            print("send ACK")
            upload(server, c_add)
            msg = ""
        elif msg[:2].decode() == "DO":
            print("get DO")
            allfiles = getall()
            allfiles = "ACK" + allfiles
            server.sendto(allfiles.encode(), c_add)
            print("send ACK and files list")
            download(server, c_add)
            msg = ""
