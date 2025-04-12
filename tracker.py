import time
import socket
from threading import *


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tr_port = 9000
sock.bind(('127.0.0.1', tr_port))
p_len = 8
seeders = {}
file_pieces = {}
dl_peers = []
dling_peers = []
wait = 5


def generate_metainfo(name, file_len):
    pieces = []
    for i in range(0, file_len, p_len):
        pieces.append(i)
    file_pieces[name] = [str(item) for item in pieces]
    with open(f'{name}.torrent', 'w') as file:
        file.write(f'{{announce: (\'127.0.0.1\', {tr_port}), info: {{name: {name}, piece_length: {p_len}, pieces: {pieces}, length: {file_len}}}}}')


def discover_peer():
    while 1:
        pkt, sender = sock.recvfrom(100)
        port, name, received, = pkt.decode().split('|')
        port = int(port)
        received = received[1:-1].split(', ')
        seeders[port] = (name, received)
        # print(port, name, received)
        dl_peers.append((port, name, received))


def match_peers(dl_peer):
    dl_port, dl_name, dl_recv = dl_peer
    # file pieces that dl_peer needs
    needed = set(file_pieces[dl_name]) - set(dl_recv)
    if not needed:
        # dl_peer has the whole file
        print(f'{dl_port} already has entire {dl_name} file')
        dling_peers.remove(dl_peer)
        return
    for port, (name, received) in seeders.items():
        if (port, name, received) == dl_peer or name != dl_name:
            continue
        if set(received) & needed:
            print(f'matching {dl_port} with {port}')
            info = f'{port}|{name}|{received}'.encode()
            addr = ('127.0.0.1', dl_port)
            sock.sendto(info, addr)
            time.sleep(wait)
            break
    

def main():
    generate_metainfo('spiderman', 64)
    discover_thread = Thread(target=discover_peer, daemon=True)
    discover_thread.start()

    while 1:
        print(f'Peers Downloading: {dling_peers}')
        if dl_peers:
            current_peer = dl_peers.pop(0)
            if current_peer not in dling_peers:
                dling_peers.append(current_peer)
            match_thread = Thread(target=match_peers, args=(current_peer,), daemon=True)
            match_thread.start()
        time.sleep(wait)


if __name__ == '__main__':
    main()
