from scapy.all import *
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether


def dhcp_server():
    print("DHCP SERVER ON - waiting for discover")
    offer_ip = assign_ip()
    # Start sniffing DHCP Discover packets
    discover = sniff(count=1, filter='udp and (port 67 or port 68) and (udp[8:1] = 1)')
    time.sleep(2)

    got_discover(discover[0], offer_ip)
    print("waiting for request")
    request = sniff(count=1, filter='udp and (port 67 or port 68)')
    time.sleep(2)
    if request:
        got_request(request[0])
    else:
        print("no request")

    print("finished server side process")
    print()


def got_discover(packet, offer_ip):
    # Check if the packet is a DHCP Discover message
    if DHCP in packet and packet[DHCP].options[0][1] == 1:
        print("DISCOVER RECEIVED")
        mac_add = packet[Ether].src
        # ip_add = offer_ip.pop(0)
        # client_lst.append((mac_add, ip_add))
        ip_add = None
        print(offer_ip.pop(0))
        for client in client_lst:
            if client[0] == mac_add:
                ip_add = client[1]
                break
        if ip_add == None:
            while True:
                ip_add = offer_ip.pop(0)
                if ip_add not in [client[1] for client in client_lst]:
                    break
        client_lst.append((mac_add, ip_add))

        # Create the DHCP Offer packet
        offer = (Ether(dst=packet[Ether].src) /
                 IP(src="0.0.0.0", dst="255.255.255.255") /
                 UDP(sport=67, dport=68) /
                 BOOTP(op=2, yiaddr=ip_add, xid=packet[BOOTP].xid) /
                 DHCP(options=[('message-type', 'offer'), ('lease_time', 86400), 'end'])
                 )
        # Send the DHCP Offer packet
        print("SENT OFFER")
        sendp(offer)


def got_request(packet):
    # Check if the packet is a DHCP Request message
    if DHCP in packet and packet[DHCP].options[0][1] == 3:
        print("GOT REQUEST")
        mac_add = packet[Ether].src
        req_ip = packet[BOOTP].yiaddr

        # Create the DHCP ACK packet
        dhcp_ack = (Ether(dst="ff:ff:ff:ff:ff:ff") /
                    IP(src="192.168.1.1", dst="255.255.255.255") /
                    UDP(sport=67, dport=68) /
                    BOOTP(op=2, yiaddr=req_ip, xid=packet[0][3].xid,
                          chaddr=mac_add) /
                    DHCP(options=[('message-type', 'ack'), ('lease_time', 86400), 'end'])
                    )
        # Send the DHCP ACK packet
        print("SENT ACK")
        sendp(dhcp_ack)


client_lst = []


def assign_ip():
    ip_list = []
    for i in range(3, 20):
        ip_list.append("192.168.1." + str(i))
    return ip_list


if __name__ == '__main__':
    dhcp_server()