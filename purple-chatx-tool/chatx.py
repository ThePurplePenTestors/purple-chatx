from cmd import Cmd
import socket
import threading
import random
import string

MAPPING_SERVER = "YOUR_MAPPING_SERVER_IP"  # <- Set this to your code mapping server
PORT = 9999

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def register_code(code, ip):
    s = socket.socket()
    try:
        s.connect((MAPPING_SERVER, 5050))
        s.send(f"REGISTER|{code}|{ip}".encode())
        return s.recv(1024).decode()
    except Exception as e:
        return f"Error: {e}"
    finally:
        s.close()

def get_ip_from_code(code):
    s = socket.socket()
    try:
        s.connect((MAPPING_SERVER, 5050))
        s.send(f"GET|{code}".encode())
        return s.recv(1024).decode()
    except Exception as e:
        return f"Error: {e}"
    finally:
        s.close()

def chat_send(sock):
    while True:
        try:
            msg = input("You: ")
            sock.send(msg.encode())
            if msg.lower() == "exit":
                break
        except:
            break

def chat_recv(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg.lower() == "exit":
                print("\n[Partner exited chat]")
                break
            print(f"\nPartner: {msg}\nYou: ", end="")
        except:
            break

def host_chat():
    code = input("Enter code (leave blank for random): ").strip().upper() or generate_code()
    my_ip = socket.gethostbyname(socket.gethostname())
    result = register_code(code, my_ip)

    if "REGISTERED" not in result:
        print(f"[!] Failed to register: {result}")
        return

    print(f"[✓] Code registered: {code}")
    print("[⏳] Waiting for connection...")

    s = socket.socket()
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    conn, addr = s.accept()
    print(f"[✓] Connected with {addr[0]}")

    threading.Thread(target=chat_recv, args=(conn,), daemon=True).start()
    chat_send(conn)
    conn.close()
    s.close()

def join_chat():
    code = input("Enter code to connect: ").strip().upper()
    ip = get_ip_from_code(code)

    if ip == "NOT_FOUND" or "Error" in ip:
        print(f"[!] Host not found for code: {code}")
        return

    print(f"[✓] Connecting to {ip}:{PORT}...")
    s = socket.socket()
    try:
        s.connect((ip, PORT))
        threading.Thread(target=chat_recv, args=(s,), daemon=True).start()
        chat_send(s)
        s.close()
    except:
        print("[!] Connection failed")

class ChatXShell(Cmd):
    intro = """
██████╗██╗  ██╗ █████╗ ████████╗██╗  ██╗
██╔══██╗██║  ██║██╔══██╗╚══██╔══╝██║  ██║
██████╔╝███████║███████║   ██║   ███████║
██╔═══╝ ██╔══██║██╔══██║   ██║   ██╔══██║
██║     ██║  ██║██║  ██║   ██║   ██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

ChatX v1.0 - Secure CLI Chat
Type help or ? to list commands.
"""
    prompt = "chatx> "

    def do_host(self, arg):
        "Host a chat session: host"
        host_chat()

    def do_join(self, arg):
        "Join a chat session: join"
        join_chat()

    def do_exit(self, arg):
        "Exit ChatX: exit"
        print("Exiting ChatX...")
        return True

    def do_clear(self, arg):
        "Clear the screen: clear"
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    ChatXShell().cmdloop()
