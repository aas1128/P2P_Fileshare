import socket
import sys 
import re
import ast
import threading
import time 

host = "127.0.0.1"
received_file = "spidermaspidermaspidermaspidermaspidermaspidermaspidermaspiderma"
received_index = [0, 8, 16, 24, 32, 40, 48, 56]
incoming_peers_to_connect = []
keep_downloading_file = True 
def main(port, fileName, metainfo):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        #First check if the port can be bound
        try:
            sock.bind((host, port))
            keep_downloading_file = True
            
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
        # Create a thread that will run the connect_to_server function
        #Set the listening port to whatever the user specifies + 1
        startBroadcast(server_ip, server_port, port + 1 , filename, received_index, sock)
        
        #Start the listen 
        startListeningForTracker(port, sock)

        startListeningForPeers(port + 1, p_len)
    
        #Start Connecting and Downloading to other peers
        connectToPeer()
        try:
            while keep_downloading_file:
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

def startBroadcast(server_ip, server_port, port , fileName, received_index, sock):
    broadcast_thread = threading.Thread(target=broadcast, args=(server_ip, server_port, port, fileName, received_index, sock), daemon=True)
        # Start the thread
    broadcast_thread.start()

def receiveFromPeers(listenPort, p_len):
    print('tcp server')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        try:
            tcp_sock.bind((host, listenPort))
            tcp_sock.listen()
            print(f'open on {listenPort}')
            conn, addr = tcp_sock.accept()  
            print(f'connected to {addr}')
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
                        print(info)
                        conn.send(info)

        except:
            pass 

def receiveFromTracker(listenPort, udp_sock):
    # udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # udp_sock.bind((host, listenPort))
        print(listenPort)
        print(f"Listening for UDP packets on {host}:{listenPort}...")
        while keep_downloading_file:
            data, sender = udp_sock.recvfrom(1024)
            packet = data.decode()
            print(f"Received packet from {sender}: {packet}")
            incoming_peers_to_connect.append(packet)
            # Store the received packet in the list
    except Exception as e:
        print("Error in UDP listener:", e)
    finally:
        udp_sock.close()

def broadcast(server_ip, server_port, port, filename, received_index, sock):
    global current_peer_port
    #Broadbast packet looks like: Port of Peer thats broadcasting|File name(spiderman)|received_indexs 
    try:
        # Create a socket object using IPv4 and TCP
            # Connect to the specified server
            while keep_downloading_file:
                packet = f"{port}|{filename}|{received_index}"
                sock.sendto(packet.encode(), (server_ip, server_port) )
                print("Broadcasted:", packet)
                time.sleep(5)    
    except Exception as e:
        print(f"Error connecting to {server_ip}:{server_port} - {e}")

def connectToPeer():
    print('tcp client')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        try:
            while keep_downloading_file:
                #Here we check if there are any packets sent to us by the tracker
                if incoming_peers_to_connect:
                    print(incoming_peers_to_connect)
                    #Pop off the first one and see what we have to download
                    peer_info = incoming_peers_to_connect.pop(0)
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
                    print(f'connecting to {port}')
                    client_sock.connect((host, port))
                    client_sock.sendall(indexes_needed.encode())
                    data = client_sock.recv(1024)
                    print(data)
        except:
            pass 

def checksum(data):
    """
    compiutes checksum
    data: data to compute checksum on
    retunrs: checksum of data
    """
    csum = 0x0
    for b in data.encode():
        csum += b
    
    csum = csum ^ 0xFFFF
    return csum


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <fileName> <metadata>")
        sys.exit(1)
    port = int(sys.argv[1])
    fileName = sys.argv[2]
    metadata = sys.argv[3]

main(port, fileName, metadata)