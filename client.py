import socket
import sys
import threading

def read_msg(sock_cli): 
    while True:
        msg = sock_cli.recv(65535).decode("utf-8")
        if len(msg) == 0:
            break
        print(msg)

    sock_cli.close()

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
while True:
    try:
        #Jika ingin memulai chat ketik chat
        start = input("")
        
        #Jika inputan benar
        if start == "chat":
            addfriend = input("Type addfriend to add friend or click enter to continue: ")
            
            #Menambah teman
            if addfriend == "addfriend":
                dest = addfriend
                #Memasukkan nama username teman
                addfriend_name = input("Name : ")
                msg = addfriend_name
                kosong = ""
                sock_cli.send(bytes("{}|{}|{}".format(dest, msg, kosong), "utf-8"))

            input("")

            #Memilih status
            status = input("Chat with friends mode? (yes / no) \n")
            
            #Jika iya
            if status == "yes":
                #Masuk ke dalam friends mode
                statusmode = "chat_friends"
                dest = input("Send to friends: ")
                msg = input("Message: ") 
                sock_cli.send(bytes("{}|{}|{}".format(dest, msg, statusmode), "utf-8"))

            #Jika tidak    
            if status == "no":
                dest = input("Send to: ")
                msg = input("Message: ")

                if msg == "exit":
                    sock_cli.close()
                    break
                 
                kosong = ""
                sock_cli.send(bytes("{}|{}|{}".format(dest, msg, kosong), "utf-8"))
        else:
            print("Type chat for starting")

    except KeyboardInterrupt:
        sock_cli.close()
        sys.exit(0)
