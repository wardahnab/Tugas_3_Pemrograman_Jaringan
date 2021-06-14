import socket
import sys
import threading
import os
import ntpath

def read_msg(sock_cli): 
    #Menerima pesan
    while True:
        msg = sock_cli.recv(65535)
        if len(msg) == 0:
            break
        datatype, message = msg.split(b"|", 1)
        datatype = datatype.decode("utf-8")

        #semua pesan selain file
        if datatype == "message":
            message = message.decode("utf-8")
            print(message)

        #file
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

#Object socket
sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect ke server
sock_cli.connect(('127.0.0.1', 6666))

#Mengambil username
username = sys.argv[1]
sock_cli.send(bytes(username, "utf-8"))

#Buat Thread untuk menerima pesan
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

#Mengirim pesan
try:
    while True:
        dest = input("-kirim pesan privat : chat <username> <message>\n"
                     "-kirim broadcast : bcast <message>\n"
                     "-tambah teman : addfriend <username>\n"
                     "-kirim pesan khusus teman : friends <message>\n"
                     "-kirim file : sendfile <username> <filepath>\n"
                     "-keluar : exit\n")
        msg = dest.split(" ", 1)

        if msg[0] == "exit":
            sock_cli.close()
            break

        elif msg[0] == "chat":
            username, message = msg[1].split(" ", 1)
            sock_cli.send(bytes("{}|{}".format(username, message), "utf-8"))    
            
        elif msg[0] == "bcast":
            sock_cli.send(bytes("bcast|{}".format(msg[1]), "utf-8"))    
            
        elif msg[0] == "addfriend":
            friend = msg[1]
            sock_cli.send(bytes("addfriend|{}".format(friend), "utf-8"))    

        elif msg[0] == "friends":
            sock_cli.send(bytes("friends|{}".format(msg[1]), "utf-8"))    

        elif msg[0] == "sendfile":
            username, filepath = msg[1].split(" ", 1)
            size = os.path.getsize(filepath)
            print("sending ", filepath, " to ", username)
            filedata = f'sendfile|{username}|{filepath}|{size}|'.encode('utf-8')
            with open(filepath, 'rb') as f:
                filedata += f.read()
            sock_cli.sendall(filedata)
            
        else:
            print("wrong command")

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)
