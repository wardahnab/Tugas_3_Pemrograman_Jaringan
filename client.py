import socket
import sys
import threading
import os
import ntpath

def read_msg(sock_cli, friend_req_queue):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        datatype, message = data.split(b"|", 1)
        datatype = datatype.decode("utf-8")
        if datatype == "message":
            message = message.decode("utf-8")
            print(message)
        elif datatype == "file":
            sender, filename, filesize, filedata = message.split(b'|', 3)
            sender = sender.decode('utf-8')
            print("file received from", sender)
            filename = filename.decode('utf-8')
            filename = ntpath.basename(filename)
            filesize = int(filesize.decode('utf-8'))
            while len(filedata) < filesize:
                if filesize - len(filedata) > 65536:
                    filedata += sock_cli.recv(65536)
                else:
                    filedata += sock_cli.recv(filesize - len(filedata))
                    break
            with open(filename, 'wb') as f:
                f.write(filedata)
        elif datatype == "reqfriend":
            friend = message.decode("utf-8")
            friend_req_queue.add(friend)
            print(f"Friend request from {friend}\n"
                  f"type: 'accfriend {friend}' to accept friend request")

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(('127.0.0.1', 6666))

#kirim username ke server
username = input("Username: ")
sock_cli.send(bytes(username, "utf-8"))
# sock_cli.send(bytes(sys.argv[1], "utf-8"))

friend_req_queue = set()

#buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=read_msg, args=(sock_cli, friend_req_queue))
thread_cli.start()

try:
    while True:
        dest = input("message <username> <message> (kirim message biasa)\n"
                     "bcast <message> (kirim broadcast)\n"
                     "sendfile <username> <filepath> (kirim file)\n"
                     "reqfriend <username>\n"
                     "accfriend <username>\n"
                     "friends (broadcast khusus friends)\n"
                     "exit (keluar)\n")
        msg = dest.split(" ", 1)

        if msg[0] == "exit":
            sock_cli.close()
            break
        elif msg[0] == "message":
            username, message = msg[1].split(" ", 1)
            sock_cli.send(f"{username}|{message}".encode("utf-8"))
        elif msg[0] == "bcast":
            sock_cli.send(f"bcast|{msg[1]}".encode("utf-8"))
        elif msg[0] == "friends":
            sock_cli.send(f"friends|{msg[1]}".encode("utf-8"))
        elif msg[0] == "sendfile":
            username, filepath = msg[1].split(" ", 1)
            size = os.path.getsize(filepath)
            print("sending ", filepath, " to ", username)
            filedata = f'sendfile|{username}|{filepath}|{size}|'.encode('utf-8')
            with open(filepath, 'rb') as f:
                filedata += f.read()
            sock_cli.sendall(filedata)
        elif msg[0] == "reqfriend":
            sock_cli.send(f"reqfriend|{msg[1]}".encode("utf-8"))
        elif msg[0] == "accfriend":
            friend = msg[1]
            print(friend_req_queue)
            if friend in friend_req_queue:
                friend_req_queue.remove(friend)
                sock_cli.send(f"accfriend|{friend}".encode("utf-8"))
            else:
                print("not detected")

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)



