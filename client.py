import socket
import threading

def read_msg(sock_cli): 
    while True:
        msg = sock_cli.recv(65535)
        if len(msg) == 0:
            break
        print(msg)
        
    sock_cli.close()

#Object socket
sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect ke server
sock_cli.connect(('127.0.0.1', 6666))

#Buat Thread untuk menerima pesan
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

#Mengirim pesan
while True:
    try:
        msg = input("")

        if msg == "exit":
            sock_cli.close()
            break
        
        sock_cli.send(bytes(msg, "utf-8"))

    except KeyboardInterrupt:
        sock_cli.close()
        sys.exit(0)
