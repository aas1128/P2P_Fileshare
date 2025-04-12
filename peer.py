import socket
import sys 
import re
import ast
import threading
import time 

host = "127.0.0.1"
received_file = {}
received_index = []
def main(port, fileName, metainfo):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        #First check if the port can be bound
        try:
            sock.bind((host, port))
        except socket.error as e:
            # If binding fails, it likely means the port is in use
            print(f"Error binding to port {port} on {host}: {e}")
            return False
        #Read in the torrent file
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
        except Exception as e:
            print("Error parsing dictionary:", e)
            return None
        trackerInfo = result_dict["announce"]
        info = result_dict["info"]
        filename = info["name"]
        #Need to connect to the tracker to start broadcasting.
        server_ip = trackerInfo[0]  
        server_port = trackerInfo[1]     
    # Create a thread that will run the connect_to_server function
    #Set the listening port to whatever the user specifies + 1
        startBroadcast(server_ip, server_port, port + 1 , fileName, received_index, sock)
        
        print("here")
        startListening(port + 1)
        
        #Once I Bind to port get the Tracker URL from the metaInfo
        #The broadcast should be on a timer which I repetedly => 10 seconds, and on every receive
        #I need a thread that is open and listening for file parts
        #Once I read in a file I validate it, update my recieved_file to 
        #Update the dictionary: the key is the index , the value is the actual fiel 
        try:
            while True:
                time.sleep(3)
        except KeyboardInterrupt:
         print("Exiting program.")

def startListening(port):
    trackerListen_thread = threading.Thread(target=receiveFromTracker, args=(port,), daemon=True)
        # Start the thread
    trackerListen_thread.start()
    pass

def startBroadcast(server_ip, server_port, port , fileName, received_index, sock):
    broadcast_thread = threading.Thread(target=broadcast, args=(server_ip, server_port, port, fileName, received_index, sock), daemon=True)
        # Start the thread
    broadcast_thread.start()


def broadcast(server_ip, server_port, port, filename, received_index, sock):
    global current_peer_port
    #Broadbast packet looks like: Port of Peer thats broadcasting|File name(spiderman)|received_indexs 
    try:
        # Create a socket object using IPv4 and TCP
            # Connect to the specified server
            while True:
                packet = f"{port}|{filename}|{received_index}"
                sock.sendto(packet.encode(), (server_ip, server_port) )
                print("Broadcasted:", packet)
                time.sleep(5)    
    except Exception as e:
        print(f"Error connecting to {server_ip}:{server_port} - {e}")

def receiveFromTracker(listenPort):
    print("here")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_sock.bind((host, listenPort))
        print(f"Listening for UDP packets on {host}:{listenPort}...")
        while True:

            data, sender = udp_sock.recvfrom(1024)
            packet = data.decode()
            print(f"Received packet from {sender}: {packet}")
            # Store the received packet in the list
    except Exception as e:
        print("Error in UDP listener:", e)
    finally:
        udp_sock.close()
    #getting a packet from the tracker that has info about the thread I need to connect.
    pass 

def connectToPeer():
    #Start data tranfer
    pass 

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <fileName> <metadata>")
        sys.exit(1)
    port = int(sys.argv[1])
    fileName = sys.argv[2]
    metadata = sys.argv[3]

main(port, fileName, metadata)