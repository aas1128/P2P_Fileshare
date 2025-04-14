Aayan Sayed, Finn Saunders-Zurn
CSCI 351

Project: P2P Fileshare
Description: 
The goal of the project was to design a simple P2P filehshare system. It would allow multiple users or peers to to share 
files without relying on a centralized server. Our implementation has peer discovery via broadcasts, Searching of another peer's Indexes/File Chucks, 
concurrency with multithreading, data transfer via TCP, and file integrity checking via checksums.


1) How to compile and run the code:
    1) Clone the github repository to access the python code and the dependencies (can make a virtual environment using python)
    2) Check if python is downloaded on the system
    3) install the requirements needed to run the code 

2) For our bitTorrent we need there to be at least 1 peer that acts as a seeder for other peers. We tested with a "test_peer" which had the 
   entire file already in its directory and was being tracked. Then the tracker would pair peers together that had file parts to swap, starting with the seeder.

3) The Test_peer, and any other peers who partake can be run in any order alongside the tracker. The tracker works to let the peers know which where/what other peers are in the network. 

4) On run the Peers start a new thread that broadcasts their port number and the parts of the file they currently have. The peer than starts another thread that begins to listen
   for packets form the tracker informing it of peers it needs to connect to. The Peer than starts yet another thread where It begins to intiate TCP connection and file transfer with other peers.

Peer:  python3 peer.py <Port To Connect To> <Name of File> <.torrent File Corresponsing to the download>
        Ex: python3 peer.py 10000 spiderman spiderman.torrent

Seeder: python3 test_peer.py <Port To Connect To> <Name of File> <.torrent File Corresponsing to the download>
        Ex. python3 test_peer.py 10000 spiderman spiderman.torrent

Tracker: python3 tracker.py 
 

