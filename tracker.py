import time
import socket
from threading import *


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tr_port = 9000
sock.bind(('127.0.0.1', tr_port))
p_len = 8
seeders = {}
file_pieces = {}
current_dl_peer = ()
wait = 5


def generate_metainfo(name, file_len):
    pieces = []
    for i in range(0, file_len, 8):
        pieces.append(i)
    file_pieces[name] = pieces
    with open(f'{name}.torrent', 'w') as file:
        file.write(f'{{announce: (\'127.0.0.1\', {tr_port}), info: {{name: {name}, piece_length: {p_len}, pieces: {pieces}, length: {file_len}}}}}')


def discover_peer():
    global current_dl_peer
    while 1:
        pkt, _ = sock.recvfrom(100)
        print(pkt)
        port, name, received, = pkt.decode().split('|')
        received = received.split(',')
        seeders[port] = (name, received)
        current_dl_peer = (port, name, received)


def match_peers(dl_peer):
    dl_port, dl_name, dl_recv = dl_peer
    needed = set(file_pieces[dl_name]) - set(dl_recv)
    for port, (name, received) in seeders.items():
        received = received.split(',')
        if (port, name, received) == dl_peer or name != dl_name:
            continue
        if set(received) & needed:
            info = f'{port}|{name}|{received}'
            addr = ('127.0.0.1', dl_port)
            sock.sendto(info, addr)
            return 1
    return 0


def main():
    generate_metainfo('spiderman', 64)
    discover_thread = Thread(target=discover_peer, daemon=True)
    discover_thread.start()

    while 1:
        if current_dl_peer:
            match_peers(current_dl_peer)
        # time.sleep(wait)


if __name__ == '__main__':
    main()
