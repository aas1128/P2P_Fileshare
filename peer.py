import socket

host = "127.0.0.1"
received_file = {}
def main(port, fileName, metadata):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # set a timeout so it doesn't hang indefinitely
        sock.settimeout(1)
        # connect_ex returns 0 if the connection is successful
        result = sock.connect_ex((host, port))
        if result != 1:
            print("Port entered already in use. Please rerun with a different")
            return -1
    
def broadcast(port, received_file):
    pass

def receivePiece():
    #Need 1 thread thats sending anf 1 thread that is receiveing. 
    pass 

if __name__ == '__main__':
    # Ensure there are enough command line arguments
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <fileName> <metadata>")
        sys.exit(1)
    
    # sys.argv[0] is the script name, so the first argument is sys.argv[1]
    port = int(sys.argv[1])
    fileName = sys.argv[2]
    metadata = sys.argv[3]

