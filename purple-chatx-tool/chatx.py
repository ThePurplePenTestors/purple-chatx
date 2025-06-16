# universal_chat.py
import socket
import threading
import random
import string

MAPPING_SERVER = "YOUR_MAPPING_SERVER_IP"  # 👉 इसको सेट करें

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def register_code(code, ip):
    s = socket.socket()
    try:
        s.connect((MAPPING_SERVER, 5050))
        s.send(f"REGISTER|{code}|{ip}".encode())
        response = s.recv(1024).decode()
        return response
    except Exception as e:
        return f"Error: {e}"
    finally:
        s.close()


def get_ip_from_code(code):
    s = socket.socket()
    try:
        s.connect((MAPPING_SERVER, 5050))
        s.send(f"GET|{code}".encode())
        ip = s.recv(1024).decode()
        return ip
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
                print("Partner exited.")
                break
            print(f"\nPartner: {msg}\nYou: ", end="")
        except:
            break


def host_chat():
    print("\n[+] Hosting chat...")
    choice = input("Want to enter custom code? (y/n): ").strip().lower()
    if choice == "y":
        code = input("Enter your custom code (no spaces): ").strip().upper()
    else:
        code = generate_code()

    my_ip = socket.gethostbyname(socket.gethostname())
    result = register_code(code, my_ip)

    if "REGISTERED" not in result:
        print(f"[-] Error: {result}")
        return

    print(f"[✓] Share this code: {code}")
    print("[⏳] Waiting for client to connect...")

    s = socket.socket()
    s.bind(("0.0.0.0", 9999))
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
        print(f"[-] Could not find host for code: {code}")
        return

    print(f"[✓] Connecting to {ip}...")
    s = socket.socket()
    try:
        s.connect((ip, 9999))
        threading.Thread(target=chat_recv, args=(s,), daemon=True).start()
        chat_send(s)
        s.close()
    except:
        print("[-] Connection failed.")


def main():
    print("""
    =============================
    |    Universal Chat Tool    |
    =============================
    [1] Host Chat (Generate/Enter Code)
    [2] Join Chat (Enter Code)
    """)

    opt = input("Choose option (1 or 2): ").strip()
    if opt == '1':
        host_chat()
    elif opt == '2':
        join_chat()
    else:
        print("Invalid input")


if __name__ == "__main__":
    main()
