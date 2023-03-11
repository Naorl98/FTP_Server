from scapy.all import *
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from tkinter import *
import socket
import time
import os
import tkinter as tk
import random

flter = "udp and (port 67 or 68)"
BUFF = 512  # Buffer size
ip_port = ("127.0.0.1", 53)
ip = "127.0.0.1"
port = 30190
my_port = 20190
time_up = 2
time_down = 8
packet_maxsize = 1024
sorc = 0
tcpsize = 0
send = "".encode()
amount = 0
index = 0
file_name = ""
buffer_send = []
index_send = []
global sock, f, curr, tcpsocket


def home():
    global sock
    sock.close()
    dnsw.pack_forget()
    con.pack_forget()
    first.pack(fill='both', expand=1)


def home2():
    dhcpw.pack_forget()
    first.pack(fill='both', expand=1)


# ftp client start
def ftphome():
    global sock
    print("Exit ftp")
    sock.sendto("FN".encode(), (ip, port))
    sock.close()
    ftpw.pack_forget()
    first.pack(fill='both', expand=1)


def connect():
    global sock
    con.pack(fill='both', expand=1)
    maxtry = 5
    num_try = 0
    try:
        sock.sendto("NEW".encode(), (ip, port))
        time.sleep(0.02)
    except ConnectionError:
        lab.config(text="Server not open")
        lab.pack(padx=10, pady=20)
        num_try = 5
    while num_try < maxtry:
        try:
            rec, add = sock.recvfrom(packet_maxsize)
            if rec.decode() == "ACK":
                con.pack_forget()
                return True
            elif rec.decode() == "WAIT":
                print("WAIT from server " + str(num_try))
                lab.pack_forget()
                lab.config(text="Wait to server to contact.." + str(num_try) + " time")
                lab.pack(padx=10, pady=20)
                time.sleep(3)
        except socket.timeout:
            print("Time Out")
            num_try += 1
            lab.config(text="Try again.." + str(num_try) + " time")
            time.sleep(2)
        except socket.error as e:
            num_try += 1
            print(f"ERROR: {e}")
            lab.config(text="Try again.." + str(num_try) + " time")
            time.sleep(1)
    if num_try == 5:
        lab2.pack(padx=10, pady=20)
        menu2.pack(padx=10, pady=0)


def back_ftp():
    downw.pack_forget()
    ftpw.pack(fill='both', expand=1)


def ftp_client():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, my_port))
    first.pack_forget()
    if connect():
        print("Connect to server")
        ftpw.pack(fill='both', expand=1)


def enter():
    if filename.get('1.0', tk.END) != 0:
        uplo.configure(state=NORMAL)


def upload_finish(buff):
    global send, sock
    print("In upload finish")
    tries = 2
    timescount = 0
    sock.settimeout(time_up)
    while send.decode() != "ACK-ALL":
        try:
            send, add = sock.recvfrom(packet_maxsize)
            if send[:4].decode() == "ERR2":
                print("Get ERR2, Req = " + send[4:].decode())
                sock.sendto(buff[int(send[4:].decode())].encode(), (ip, port))
            elif send[:4].decode() == "ERR3":
                print("Get ERR3 and send ACK_R")
                sock.sendto("ACK_R".encode(), (ip, port))
                time.sleep(0.02)

        except socket.timeout:
            print("Time Out")
            timescount += 1
            if timescount < tries:
                print("Send ACK_R")
                sock.sendto("ACK_R".encode(), (ip, port))
            else:
                return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    return True


# def task():
#     global amount, index, ex, packet_maxsize, send, sock
#     while ex == 0:
#         n = 0
#         try:
#             data, add = sock.recvfrom(packet_maxsize)
#             send = data
#             if data[:2].decode() == "W+":
#                 news = int(send[2:])
#                 while news > packet_maxsize:
#                     news /= 2
#                     n += 1
#                 packet_maxsize = int(send[2:])
#                 sum = amount - index
#                 sum /= 2
#                 amount = index + sum
#         except:
#             ex = 0
#     ex = 0
#     return


def finish(file, tochange, index_pac, buff):
    global sock
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


