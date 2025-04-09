import time
import socket
from threading import *


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tr_port = 9000
s.bind(('127.0.0.1', tr_port))
p_len = 8
seeders = {}
files = {}


def generate_metainfo(name, file_len):
    pieces = []
    for i in range(0, file_len, 8):
        pieces.append(i)
    with open(f'{name}.torrent', 'w') as file:
        file.write(f'{{url: {{name: {name}, piece_length: {p_len}, pieces: {pieces}, length: {file_len}}}}}')

def discover_peer():
    while 1:
        pkt, _ = s.recvfrom()
        port, received, = pkt.decode()


def main():
    generate_metainfo('spiderman', 64)
    discover_thread = Thread(target=discover_peer, daemon=True)
    discover_thread.start()


if __name__ == '__main__':
    main()
