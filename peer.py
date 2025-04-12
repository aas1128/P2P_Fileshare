import socket
import sys 
import re
import ast

host = "127.0.0.1"
received_file = {}
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
    
    # Step 2: Add quotes around unquoted string values.
    # This regex looks for values following a colon that start with a letter (i.e., not a number or an already quoted value)
    # and then adds quotes around them.
        fixed_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])', r': "\1"\2', fixed_str)
        
        # For debugging, you can print the fixed string:
        # print("Fixed string:", fixed_str)
        
        try:
            # ast.literal_eval safely evaluates the string to a Python literal (dictionary, list, etc.)
            result_dict = ast.literal_eval(fixed_str)
            print(result_dict)
        except Exception as e:
            print("Error parsing dictionary:", e)
            return None
        print("here")
        print(result_dict["announce"])
        #Once I Bind to port get the Tracker URL from the metaInfo
        #The broadcast should be on a timer which I repetedly => 10 seconds, and on every receive
        #I need a thread that is open and listening for file parts
        #Once I read in a file I validate it, update my recieved_file to 
        #Update the dictionary: the key is the index , the value is the actual fiel 
        
        

    
def broadcast(port, received_file):
    pass

def receivePiece():
    #Need 1 thread thats sending anf 1 thread that is receiveing. 
    pass 

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python peer.py <port> <fileName> <metadata>")
        sys.exit(1)
    port = int(sys.argv[1])
    fileName = sys.argv[2]
    metadata = sys.argv[3]

main(port, fileName, metadata)