def download():
    global sock
    print("in download")
    ftpw.pack_forget()
    downw.pack(fill='both', expand=1)
    print("build")
    line = ""
    sock.settimeout(1)
    try:
        sock.sendto("DO".encode(), (ip, port))
        print("send DO")
        names, add = sock.recvfrom(packet_maxsize)
    except socket.timeout:
        print("Time Out")
        home()
        return
    except socket.error as e:
        print("EXIT, socket error - ", e)
        home()
        return
    except Exception as e:
        print(f"EXIT,ERROR: {e}")
        home()
        return

    if names[:3].decode() == "ACK":
        print("got ACK")
        i = 3
        while names[i:i + 1].decode():
            if names[i:i + 1].decode() != '?':
                line += names[i:i + 1].decode()
            else:
                print("Get name:" + line)
                mylist.insert(END, line)
                line = ""
            i += 1
        mylist.pack(side=LEFT, fill=BOTH)
        scrollbar.config(command=mylist.yview)


def cfile():
    global sock
    fname = mylist.get(mylist.curselection())
    print("*********************")
    print("Choose file: " + fname)
    seq_packet = 0
    changed = False
    larrived = False
    buffer = []
    index_packet = []
    sock.sendto(fname.encode(), (ip, port))
    pcount, add = sock.recvfrom(packet_maxsize)
    pcount = int(pcount.decode())
    print("Receive size")
    fil = open(fname, 'w')
    print("open file")
    sock.sendto("ACK".encode(), (ip, port))
    sock.settimeout(time_down)
    while True:
        if seq_packet == pcount:
            print("go to finish upload")
            finish(fil, changed, index_packet, buffer)
            sock.settimeout(None)
            sock.sendto("ACK-ALL".encode(), (ip, port))
            break
        elif larrived and seq_packet < pcount:
            sock.sendto("ERR3".encode(), (ip, port))
        try:
            data, add = sock.recvfrom(packet_maxsize)
            if data[:3].decode() == "BYE":
                sock.settimeout(None)
                print("Server send BYE")
                break
            elif data[:5].decode() == "ACK_R":
                if pcount > seq_packet > 0:
                    lost = []
                    for i in range(pcount):
                        if i not in index_packet:
                            lost.append(i)
                    for i in range(len(lost)):
                        sock.sendto(("ERR2" + str(lost[i])).encode(), (ip, port))
                        data, add = sock.recvfrom(packet_maxsize)
                        buffer.append(data.decode())
                        seq_packet = seq_packet + 1
                        if index_packet and lost[i] < index_packet[-1]:
                            changed = True
                        index_packet.append(lost[i])
            else:
                info = data.decode()
                data, add = sock.recvfrom(packet_maxsize)
                if data[:1].decode() == "L" or data[:1].decode() == "P":
                    buffer.append(info)
                    seq_packet = seq_packet + 1
                    num = int(data[1:].decode())
                    if index_packet and num < index_packet[-1]:
                        changed = True
                    index_packet.append(num)
                    if data[:1].decode() == "L":
                        larrived = True
        except socket.timeout:
            print("Time Out")
            sock.sendto("BYE".encode(), (ip, port))
            break
    fil.close()
    mylist.delete(0, END)
    downw.pack_forget()
    back_ftp()


def stop():
    global f, sock
    sock.sendto("BYE".encode(), (ip, port))
    filename.delete("1.0", "end")
    filename.insert(INSERT, "Stopped")
    print("Choose to stop")
    stopb.configure(state=DISABLED)
    contib.configure(state=DISABLED)
    uplo.configure(state=DISABLED)
    f.close()


def contin():
    global index, amount, index_send, buffer_send, f, file_name, sock
    stopb.configure(state=DISABLED)
    contib.configure(state=DISABLED)
    filename.insert(INSERT, "Continue")
    sock.sendto("CON".encode(), (ip, port))
    print("Choose to continue")
    time.sleep(0.02)
    while True:
        if index == amount:
            # ex = 1
            end = upload_finish(buffer_send)
            if end:
                print("File sent")
                filename.delete("1.0", "end")
                filename.insert(INSERT, "File upload")
                uplo.configure(state=DISABLED)
            break
        data = f.read(packet_maxsize)
        sock.sendto(data.encode(), (ip, port))
        buffer_send.append(data)
        index_send.append(index)
        time.sleep(0.01)

        if index == amount - 1:
            seq = "L" + str(index)
            sock.sendto(seq.encode(), (ip, port))
        else:
            seq = "P" + str(index)
            sock.sendto(seq.encode(), (ip, port))
        index += 1
    f.close()


