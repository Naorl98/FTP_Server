import socket
import time
import os
import tkinter as tk
from tkinter import *

ip = "127.0.0.1"
port = 30190
time_out = 5
packet_maxsize = 1024
# ex = 0
send = "".encode()
global sock, amount, index


def home():
    con.pack_forget()
    ftpw.pack_forget()
    first.pack(fill='both', expand=1)

# ftp client start


def connect():
    con.pack(fill='both', expand=1)
    maxtry = 5
    num_wait = 0
    num_try = 0
    while num_wait < maxtry and num_try < maxtry:
        try:
            sock.sendto("NEW".encode(), (ip, port))
            time.sleep(0.02)
        except ConnectionResetError:
            lab.config(text="Server not open")
            lab.pack(padx=10, pady=20)
            num_try = 5
        try:
            rec, add = sock.recvfrom(packet_maxsize)
            if rec.decode() == "ACK":
                con.pack_forget()
                return True
            elif rec.decode() == "WAIT":
                print("WAIT from server " + str(num_wait))
                lab.pack_forget()
                num_wait += 1
                lab.config(text="Wait to server to contact.." + str(num_wait) + " time")
                lab.pack(padx=10, pady=20)
                num_wait += 1
                time.sleep(2)
        except Exception as e:
            num_try += 1
            lab.config(text="Try again.." + str(num_try) + " time")
            time.sleep(0.2)
    if num_wait == 5 or num_try == 5:
        lab2.pack(padx=10, pady=20)
        menu2.pack(padx=10, pady=0)


def ftp_client():
    first.pack_forget()
    if connect():
        print("Connect to server")
        ftpw.pack(fill='both', expand=1)


def enter():
    if filename.get('1.0', tk.END) != 0:
        uplo.configure(state=NORMAL)


def upload_finish(buff):
    global send
    tries = 3
    timescount = 0
    while send.decode() != "ACK-ALL":
        try:
            send, add = sock.recvfrom(packet_maxsize)
            if send[:4].decode() == "ERR2":
                sock.sendto(buff[int(send[4:])].encode(), (ip, port))
            elif send[:4].decode() == "ERR3":
                sock.sendto("ACK_R".encode(), (ip, port))
        except Exception as e:
            print(f"ERROR: {e}")
            timescount += 1
            if timescount < tries:
                sock.sendto("ACK_R".encode(), (ip, port))
            else:
                print("Client Error")
                return False
    return True


# def task():
#     global amount, index, ex, packet_maxsize, send
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
    print("in download")
    ftpw.pack_forget()
    downw.pack(fill='both', expand=1)
    print("build")
    line = ""
    sock.sendto("DO".encode(), (ip, port))
    print("send DO")
    names, add = sock.recvfrom(packet_maxsize)

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
    f = open(fname, 'w')
    print("open file")
    sock.sendto("ACK".encode(), (ip, port))
    sock.settimeout(time_out)
    while True:
        if seq_packet == pcount:
            print("go to finish upload")
            finish(f, changed, index_packet, buffer)
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
    f.close()
    mylist.delete(0, END)
    downw.pack_forget()
    ftp_client()


def upload():
    # global amount, index, ex
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
    sock.sendto("UP".encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
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
        index = 0
        sock.settimeout(time_out)
        # thread = Thread(target=task)
        # run the thread
        # thread.start()
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
            index += 1
            time.sleep(0.01)

            if index == amount:
                seq = "L" + str(index)
                sock.sendto(seq.encode(), (ip, port))
            else:
                seq = "P" + str(index)
                sock.sendto(seq.encode(), (ip, port))
# ftp client start


# dns client start

BUFF = 512  # Buffer size
ip_port = ("127.0.0.1", 53)


def check_domain(domain):
    # Split the domain to parts
    domain_parts = domain.split('.')
    # if it has less than 2 parts its not good : google.com has 2
    if len(domain_parts) < 2:
        return False
    return True


def domain_to_ip():
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
        link.delete("1.0", "end")
        link.insert(INSERT, "Error with this domain name, try again")
        link.pack(padx=10, pady=20)
        print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
        return
    except Exception as e:
        link.delete("1.0", "end")
        link.insert(INSERT, "Error with this domain name, try again")
        link.pack(padx=10, pady=20)
        print("ERROR WITH THIS DOMAIN NAME, TRY AGAIN")
        return


def dns_client():
    first.pack_forget()
    dnsw.pack(fill='both', expand=1)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    dns = tk.Button(first, text="DNS", font=('Ariel', 20), bg='Green', width=40, command=dns_client)
    dns.pack(padx=10, pady=30)
    dhcp = tk.Button(first, text="DHCP", font=('Ariel', 20), bg='Green', width=40, command=ftp_client)
    dhcp.pack(padx=10, pady=30)
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
    menu = tk.Button(ftpw, text="Menu", font=('Ariel', 10), bg='Red', width=5, command=home)
    menu.pack(padx=10, pady=0)
    # ftp window finish

    # download window start
    downw = Frame(root, bg='Black')
    downl = tk.Label(downw, text="Download, choose file: ", bg='Black', fg='Green', font=('David', 30))
    downl.pack()
    scrollbar = Scrollbar(downw)
    scrollbar.pack(side=RIGHT, fill=Y)
    mylist = Listbox(downw, width=60, bg='Black', fg='Green', yscrollcommand=scrollbar.set)
    cho = tk.Button(downw, text="Enter", font=('Ariel', 20), bg='Green', width=30, command=cfile)
    cho.place(x=50, y=150)
    cho.pack(padx=10, pady=10)
    # download window finish

    # connection start
    con = Frame(root, bg='Black')
    lab = tk.Label(con, text="Try to connect...please wait", bg='Black', fg='Green', font=('David', 30))
    lab.pack(padx=10, pady=20)
    lab2 = tk.Label(con, text="Can't connect to server, Goodbye", bg='Black', fg='Green', font=('Ariel', 20))
    menu2 = tk.Button(con, text="Menu", font=('Ariel', 10), bg='Red', width=5, command=home)
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

    root.mainloop()
