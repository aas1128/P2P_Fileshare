import time
import socket
from threading import *


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tr_port = 9000
sock.bind(('127.0.0.1', tr_port))
p_len = 8
seeders = {}
current_dl_peer = None


def generate_metainfo(name, file_len):
    pieces = []
    for i in range(0, file_len, 8):
        pieces.append(i)
    with open(f'{name}.torrent', 'w') as file:
        file.write(f'{{announce: (\'127.0.0.1\', {tr_port}), info: {{name: {name}, piece_length: {p_len}, pieces: {pieces}, length: {file_len}}}}}')


def discover_peer():
    while 1:
        pkt, _ = sock.recvfrom()
        port, received, = pkt.decode().split('/')
        seeders[port] = received
        current_dl_peer = (port, received)


def match_peers(downloading_peer):
    for port, received in seeders.items():
        if port != downloading_peer:
            info = f'{port}/{received}'
            addr = ('127.0.0.1', downloading_peer)
            sock.sendto(info, addr)


def main():
    generate_metainfo('spiderman', 64)
    discover_thread = Thread(target=discover_peer, daemon=True)
    discover_thread.start()

    while 1:
        if current_dl_peer:
            match_peers(current_dl_peer)


if __name__ == '__main__':
    main()
