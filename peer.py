import socket
import sys 
import re
import ast
import threading
import time 

host = "127.0.0.1"
received_file = ""
received_index = []
incoming_peers_to_connect = []
keep_downloading_file = True 
keep_seeding = True
def main(port, metainfo, file):
    print(port, metainfo, file)
    global received_file, received_index
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        #First check if the port can be bound
        try:
            sock.bind((host, port))            
        except socket.error as e:
            # If binding fails, it likely means the port is in use
            print(f"Error binding to port {port} on {host}: {e}")
            return False
        
        #Read in the torrent file
        torrent_file = parse_torrent_file(metainfo)
        #Need to get info from file to start broadcast & listen
        trackerInfo = torrent_file["announce"]
        filename =  torrent_file["info"]["name"]
        server_ip = trackerInfo[0]  
        server_port = trackerInfo[1]  
        p_len = int(torrent_file["info"]["piece_length"])
        pieces = torrent_file["info"]["pieces"]
        pieces = [int(x) for x in pieces]

        if file:
            # the peer has the file
            with open(file, 'r') as f:
                received_file = f.read()
                received_index = pieces
            print('Peer has file')

        # Create a thread that will run the connect_to_server function
        #Set the listening port to whatever the user specifies + 1
        startBroadcast(server_ip, server_port, port + 1, filename, sock)
        
        #Start the listen 
        startListeningForTracker(port, sock)

        startListeningForPeers(port + 1, p_len)
    
        #Start Connecting and Downloading to other peers
        connectToPeer(filename, pieces, port)
        try:
            while keep_seeding:
                time.sleep(3)
        except KeyboardInterrupt:
         print("Exiting program.")


def parse_torrent_file(metainfo):
    try: 
            with open(metainfo, 'r') as file:
            # Read the entire file
                file_content = file.read()
    except:
        print("Torrent File Does Not Exist")
        return False
    fixed_str = re.sub(r'(\b[a-zA-Z_][a-zA-Z0-9_]*\b)(\s*):', r'"\1"\2:', file_content)
    fixed_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])', r': "\1"\2', fixed_str)
    try:
        # ast.literal_eval safely evaluates the string to a dictionary
        result_dict = ast.literal_eval(fixed_str) 
        return result_dict
    except Exception as e:
        print("Error parsing Torrent File:", e)
        return None


def startListeningForTracker(port, sock):
    trackerListen_thread = threading.Thread(target=receiveFromTracker, args=(port, sock), daemon=True)
    # Start the thread
    trackerListen_thread.start()

def startListeningForPeers(port, p_len):
    peerListen_thread = threading.Thread(target=receiveFromPeers, args=(port, p_len), daemon=True)
    # Start the thread
    peerListen_thread.start()

def startBroadcast(server_ip, server_port, port , fileName, sock):
    broadcast_thread = threading.Thread(target=broadcast, args=(server_ip, server_port, port, fileName, sock), daemon=True)
        # Start the thread
    broadcast_thread.start()


def receiveFromPeers(listenPort, p_len):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        try:
            tcp_sock.bind((host, listenPort))
            tcp_sock.listen()
            print(f'Open on {listenPort}')
            conn, addr = tcp_sock.accept()  
            print(f'Connected to {addr}')
            with conn:
                while True:
                    received_data = conn.recv(1024)
                    if not received_data:
                        break
                    #start sending the packets they need to them
                    needed = received_data.decode()[1:-1].split(', ')
                    for piece in needed:
                        idx = int(piece)
                        file_chunk = received_file[idx:idx+p_len]
                        csum = checksum(file_chunk)
                        info = f'{idx}|{file_chunk}|{csum}'.encode()
                        print(f'Sending chunk {idx}: {file_chunk}')
                        conn.send(info)
                        time.sleep(2)
        except:
            pass 


def receiveFromTracker(listenPort, udp_sock):
    # udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # udp_sock.bind((host, listenPort))
        print(f"Listening for UDP packets on {host}:{listenPort}...")
        while keep_seeding:
            data, sender = udp_sock.recvfrom(1024)
            packet = data.decode()
            print(f"Received packet from {sender}: {packet}")
            incoming_peers_to_connect.append(packet)
            # Store the received packet in the list
    except Exception as e:
        print("Error in UDP listener:", e)
    finally:
        udp_sock.close()


def broadcast(server_ip, server_port, port, filename, sock):
    global keep_seeding
    #Broadbast packet looks like: Port of Peer thats broadcasting|File name(spiderman)|received_indexs 
    try:
        # Create a socket object using IPv4 and TCP
            # Connect to the specified server
            while keep_seeding:
                packet = f"{port}|{filename}|{received_index}"
                sock.sendto(packet.encode(), (server_ip, server_port) )
                print("Broadcasted:", packet)
                time.sleep(5)    
    except Exception as e:
        print(f"Error connecting to {server_ip}:{server_port} - {e}")


def connectToPeer(filename, pieces, peer_port):
    global received_file, keep_downloading_file
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
            connected = False
            while keep_downloading_file:
                if received_index == pieces:
                    # break if peer has received all pieces of the file
                    keep_downloading_file = False
                    break
                #Here we check if there are any packets sent to us by the tracker
                if incoming_peers_to_connect:
                    #Pop off the first one and see what we have to download
                    peer_info = incoming_peers_to_connect[0]
                    #Incoming peer info in in form:
                    port, name, received, = peer_info.split('|')
                    port = int(port)
                    received = received[1:-1].split(', ')
                    indexes_we_have =  set(received_index)
                    indexes_needed = []
                    #Build a list of all the indexes we need before we to the TCP connection
                    for val in received:
                        index_I_might_need = int(val.strip("'"))
                        if  index_I_might_need not in indexes_we_have :
                            indexes_needed.append(index_I_might_need)
                    # print(f'needed: {indexes_needed}')
                    if not connected:
                        client_sock.connect((host, port))
                        print(f'Connected to {port}')
                        connected = True
                    # send needed indexes to other peer
                    info = f'{indexes_needed}'.encode()
                    client_sock.sendall(info)
                    # receive a chunk of the file from peer and decode/validate it
                    file_chunk = client_sock.recv(1024)
                    index, fileChunk, prevchecksum = file_chunk.decode().split('|')
                    index = int(index)
                    newCheckSum = checksum(fileChunk)
                    if newCheckSum != int(prevchecksum):
                        print(f'Checksums not equal for chunk {index}')
                        continue
                    # if validated, update received
                    print(f'Received chunk {index}: {fileChunk}')
                    received_index.append(index)
                    received_index.sort()
                    received_file = received_file[:index] +  fileChunk + received_file[index:]
            
            # when all pieces have been received, write to file
            incoming_peers_to_connect.pop(0)
            writeToFile(filename, received_file, peer_port)
            return           
    except Exception as e:
        print(e) 


def writeToFile(filename, data_to_write, port):
    print('Writing file...')
    with open(f'{port}_{filename}', 'w') as f:
        f.write(data_to_write)


def checksum(data):
    """
    compiutes checksum
    data: data to compute checksum on
    returns: checksum of data
    """
    csum = 0x0
    for b in data.encode():
        csum += b

    csum = csum ^ 0xFFFF
    return csum


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python peer.py <port> <metainfo file> [file]")
        sys.exit(1)
    port = int(sys.argv[1])
    metainfo = sys.argv[2]
    file = None
    if len(sys.argv) == 4:
        file = sys.argv[3]
    main(port, metainfo, file)
