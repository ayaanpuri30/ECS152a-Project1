import os
import socket
import sys

import dpkt


def get_app_protocol(ip_data):
    # --- UDP ---
    if isinstance(ip_data, dpkt.udp.UDP):
        sport, dport = ip_data.sport, ip_data.dport
        if sport == 53 or dport == 53:
            return "DNS"
        elif sport == 5353 or dport == 5353:
            return "mDNS"
        elif sport == 5355 or dport == 5355:
            return "LLMNR"
        elif sport == 67 or dport == 68:
            return "DHCP"
        elif sport == 123:
            return "NTP"
        elif sport == 443 or dport == 443:
            return "QUIC"  # HTTP/3 over UDP
        else:
            return "UDP"

    # --- TCP ---
    elif isinstance(ip_data, dpkt.tcp.TCP):
        sport, dport = ip_data.sport, ip_data.dport
        payload = ip_data.data or b""

        # HTTP
        if sport == 80 or dport == 80:
            if payload.startswith((b"GET ", b"POST ", b"HEAD ", b"HTTP/")):
                return "HTTP"
            return "HTTP"

        # HTTPS (TLS)
        elif sport == 443 or dport == 443:
            return "HTTPS"

        # FTP
        elif sport == 21 or dport == 21:
            return "FTP"

        # SSH
        elif sport == 22 or dport == 22:
            if payload.startswith(b"SSH-"):
                return "SSH"
            return "SSH"

        # SMTP / POP / IMAP (optional extras)
        elif sport in (25, 465, 587) or dport in (25, 465, 587):
            return "SMTP"
        elif sport in (110,) or dport in (110,):
            return "POP3"
        elif sport in (143, 993) or dport in (143, 993):
            return "IMAP"

        else:
            return "TCP"

    # --- ICMP / ICMPv6 ---
    elif isinstance(ip_data, dpkt.icmp.ICMP):
        return "ICMP"
    elif isinstance(ip_data, dpkt.icmp6.ICMP6):
        return "ICMPv6"

    # --- Others ---
    else:
        return "Other"


def parse_pcap(pcap_file):
    f = open(pcap_file, "rb")
    pcap = dpkt.pcap.Reader(f)
    count_types = {}
    ips = set()
    browsers = set()

    for i, (timestamp, data) in enumerate(pcap):
        eth = dpkt.ethernet.Ethernet(data)

        if not isinstance(eth.data, dpkt.ip.IP) and not isinstance(
            eth.data, dpkt.ip6.IP6
        ):
            continue

        ip = eth.data

        count_types[get_app_protocol(ip.data)] = (
            count_types.get(get_app_protocol(ip.data), 0) + 1
        )

        if not isinstance(ip.data, dpkt.tcp.TCP):
            continue

        tcp = ip.data

        if isinstance(ip, dpkt.ip.IP):
            dst_ip = socket.inet_ntoa(ip.dst)
        elif isinstance(ip, dpkt.ip6.IP6):
            # dst_ip = socket.inet_ntop(socket.AF_INET6, ip.dst)
            continue
        else:
            continue

        ips.add(dst_ip)

        if not len(tcp.data) > 0:
            continue

        if tcp.dport == 80:
            try:
                pass
                http = dpkt.http.Request(tcp.data)
                browsers.add(http.headers.get("user-agent"))
            except Exception as e:
                print(e, file=sys.stderr)

        elif tcp.sport == 80:
            try:
                pass
                http = dpkt.http.Response(tcp.data)
                browsers.add(http.headers.get("user-agent"))
            except Exception as e:
                print(e, file=sys.stderr)

    return count_types, ips, browsers


def main(arg):
    files = sorted([file for file in os.listdir() if file.endswith(".pcap")])
    for file in files:
        count_types, dst_ip, browsers = parse_pcap(file)

        if arg == "count":
            print(file, count_types)
        elif arg == "ip":
            print(file, dst_ip)
        elif arg == "browsers":
            print(file, browsers)
        else:
            print(file, count_types, "\n", dst_ip, "\n", browsers)


if __name__ == "__main__":
    main("" if len(sys.argv) == 1 else sys.argv[1])
