import socket
import time
import os
import tkinter as tk
from base64 import encode
from tkinter import *
import sys

ip = "127.0.0.1"
port = 30190
time_out = 5
packet_maxsize = 1024
global socket


def home():
    ftpw.pack_forget()
    first.pack()


def connect():
    con = Frame(root, bg='Black')
    con.pack(fill='both', expand=1)
    lab = tk.Label(con, text="Try to connect...please wait", bg='Black', fg='Green', font=('David', 30))
    lab.pack(padx=10, pady=20)
    maxtry = 5
    trying = 0
    while trying < maxtry:
        try:
            sock.sendto("NEW".encode(), (ip, port))
            time.sleep(0.02)
        except ConnectionResetError:
            lab = tk.Label(con, text="Server not open", bg='Black', fg='Green', font=('Ariel', 20))
            lab.pack(padx=10, pady=20)
            trying = 5
        try:
            rec, add = sock.recvfrom(packet_maxsize)
            if rec.decode() == "ACK":
                con.pack_forget()
                return True
            elif rec.decode() == "NACK":
                print("NACK from server " + str(trying))
                lab.pack_forget()
                lab = tk.Label(con, text="Try again", bg='Black', fg='Green', font=('Ariel', 20))
                lab.pack(padx=10, pady=20)
                trying += 1
                time.sleep(0.02)
        except ConnectionError:
            lab = tk.Label(con, text="Try again", bg='Black', fg='Green', font=('Ariel', 20))
            lab.pack(padx=10, pady=20)
    if trying == 5:
        lab = tk.Label(con, text="Can not connect to server, Goodbye", bg='Black', fg='Green', font=('Ariel', 20))
        lab.pack(padx=10, pady=20)


def ftp_client():
    first.pack_forget()
    if connect():
        print("Connect to server")
        ftpw.pack(fill='both', expand=1)


def enter():
    if filename.get('1.0', tk.END) != 0:
        down.configure(state=NORMAL)
        uplo.configure(state=NORMAL)


def upload_finish(buff):
    data = "a".encode()
    tries = 3
    timescount = 0
    while data.decode() != "ACK-ALL":
        try:
            data, add = sock.recvfrom(packet_maxsize)
            if data[:4].decode() == "ERR2":
                sock.sendto(buff[int(data[4:])].encode(), (ip, port))
            elif data[:4].decode() == "ERR1":
                sock.sendto("ACK_R".encode(), (ip, port))
        except ValueError:
            timescount += 1
            if timescount < tries:
                sock.sendto("ACK_R", (ip, port))
            else:
                print("Client Error")
                return False
    return True


def upload():
    print("in upload")
    file_name = (filename.get('1.0', tk.END))[:-1] + ".txt"
    err = 0
    buffer_send = []
    index_send = []
    try:
        f = open(file_name, 'r')
    except FileNotFoundError:
        print("File not found")
    print("open file")
    sock.sendto("UP".encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
    print("server send- " + rec.decode())
    sock.sendto(("F" + file_name).encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
    if rec.decode() == "ERR1":
        filename.delete("1.0", "end")
        filename.insert(INSERT, "File exist, Enter different name")
        filename.pack()
        down.configure(state=DISABLED)
        uplo.configure(state=DISABLED)
        return
    else:
        err = 1
        print("Send file")
    file_stats = os.stat(file_name)
    amount = int(file_stats.st_size / packet_maxsize) + 1
    print("file size = " + str(amount))
    sock.sendto(("S" + str(amount)).encode(), (ip, port))
    rec, add = sock.recvfrom(packet_maxsize)
    if rec.decode() == "ACK":
        i = 0
        sock.settimeout(time_out)
        while True:
            if i == amount:
                end = upload_finish(buffer_send)
                if end:
                    print("File sent")
                    filename.delete("1.0", "end")
                    down.configure(state=DISABLED)
                    uplo.configure(state=DISABLED)
                break
            data = f.read(packet_maxsize)
            sock.sendto(data.encode(), (ip, port))
            buffer_send.append(data)
            index_send.append(i)
            i += 1
            time.sleep(0.01)

            if i == amount:
                seq = "L" + str(i)
                sock.sendto(seq.encode(), (ip, port))
            else:
                seq = "P" + str(i)
                sock.sendto(seq.encode(), (ip, port))


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    root = Tk()
    root.geometry("500x500")
    root.title("Final Proj")
    first = Frame(root)
    first.pack()
    label = tk.Label(first, text="Choose option", font=('Ariel', 20))
    label.pack(padx=10, pady=10)
    ftp = tk.Button(first, text="FTP", font=('Ariel', 20), command=ftp_client)
    ftp.pack(padx=10, pady=30)
    ftpw = Frame(root, bg='Black')
    ftpl = tk.Label(ftpw, text="File Transfer-Enter File name", bg='Black', fg='Green', font=('David', 30))
    ftpl.pack(padx=10, pady=30)
    filename = tk.Text(ftpw, height=5, font=('Ariel', 10))
    filename.pack(padx=10, pady=10)
    enter = tk.Button(ftpw, text="Enter", font=('Ariel', 20), bg='Green', width=10, command=enter)
    enter.pack(padx=10, pady=10)
    down = tk.Button(ftpw, text="Download", state=DISABLED, font=('Ariel', 20), bg='Green', width=40)
    down.pack(padx=10, pady=20)
    uplo = tk.Button(ftpw, text="Upload", state=DISABLED, font=('Ariel', 20), bg='Green', width=40, command=upload)
    uplo.pack(padx=10, pady=10)
    menu = tk.Button(ftpw, text="Menu", font=('Ariel', 10), bg='Red', width=5, command=home)
    menu.pack(padx=10, pady=10)
    root.mainloop()
