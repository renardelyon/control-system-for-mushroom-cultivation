import socket
import tqdm
import os

PORT = 5050
SERVER = '192.168.43.148'
HEADER = 64
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

filename = "./data/data.csv"
# get the file size
filesize = os.path.getsize(filename)

ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print("[NEW CONNECTION] {} is connected.".format(addr))
    msg_length = conn.recv(HEADER).decode("utf-8")
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode("utf-8")

        print("[{}] {}".format(addr, msg))

        conn.send("{}{}{}".format(filename, SEPARATOR, filesize).encode())

        progress = tqdm.tqdm(range(filesize), "Sending {}".format(filename), 
                        unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                conn.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
    conn.close()


def server_start():
    server.listen()
    print("[LISTENING] Server listening as {}:{}".format(SERVER, PORT))
    try:
        while True:
            conn, address = server.accept()
            handle_client(conn, address)
    except (KeyboardInterrupt, SystemExit):
        server.close()

if __name__ == '__main__':
    server_start()
        
