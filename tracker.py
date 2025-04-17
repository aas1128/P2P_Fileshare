"""
Module that tracks downloads, matching peers together
"""
import os
import sys
import time
import socket
from threading import *


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tr_port = 9000
sock.bind(('127.0.0.1', tr_port))
p_len = 8
seeders = {}
peer_timeout = 60
file_pieces = {}
dl_peers = []
dling_peers = []
wait = 2


def generate_metainfo(file_path):
    """
    Given a base file, generate a .torrent file containing the metainfo
    file_path: path of base file
    """
    # get relevant info from base file
    file = os.path.basename(file_path)
    file_name, file_ext = os.path.splitext(file)
    file_len = os.path.getsize(file_path)
    print(f'Generating {file_name}.torrent from {file}...')

    # compute info for metainfo file
    pieces = []
    for i in range(0, file_len, p_len):
        pieces.append(str(i))
    file_pieces[file] = pieces

    # write to metainfo .torrent file
    with open(f'{file_name}.torrent', 'w') as f:
        f.write(f'{{announce: (\'127.0.0.1\', {tr_port}), info: {{name: \'{file}\', piece_length: {p_len}, pieces: {pieces}, length: {file_len}}}}}')


def discover_peers():
    """
    Listen for peers broadcasting the files they have/want
    """
    while 1:
        # receive broadcasts from peers
        pkt, sender = sock.recvfrom(1024)
        # print(f'Received: {pkt} from {sender}')
        # clean up packet data
        port, name, received, = pkt.decode().split('|')
        port = int(port)
        received = received[1:-1].split(', ')
        # add to seeders and downloaders
        if received != file_pieces[name]:
            dl_peers.append((port, name, received, sender))
        # else peer has full file, don't need to append
        curr_time = time.time()
        # if port in seeders and seeders[port][0] == name:
        #     # if the peer is already seeding this file
        #     if (curr_time - seeders[port][2]) < peer_timeout:
        #         # if peer hasn't timed out, don't re add it
        #         # print(f'not re adding {port}')
        #         continue
        seeders[port] = (name, received, curr_time)


def cleanup_seeders():
    """
    Periodically remove seeders that haven't been heard from in a while
    """
    while 1:
        print(f'Cleaning seeders...')
        # every 30s, check for 'dead' peers
        for port, (name, received, rcv_time) in list(seeders.items()):
            curr_time = time.time()
            if (curr_time - rcv_time) > peer_timeout:
                # if a peer hasnt been heard from in <60>s, remove from seeders
                print(f'{port} is dead, removing...') 
                seeders.pop(port)
        time.sleep(30)


def match_peers(dl_peer):
    """
    Match a peer to another peer that has file parts it needs
    dl_peer: peer searching for parts of the file
    """
    dl_port, dl_name, dl_recv, dl_sender = dl_peer
    print(f'{dl_port} seaching for {dl_name}...')
    # file pieces that dl_peer needs
    needed = set(file_pieces[dl_name]) - set(dl_recv)
    if not needed:
        # dl_peer has the whole file
        print(f'{dl_port} already has entire {dl_name} file, removing...')
        dling_peers.remove(dl_peer)
        return
    for port, (name, received, rcv_time) in seeders.items():
        if (port, name, received) == (dl_port, dl_name, dl_recv) or name != dl_name:
            # if same peer
            continue
        if set(received) & needed:
            # if there is an intersection of what the peer has and what dl_peer needs
            print(f'Matching {dl_port} with {port}...')
            info = f'{port}|{name}|{received}'.encode()
            sock.sendto(info, dl_sender)
            time.sleep(wait)
            break
    

def main(file):
    """
    Main function that creates threads for discovery and cleanup, 
    and runs main loop where peers are matched
    """
    # generate metainfo file
    generate_metainfo(file)

    # start thread to discover new peers
    discover_thread = Thread(target=discover_peers, daemon=True)
    discover_thread.start()

    # start thread to remove 'dead' seeders from list
    cleanup_thread = Thread(target=cleanup_seeders, daemon=True)
    cleanup_thread.start()

    while 1:
        print(f'Seeders: {list(seeders.keys())}')
        print(f'Leechers: {dl_peers}')
        if dl_peers:
            # if there are peers that want to download something, get oldest in list
            current_peer = dl_peers.pop(0)
            if current_peer not in dling_peers:
                dling_peers.append(current_peer)
            print(f'Peers Downloading: {dling_peers}')
            # start thread to match the current peer to a peer that has what it needs
            match_thread = Thread(target=match_peers, args=(current_peer,), daemon=True)
            match_thread.start()
        print('-------------------------------')
        time.sleep(wait)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python tracker.py <file>')
        sys.exit(1)
    main(sys.argv[1])
