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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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

        print(file_content)
        fixed_str = re.sub(r'(\b[a-zA-Z_][a-zA-Z0-9_]*\b)(\s*):', r'"\1"\2:', file_content)
        fixed_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])', r': "\1"\2', fixed_str)
        try:
            # ast.literal_eval safely evaluates the string to a dictionary
            result_dict = ast.literal_eval(fixed_str)
            print(result_dict)
        except Exception as e:
            print("Error parsing dictionary:", e)
            return None
        print("here")
        print(result_dict["announce"])
        trackerInfo = result_dict["announce"]
        info = result_dict["info"]
        filename = info["name"]
        #Need to connect to the tracker to start broadcasting.
        server_ip = trackerInfo[0]  
        server_port = trackerInfo[1]     
    # Create a thread that will run the connect_to_server function
        connection_thread = threading.Thread(target=broadcast, args=(server_ip, server_port, port , fileName, received_index), daemon=True)
        # Start the thread
        connection_thread.start()
        # Optionally, wait for the thread to finish
        connection_thread.join()

        #Once I Bind to port get the Tracker URL from the metaInfo
        #The broadcast should be on a timer which I repetedly => 10 seconds, and on every receive
        #I need a thread that is open and listening for file parts
        #Once I read in a file I validate it, update my recieved_file to 
        #Update the dictionary: the key is the index , the value is the actual fiel 
        
        

    
def broadcast(server_ip, server_port, port, filename, received_index):
    global current_peer_port
    #Broadbast packet looks like: Port of Peer thats broadcasting|File name(spiderman)|received_indexs 
    try:
        # Create a socket object using IPv4 and TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the specified server
            sock.connect((server_ip, server_port))
            while True:
                packet = f"{port}|{filename}|{received_index}"
                sock.sendall(packet.encode())
                print("Broadcasted:", packet)
                time.sleep(5)    
    except Exception as e:
        print(f"Error connecting to {server_ip}:{server_port} - {e}")
    


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <fileName> <metadata>")
        sys.exit(1)
    port = int(sys.argv[1])
    fileName = sys.argv[2]
    metadata = sys.argv[3]

main(port, fileName, metadata)