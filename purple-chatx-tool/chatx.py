from cmd import Cmd
import socket
import threading
import random
import string
import os

MAPPING_SERVER = "YOUR_MAPPING_SERVER_IP"  # <- Set this to your code mapping server or leave blank
PORT = 9999
ENABLE_LOGGING = True
LOG_FILE = "chatx.log"
ENCRYPTION_KEY = "pankaj2025"

# === UTILITIES ===
def log(msg):
    if ENABLE_LOGGING:
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")

def xor_encrypt_decrypt(msg, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(msg))

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# === DUMMY PLACEHOLDERS (MAPPING DISABLED) ===
def register_code(code, ip):
    return "REGISTERED"

def get_ip_from_code(code):
    return "127.0.0.1" if code else "NOT_FOUND"

# === CHAT FUNCTIONS ===
def chat_send(sock):
    while True:
        try:
            msg = input("You: ")
            if msg.strip().lower() == "exit":
                sock.send(xor_encrypt_decrypt("exit", ENCRYPTION_KEY).encode())
                break
            sock.send(xor_encrypt_decrypt(msg, ENCRYPTION_KEY).encode())
            log("You: " + msg)
        except:
            break

def chat_recv(sock):
    while True:
        try:
            msg = xor_encrypt_decrypt(sock.recv(1024).decode(), ENCRYPTION_KEY)
            if msg.lower() == "exit":
                print("\n[Partner exited chat]")
                break
            print(f"\nPartner: {msg}\nYou: ", end="")
            log("Partner: " + msg)
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

# === SHELL ===
class ChatXShell(Cmd):
    intro = """
██████╗██╗  ██╗ █████╗ ████████╗██╗  ██╗
██╔══██╗██║  ██║██╔══██╗╚══██╔══╝██║  ██║
██████╔╝███████║███████║   ██║   ███████║
██╔═══╝ ██╔══██║██╔══██║   ██║   ██╔══██║
██║     ██║  ██║██║  ██║   ██║   ██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

ChatX v1.1 - Secure CLI Chat
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
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_config(self, arg):
        "Change configuration (log, key): config"
        global ENABLE_LOGGING, ENCRYPTION_KEY
        option = input("Change (log/key): ").strip().lower()
        if option == "log":
            ENABLE_LOGGING = input("Enable logging? (yes/no): ").lower().startswith("y")
            print(f"Logging set to {ENABLE_LOGGING}")
        elif option == "key":
            ENCRYPTION_KEY = input("Enter new encryption key: ").strip()
            print("Encryption key updated.")
        else:
            print("Unknown config option.")

if __name__ == '__main__':
    ChatXShell().cmdloop()
