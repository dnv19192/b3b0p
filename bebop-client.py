import socket
import sys
import time

ip = ""
port = 0

def main():
    if len(sys.argv) < 2:
        sys.exit("No Address specified")
    else:
        address = sys.argv[1].split(":")
        if len(address) < 2:
            sys.exit("Incorrect IP:PORT address.")

        ip, port = address[0], int(address[1])

    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip,port))
            client.close()
        except ConnectionRefusedError:
            print("Connecting...")
            time.sleep(5)
            continue
        else:
            break

main()
