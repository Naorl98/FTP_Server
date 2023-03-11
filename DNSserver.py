import socket

BUFF = 512  # Buffer size


def recv_ip(domain):
    """
    Receives domain name and returns its IP
    if the domain name is invalid or didn't find IP returns None.
    :param domain: string of domain name
    :return: IP address according to the domain or None if invalid
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip  # If the domain is good and has IP
    except socket.gaierror:  # Get address info error
        return None


def dns_server(ip, port):
    """
    Receives requests for domain names and replies with its IP address
    :param ip: DNS Server IP
    :param port: DNS Server port
    :return: the IP of the specified domain name, if there is an error it returns the error
    """
    domain_ip = []      # stores the domain with its ip in a list of tuples
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # udp socket
    sock.bind((ip, port))      # binds with the server and port
    print(f"DNS SERVER STARTED {ip}, {port}")

    while True:
        data, addr = sock.recvfrom(BUFF)
        domain = data.decode()
        print(f"RECEIVED REQUEST FOR: {domain}")
        ip_add = None
        for index in domain_ip:     # checks if the ip is already been searched
            if index[0] == domain:  # list of tuples - index 0 stores domain, index 1 stores ip
                ip_add = index[1]
                break

        if ip_add is None:      # if the domain hasn't been searched before
            ip_add = recv_ip(domain)
            if ip_add is None:
                print(f"THERE IS NO IP FOR THAT DOMAIN!! {domain}")
                continue
            print("SENDING IP ADDRESS")
            sock.sendto(ip_add.encode(), addr)
            domain_ip.append((domain, ip_add))      # adds the domain,ip as tuple to the list since its been searched
        else:
            print("SENDING IP ADDRESS FROM CACHE")      # domain's ip has been searched before and stored in the list
            sock.sendto(ip_add.encode(), addr)


if __name__ == "__main__":
    dns_server("127.0.0.1", 53)