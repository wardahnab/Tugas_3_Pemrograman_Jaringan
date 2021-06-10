import socket
import sys
import threading


def read_msg(clients, friends, sock_cli, addr_cli, src_username):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parsing pesannya
        dest, msg = data.split(b"|", 1)
        dest = dest.decode("utf-8")

        #kirim data ke semua client
        if dest == "bcast":
            msg = msg.decode("utf-8")
            _msg = f"<{src_username}>: {msg}"
            # send_friends(clients, friends, src_username, _msg, addr_cli)
            send_broadcast(clients, msg, addr_cli)
        elif dest == "friends":
            msg = msg.decode("utf-8")
            _msg = f"<{src_username}>: {msg}"
            send_friends(clients, friends, src_username, _msg, addr_cli)
            # send_broadcast(clients, msg, addr_cli)
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

            dest_sock_cli = get_sock(clients, src_username, dest_username)
            if dest_sock_cli is not None:
                send_file(dest_sock_cli, filename, size, filedata, src_username)
        elif dest == "reqfriend":
            dest_username = msg.decode("utf-8")
            if dest_username not in clients:
                send_msg(clients[src_username][0], f"{dest_username} not in clients")
                continue
            send_friend_request(clients[dest_username][0], src_username)
        elif dest == "accfriend":
            dest_username = msg.decode("utf-8")
            friends[src_username].append(dest_username)
            friends[dest_username].append(src_username)
            send_msg(clients[dest_username][0], f"{src_username} added")
            send_msg(clients[src_username][0], f"{dest_username} added")
        else:
            dest_username = dest
            msg = msg.decode("utf-8")
            _msg = f"<{src_username}>: {msg}"
            dest_sock_cli = get_sock(clients, src_username, dest_username)
            if dest_sock_cli is not None:
                send_msg(dest_sock_cli, _msg)
    sock_cli.close()
    print("connection closed", addr_cli)
    del clients[src_username]


def send_file(sock_cli, filename, size, filedata, username):
    file = f'file|{username}|{filename}|{size}|'.encode('utf-8')
    file += filedata
    sock_cli.sendall(file)


def send_friends(clients, friends, src_username, data, sender_addr_cli):
    cur_friends = friends[src_username]
    for cur_friend in cur_friends:
        if cur_friend not in clients:
            continue
        sock_cli, addr_cli, _ = clients[cur_friend]
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (addr_cli[0] == sender_addr_cli[0] and addr_cli[1] == sender_addr_cli[1]):
            send_msg(sock_cli, data)

def send_friend_request(sock_cli, src_username):
    message = f"reqfriend|{src_username}"
    sock_cli.send(message.encode("utf-8"))


def send_msg(sock_cli, data):
    message = f'message|{data}'
    sock_cli.send(bytes(message, "utf-8"))


def get_sock(clients, src_username, dest_username):
    # if dest_username not in friends[src_username]:
    #     send_msg(clients[src_username][0], f"Error: {dest_username} not a friend")
    #     return None
    if dest_username not in clients:
        send_msg(clients[src_username][0], f"Error: {dest_username} not in clients")
        return None
    return clients[dest_username][0]


server_address = ('0.0.0.0', 6666)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

# buat dictionary utk menyimpan informasi
clients = {}
friends = {}

try:
    while True:
        sock_cli, addr_cli = server_socket.accept()

        # baca username client
        src_username = sock_cli.recv(65535).decode("utf-8")
        print(src_username, "joined")

        # buat thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, friends, sock_cli, addr_cli, src_username))
        thread_cli.start()

        # simpan informasi client ke dictionary
        clients[src_username] = (sock_cli, addr_cli, thread_cli)
        friends[src_username] = []

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)
