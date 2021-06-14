import socket
import sys
import threading


def read_msg(clients, sock_cli, addr_cli, username_cli, friends): 
    #Menerima pesan
    while True:
        data = sock_cli.recv(65535).decode("utf-8")
        if len(data) == 0:
            break

        #Parsing pesannya
        dest, msg, statusmode = data.split("|")
        print(addr_cli, dest, msg, statusmode)
    
    #Mengirim pesan ke client        
        #Mengirim pesan untuk semua client
        if dest == "semua":
            msg = "[{}]: {}".format(username_cli, msg)
            send_broadcast(clients, msg, addr_cli)
        
        #Menambah teman
        elif dest == "addfriend":
            dest_username_cli = msg
            friends[username_cli].append(dest_username_cli)
            friends[dest_username_cli].append(username_cli)
            send_msg(clients[username_cli][0], "{} is now friend".format(dest_username_cli))
            send_msg(clients[dest_username_cli][0], "{} is now friend".format(username_cli))
        
        #Chat dalam friends mode
        elif statusmode == "chat_friends":
            dest_username_cli = friends[username_cli]
            msg = "[{}]: {}".format(username_cli, msg)
            for dest_sock_cli, dest_addr_cli, _, dest_username_cli in clients.values():
                if dest_username_cli == dest:
                    send_msg(dest_sock_cli, msg)
        
        #Mengirim pesan untuk cilent tertentu (tidak harus teman)
        else:
            msg = "[{}]: {}".format(username_cli, msg)
            for dest_sock_cli, dest_addr_cli, _, dest_username_cli in clients.values():
                print(dest)
                print(dest_username_cli)
                if dest_username_cli == dest:
                    send_msg(dest_sock_cli, msg)
        
    #Disconnect client dan dihapus dari daftar client
    sock_cli.close()
    print("Connection closed", addr_cli)
    del clients["{}:{}".format(addr_cli[0], addr_cli[1])]

#send_broadcast(ke semua client)
def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _, username_cli in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

#send_msg(pesan ke client tertentu)
def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))

#Object socket server
sock_server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind server ke IP dan port tertentu
sock_server.bind(('0.0.0.0', 6666))

#Server listen
sock_server.listen(5)

#Dictionary untuk client
clients = {}
friends = {}

while True:
    try:
        sock_cli, addr_cli = sock_server.accept()
    
        #Menerima username dari client
        username_cli = sock_cli.recv(65535).decode("utf-8")
        print(" {} successfully joined".format(username_cli))

        #Buat Thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, username_cli, friends))
        thread_cli.start()

        #Menambah client baru ke dictionary
        clients[username_cli] = (sock_cli, addr_cli, thread_cli, username_cli)
        friends[username_cli] = []

    except KeyboardInterrupt:
        #Menutup object server
        sock_server.close()
        sys.exit(0)
