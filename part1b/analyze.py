import sys

import dpkt


## 'my-secret': 'Zubair Rocks!!'
def parse_pcap1(pcap_file):
    f = open(pcap_file, "rb")
    pcap = dpkt.pcap.Reader(f)

    for timestamp, data in pcap:
        eth = dpkt.ethernet.Ethernet(data)

        if not isinstance(eth.data, dpkt.ip.IP) and not isinstance(
            eth.data, dpkt.ip6.IP6
        ):
            continue

        ip = eth.data

        if not isinstance(ip.data, dpkt.tcp.TCP):
            continue

        tcp = ip.data

        if not len(tcp.data) > 0:
            continue

        if tcp.dport == 80:
            try:
                http = dpkt.http.Request(tcp.data)
                print(http.headers)
            except Exception as e:
                print(e, file=sys.stderr)

        elif tcp.sport == 80:
            try:
                http = dpkt.http.Response(tcp.data)
                print(http.headers)
            except Exception as e:
                print(e, file=sys.stderr)


def main():
    parse_pcap1("./PCAP1_1.pcap")


if __name__ == "__main__":
    main()
