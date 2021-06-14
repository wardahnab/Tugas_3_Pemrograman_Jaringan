import socket
import sys
import threading


def read_msg(clients, friends, sock_cli, addr_cli, src_username):
    #Menerima pesan
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parsing pesannya
        dest, msg = data.split(b"|", 1)
        dest = dest.decode("utf-8")

    #Mengirim pesan ke client
        #Mengirim pesan ke semua client
        if dest == "bcast":
            msg = msg.decode("utf-8")
            msg2 = "<{}>: {}".format(src_username, msg)
            send_broadcast(clients, msg2, addr_cli)

        #Menambah teman
        elif dest == "addfriend":
            dest_username = msg.decode("utf-8")
            friends[src_username].append(dest_username)
            friends[dest_username].append(src_username)
            send_msg(clients[dest_username][0], f"{src_username} is now friend")
            send_msg(clients[src_username][0], f"{dest_username} is now friend")

        #Mengirim pesan ke semua teman
        elif dest == "friends":
            msg = msg.decode("utf-8")
            msg2 = "<{}>: {}".format(src_username, msg)
            send_friends(clients, friends, src_username, msg2, addr_cli)
            
        #Mengirim file
        elif dest == "sendfile":
            dest_username, filename, size, filedata = msg.split(b'|', 3)
            dest_username = dest_username.decode("utf-8")
            filename = filename.decode("utf-8")
            size = int(size.decode("utf-8"))

            while len(filedata) < size:
                if size-len(filedata) > 65536:
                    filedata += sock_cli.recv(65536)
                else:
                    filedata += sock_cli.recv(size - len(filedata))
                    break
            dest_sock_cli = clients[dest_username][0]
            if dest_sock_cli is not None:
                send_file(dest_sock_cli, filename, size, filedata, src_username)
        
        #Mengirim pesan privat
        else:
            msg = msg.decode("utf-8")
            msg2 = "<{}>: {}".format(src_username, msg)
            dest_sock_cli = clients[dest][0]
            send_msg(dest_sock_cli, msg2)

    #Disconnect client dan dihapus dari daftar client
    sock_cli.close()
    print("connection closed", addr_cli)
    del clients["{}:{}".format(addr_cli[0], addr_cli[1])]

#send_broadcast(ke semua client)
def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (addr_cli[0] == sender_addr_cli[0] and addr_cli[1] == sender_addr_cli[1]):
            send_msg(sock_cli, data)

#send_msg(pesan ke client tertentu)
def send_msg(sock_cli, data):
    message = f'message|{data}'
    sock_cli.send(bytes(message, "utf-8"))

#send_friends(ke semua teman)
def send_friends(clients, friends, src_username, data, sender_addr_cli):
    cur_friends = friends[src_username]
    for cur_friend in cur_friends:
        if cur_friend not in clients:
            continue
        sock_cli, addr_cli, _ = clients[cur_friend]
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

#send_file(kirim file)
def send_file(sock_cli, filename, size, filedata, username):
    file = f'file|{username}|{filename}|{size}|'.encode('utf-8')
    file += filedata
    sock_cli.sendall(file)


#Object socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind server ke IP dan port tertentu
server_socket.bind(('0.0.0.0', 6666))

#Server listen
server_socket.listen(5)

#Dictionary untuk client dan friend
clients = {}
friends = {}

try:
    while True:
        sock_cli, addr_cli = server_socket.accept()

        #Menerima username dari client
        src_username = sock_cli.recv(65535).decode("utf-8")
        print(" {} successfully joined".format(src_username))

        #Buat Thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, friends, sock_cli, addr_cli, src_username))
        thread_cli.start()

        #Menambah client baru ke dictionary
        clients[src_username] = (sock_cli, addr_cli, thread_cli)
        friends[src_username] = []

except KeyboardInterrupt:
    #Menutup object server
    server_socket.close()
    sys.exit(0)