def upload():
    global index, amount, index_send, buffer_send, f, file_name, sock
    print("in upload")
    file_name = (filename.get('1.0', tk.END))[:-1] + ".txt"
    buffer_send = []
    index_send = []
    try:
        f = open(file_name, 'r')
    except Exception as e:
        print(f"ERROR: {e}")
        filename.delete("1.0", "end")
        filename.insert(INSERT, "File not found")
        print("File not found")
        return
    print("open file")
    sock.settimeout(1)
    try:
        sock.sendto("UP".encode(), (ip, port))
        rec, add = sock.recvfrom(packet_maxsize)
    except socket.timeout:
        print("EXIT, Time Out")
        home()
        return
    except socket.error as e:
        print("EXIT, socket error - ", e)
        home()
        return

    except Exception as e:
        print(f"EXIT,ERROR: {e}")
        home()
        return
    print("server send - " + rec.decode())
    sock.sendto(("F" + file_name).encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
    if rec.decode() == "ERR1":
        filename.delete("1.0", "end")
        filename.insert(INSERT, "File exist, Enter different name")
        filename.pack()
        uplo.configure(state=DISABLED)
        return
    print("Send file")
    file_stats = os.stat(file_name)
    amount = int(file_stats.st_size / packet_maxsize) + 1
    print("file size = " + str(amount))
    sock.sendto(("S" + str(amount)).encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
    if rec.decode() == "ACK":
        sock.settimeout(time_up)
        index = 0
        while True:
            if index == int(amount / 2):
                stopb.configure(state=NORMAL)
                contib.configure(state=NORMAL)
                sock.settimeout(None)
                sock.sendto("STOP".encode(), (ip, port))
                filename.delete("1.0", "end")
                filename.insert(INSERT, "Sent half file, continue or stop?")
                filename.pack()
                return

            data = f.read(packet_maxsize)
            sock.sendto(data.encode(), (ip, port))
            buffer_send.append(data)
            index_send.append(index)
            time.sleep(0.01)

            if index == amount:
                seq = "L" + str(index)
                sock.sendto(seq.encode(), (ip, port))
            else:
                seq = "P" + str(index)
                sock.sendto(seq.encode(), (ip, port))
            index += 1


# ftp client start

# tcp client start
def tcp_client():
    global tcpsocket
    tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsocket.bind((ip, my_port))
    first.pack_forget()
    try:
        tcpsocket.connect((ip, port))
        print("Connect to server")
        tcpw.pack(fill='both', expand=1)
    except socket.error as e:
        print("Socket error - ", e)
        tcp_home()


def tcp_home():
    global tcpsocket
    print("Exit tcp ftp")
    tcpsocket.send("FN".encode())
    tcpsocket.close()
    tcpw.pack_forget()
    first.pack(fill='both', expand=1)


def entertcp():
    if filenametcp.get('1.0', tk.END) != 0:
        uplotcp.configure(state=NORMAL)


def tcp_back():
    downtcp.pack_forget()
    tcpw.pack(fill='both', expand=1)


def tcpdownw():
    global tcpsocket
    print("in download")
    tcpw.pack_forget()
    downtcp.pack(fill='both', expand=1)
    print("build")
    line = ""
    tcpsocket.sendto("DO".encode(), (ip, port))
    print("send DO")
    try:
        alln = tcpsocket.recv(packet_maxsize)
    except socket.timeout:
        print("EXIT, Time Out")
        home()
        return
    except socket.error as e:
        print("EXIT, socket error - ", e)
        home()
        return
    except Exception as e:
        print(f"EXIT,ERROR: {e}")
        home()
        return

    if alln[:3].decode() == "ALL":
        print("got names list")
        i = 3
        while alln[i:i + 1].decode():
            if alln[i:i + 1].decode() != '?':
                line += alln[i:i + 1].decode()
            else:
                print("Get name:" + line)
                mylist2.insert(END, line)
                line = ""
            i += 1
        mylist2.pack(side=LEFT, fill=BOTH)
        scrollbar2.config(command=mylist.yview)


def downloadtcp():
    global tcpsocket
    psize = packet_maxsize
    try:
        flname = mylist2.get(mylist2.curselection())
        print("*********************")
        print("Choose file: " + flname)
        tcpsocket.send(flname.encode())
        sizef = int(tcpsocket.recv(1024).decode())
        downfile = open(flname, 'a')
        count = 0
        while count < sizef:
            buf = tcpsocket.recv(psize).decode()
            count += len(buf)
            downfile.write(buf)
            if sizef - psize < 0:
                psize = sizef
        tcpsocket.send("FIN".encode())
        tcp_back()
    except socket.timeout:
        print("Time Out")
    except socket.error as e:
        print("Socket error - ", e)
    except Exception as c:
        print(f"ERROR: {c}")


def stoptcp():
    global f, tcpsocket
    tcpsocket.send("BYE".encode())
    filenametcp.delete("1.0", "end")
    filenametcp.insert(INSERT, "Stopped")
    filenametcp.pack()
    print("Choose to stop")
    stopb.configure(state=DISABLED)
    contib.configure(state=DISABLED)
    uplotcp.configure(state=DISABLED)
    f.close()


def upload_2h():
    global f, curr, tcpsize, tcpsocket
    packet_maxx = packet_maxsize
    stopt.configure(state=DISABLED)
    contit.configure(state=DISABLED)
    filenametcp.delete("1.0", "end")
    filenametcp.insert(INSERT, "Continue")
    filenametcp.pack()
    tcpsocket.send("CON".encode())
    print("Choose to continue")
    time.sleep(0.02)
    count = 0
    while count < tcpsize:
        s = tcpsocket.sendfile(f, curr, packet_maxx)
        count += s
        curr += s
        if (tcpsize - count) - packet_maxx < 0:
            packet_maxx = tcpsize - count
    print("File sent")
    filename.delete("1.0", "end")
    filename.insert(INSERT, "File upload")
    uplo.configure(state=DISABLED)
    tcpmsg = tcpsocket.recv(packet_maxsize).decode()
    if tcpmsg == "ACK_ALL":
        print("Get ACK_ALL")
        f.close()
        tcp_back()


def upload_t():
    global f, curr, tcpsize, tcpsocket
    print("in upload")
    file_name2 = (filenametcp.get('1.0', tk.END))[:-1] + ".txt"
    try:
        f = open(file_name2, 'br')
    except Exception as e:
        print(f"ERROR: {e}")
        filename.delete("1.0", "end")
        filename.insert(INSERT, "File not found")
        print("File not found")
        tcp_back()
        return
    tcpsocket.sendto("UP".encode(), (ip, port))
    print("send UP")

    try:
        tcpsocket.send(file_name2.encode())
        server_msg = tcpsocket.recv(packet_maxsize)
        if server_msg.decode() == 'ERR1':
            filename.delete("1.0", "end")
            filename.insert(INSERT, "File exist, choose another name")
            uplotcp.configure(state=DISABLED)
            tcp_back()
            return
        file_stats = os.stat(file_name2)
        size = file_stats.st_size
        tcpsocket.send(str(size).encode())
        server_msg = tcpsocket.recv(packet_maxsize)
        if server_msg.decode() != 'OK':
            tcp_home()
            return
        count = 0
        offset = 0
        halfsize = size - int(size / 2)
        packet_max = packet_maxsize
        while count < halfsize:
            s = tcpsocket.sendfile(f, offset, packet_max)
            count += s
            if (halfsize - count) - packet_max < 0:
                packet_max = (halfsize - count)
        tcpsize = size - halfsize
        curr = count
        stopt.configure(state=NORMAL)
        contit.configure(state=NORMAL)
        tcpsocket.settimeout(None)
        print("Sent half file")
        tcpsocket.send("STOP".encode())
        filenametcp.delete("1.0", "end")
        filenametcp.insert(INSERT, "Sent half file, continue or stop?")
        filenametcp.pack()
        msg = tcpsocket.recv(packet_max)
        if msg[:3].decode() == "FIN":
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
# scp ftp client end


# dns client start
def check_domain(domain):
    # Split the domain to parts
    domain_parts = domain.split('.')
    # if it has less than 2 parts its not good : google.com has 2
    if len(domain_parts) < 2:
        return False
    return True


def domain_to_ip():
    global sock
    try:
        domain = (link.get('1.0', tk.END))[:-1]
        # Convert domain name to UTF-8 bytes
        if check_domain(domain) is False:
            link.delete("1.0", "end")
            link.insert(INSERT, "Error with this domain name, try again")
            link.pack(padx=10, pady=20)
            print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
            return
        msg = domain.encode('utf-8')
        print(f"SENDING DNS QUERY FOR {domain}")
        # Sends the query to the server
        sock.sendto(msg, ip_port)

        # Response from server
        data, server = sock.recvfrom(BUFF)
        ip_add = data.decode('utf-8')
        link.config(text="Ip address -> " + ip_add)
        link.pack(padx=10, pady=20)
        print(f"THE IP FOR {domain} is {ip_add}")
    # except socket.gaierror:
    except socket.timeout:
        link.delete("1.0", "end")
        link.insert(INSERT, "Error with this domain name, try again")
        link.pack(padx=10, pady=20)
        print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
        return
    except socket.error as e:
        print(f"ERROR: {e}")
        link.delete("1.0", "end")
        link.insert(INSERT, "Error with this domain name, try again")
        link.pack(padx=10, pady=20)
        print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        link.delete("1.0", "end")
        link.insert(INSERT, "Error with this domain name, try again")
        link.pack(padx=10, pady=20)
        print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
        return


def dns_client():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    first.pack_forget()
    dnsw.pack(fill='both', expand=1)


# dns client end


def dhcp_client():
    # send dhcp discover
    send_discover()

    # waiting for DHCP OFFER
    print("Waiting for OFFER")
    offer = sniff(filter="udp and (port 67 or port 68)", count=1)
    time.sleep(2)
    if offer:
        got_offer(offer[0])
    else:
        print("error with offer")
    print("Waiting for ACK")

    ack = sniff(filter="udp and (port 67 or port 68)", count=1)
    time.sleep(2)
    if ack:
        got_ack(ack[0])
    else:
        print("error with ack")
    print("finished client side process")
    print()


# Create the DHCP Discover packet
def send_discover():
    dhcp_discover = (Ether(dst='ff:ff:ff:ff:ff:ff') /
                    IP(src="0.0.0.0", dst="255.255.255.255") /
                    UDP(sport=68, dport=67) /
                    BOOTP(op=1, chaddr='ff:ff:ff:ff:ff:ff', xid=RandInt()) /
                    DHCP(options=[('message-type', 'discover'), 'end'])
                    )

    # Send the DHCP Discover packet
    print("SENT DISCOVER")
    sendp(dhcp_discover)


def got_offer(packet):
# Check if the packet is a DHCP Offer message
    if DHCP in packet and packet[DHCP].options[0][1] == 2:
        print("GOT OFFER")

        # Create the DHCP Request packet
        dhcp_request = (Ether(dst='ff:ff:ff:ff:ff:ff') /
                        IP(src= "0.0.0.0", dst="255.255.255.255") /
                        UDP(sport=68, dport=67) /
                        BOOTP(op=1, xid=packet[BOOTP].xid, yiaddr = packet[BOOTP].yiaddr) /
                        DHCP(options=[('message-type', 'request'), 'end'])
                        )
        # Send the DHCP Request packet
        print("SENT REQUEST")
        sendp(dhcp_request)


# Create a function to handle the DHCP ACK packet
def got_ack(packet):
    # Check if the packet is a DHCP ACK message
    if DHCP in packet and packet[DHCP].options[0][1] == 5:
        print("Got ACK")
        # Extract the assigned IP address
        assigned_ip = packet[BOOTP].yiaddr

        # Print the assigned IP address
        print(f"Assigned IP address: {assigned_ip}")
        link.config(text="Ip address -> " + assigned_ip)
        link.pack(padx=10, pady=20)
        # Configure the network interface with the assigned IP address
        conf.iface = "eth0"
        conf.route.add(net="0.0.0.0/0", gw='192.168.1.1')
        conf.route.resync()


def showdhcp():
    first.pack_forget()
    dhcpw.pack(fill='both', expand=1)  # dhcp client end


# dhcp client end


def closes():
    root.destroy()


if __name__ == '__main__':
    # root start
    root = Tk()
    root.geometry("500x500")
    root.title("Final Proj")
    # root finish

    # first start
    first = Frame(root, bg='Black')
    first.pack(fill='both', expand=1)
    label = tk.Label(first, text="Choose option", fg='Green', bg='Black', font=('Ariel', 20))
    label.pack(padx=10, pady=10)
    ftp = tk.Button(first, text="FTP", font=('Ariel', 20), bg='Green', width=40, command=ftp_client)
    ftp.pack(padx=10, pady=30)
    tcp = tk.Button(first, text="TCP", font=('Ariel', 20), bg='Green', width=40, command=tcp_client)
    tcp.pack(padx=10, pady=30)
    dns = tk.Button(first, text="DNS", font=('Ariel', 20), bg='Green', width=40, command=dns_client)
    dns.pack(padx=10, pady=30)
    dhcp = tk.Button(first, text="DHCP", font=('Ariel', 20), bg='Green', width=40, command=showdhcp)
    dhcp.pack(padx=10, pady=30)
    close = tk.Button(first, text="exit", font=('Ariel', 10), bg='Red', width=5, command=closes)
    close.pack(padx=10, pady=20)
    # first finish

    # ftp window start
    ftpw = Frame(root, bg='Black')
    ftpl = tk.Label(ftpw, text="File Transfer", bg='Black', fg='Green', font=('David', 30))
    ftpl.pack(padx=10, pady=30)
    down = tk.Button(ftpw, text="Download", font=('Ariel', 20), bg='Green', width=20, command=download)
    down.pack(padx=10, pady=10)
    ftpent = tk.Label(ftpw, text="Enter file name", bg='Black', fg='Green', font=('David', 20))
    ftpent.pack(padx=10, pady=10)
    filename = tk.Text(ftpw, height=5, font=('Ariel', 10))
    filename.pack(padx=10, pady=10)
    enter = tk.Button(ftpw, text="Enter", font=('Ariel', 10), bg='Green', width=10, command=enter)
    enter.pack(padx=10, pady=10)
    uplo = tk.Button(ftpw, text="Upload", state=DISABLED, font=('Ariel', 20), bg='Green', width=40, command=upload)
    uplo.pack(padx=10, pady=10)
    stopb = tk.Button(ftpw, text="Stop", state=DISABLED, font=('Ariel', 10), bg='Red', width=10, command=stop)
    stopb.pack(side=LEFT, padx=20, pady=1)
    contib = tk.Button(ftpw, text="Continue", state=DISABLED, font=('Ariel', 10), bg='Red', width=10, command=contin)
    contib.pack(side=LEFT, padx=20, pady=1)
    menu = tk.Button(ftpw, text="Menu", font=('Ariel', 10), bg='Red', width=10, command=ftphome)
    menu.pack(padx=10, pady=0)

    # tcp window finish
    tcpw = Frame(root, bg='Black')
    tcpl = tk.Label(tcpw, text="File Transfer", bg='Black', fg='Green', font=('David', 30))
    tcpl.pack(padx=10, pady=30)
    downt = tk.Button(tcpw, text="Download", font=('Ariel', 20), bg='Green', width=20, command=tcpdownw)
    downt.pack(padx=10, pady=10)
    tcpent = tk.Label(tcpw, text="Enter file name", bg='Black', fg='Green', font=('David', 20))
    tcpent.pack(padx=10, pady=10)
    filenametcp = tk.Text(tcpw, height=5, font=('Ariel', 10))
    filenametcp.pack(padx=10, pady=10)
    entertcp = tk.Button(tcpw, text="Enter", font=('Ariel', 10), bg='Green', width=10, command=entertcp)
    entertcp.pack(padx=10, pady=10)
    uplotcp = tk.Button(tcpw, text="Upload", state=DISABLED, font=('Ariel', 20), bg='Green', width=40, command=upload_t)
    uplotcp.pack(padx=10, pady=10)
    stopt = tk.Button(tcpw, text="Stop", state=DISABLED, font=('Ariel', 10), bg='Red', width=10, command=stoptcp)
    stopt.pack(side=LEFT, padx=20, pady=1)
    contit = tk.Button(tcpw, text="Continue", state=DISABLED, font=('Ariel', 10), bg='Red', width=10, command=upload_2h)
    contit.pack(side=LEFT, padx=20, pady=1)
    menut = tk.Button(tcpw, text="Menu", font=('Ariel', 10), bg='Red', width=10, command=tcp_home)
    menut.pack(padx=10, pady=0)
    # tcp window finish

    # download tcp window start
    downtcp = Frame(root, bg='Black')
    downltcp = tk.Label(downtcp, text="Download, choose file: ", bg='Black', fg='Green', font=('David', 30))
    downltcp.pack()
    scrollbar2 = Scrollbar(downtcp)
    scrollbar2.pack(side=RIGHT, fill=Y)
    mylist2 = Listbox(downtcp, width=60, bg='Black', fg='Green', yscrollcommand=scrollbar2.set)
    choo = tk.Button(downtcp, text="Enter", font=('Ariel', 20), bg='Green', width=30, command=downloadtcp)
    choo.place(x=50, y=150)
    choo.pack(padx=10, pady=10)
    # download tcp window finish

    # download fudp window start
    downw = Frame(root, bg='Black')
    downl = tk.Label(downw, text="Download, choose file: ", bg='Black', fg='Green', font=('David', 30))
    downl.pack()
    scrollbar = Scrollbar(downw)
    scrollbar.pack(side=RIGHT, fill=Y)
    mylist = Listbox(downw, width=60, bg='Black', fg='Green', yscrollcommand=scrollbar.set)
    cho = tk.Button(downw, text="Enter", font=('Ariel', 20), bg='Green', width=30, command=cfile)
    cho.place(x=50, y=150)
    cho.pack(padx=10, pady=10)
    # download fudp window finish

    # connection start
    con = Frame(root, bg='Black')
    lab = tk.Label(con, text="Try to connect...please wait", bg='Black', fg='Green', font=('David', 30))
    lab.pack(padx=10, pady=20)
    lab2 = tk.Label(con, text="Can't connect to server, Goodbye", bg='Black', fg='Green', font=('Ariel', 20))
    menu2 = tk.Button(con, text="Menu", font=('Ariel', 10), bg='Red', width=10, command=home)
    # connection finish

    # DNS window start
    dnsw = Frame(root, bg='Black')
    lab = tk.Label(dnsw, text="Enter domain please:", bg='Black', fg='Green', font=('David', 30))
    lab.pack(padx=10, pady=20)
    link = tk.Text(dnsw, width=50, height=1, font=('Ariel', 10))
    link.pack(padx=10, pady=20)
    domainc = tk.Button(dnsw, text="Domain calculation", font=('Ariel', 20), bg='Green', width=20, command=domain_to_ip)
    domainc.pack(padx=10, pady=20)
    showdo = tk.Label(dnsw, text="Ip address -> ", bg='Black', justify=LEFT, fg='Green', font=('Ariel', 20))
    showdo.pack(padx=10, pady=20)
    menu3 = tk.Button(dnsw, text="Menu", font=('Ariel', 10), bg='Red', width=5, command=home)
    menu3.pack(padx=10, pady=20)
    # DNS window end

    # DHCP window start
    dhcpw = Frame(root, bg='Black')
    gelab = tk.Label(dhcpw, text="DHCP - Get a ip", bg='Black', fg='Green', font=('David', 30))
    gelab.pack(padx=10, pady=20)
    getip = tk.Button(dhcpw, text="Get", font=('Ariel', 20), bg='Green', width=20, command=dhcp_client)
    getip.pack(padx=10, pady=20)
    showip = tk.Label(dhcpw, text="Ip address -> ", bg='Black', justify=LEFT, fg='Green', font=('Ariel', 20))
    showip.pack(padx=10, pady=20)
    menu4 = tk.Button(dhcpw, text="Menu", font=('Ariel', 10), bg='Red', width=5, command=home2)
    menu4.pack(padx=10, pady=20)
    # DHCP window end

    root.mainloop()
