import socket
import threading


def read_msg(clients, sock_cli, addr_cli): 
    #Menerima pesan
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #Parsing pesannya
        print(addr_cli, data)
        
        #Mengirim pesan ke client        
        send_broadcast(clients, data, addr_cli)
        
    #Disconnect client dan dihapus dari daftar client
    sock_cli.close()
    print("Connection closed", addr_cli)
    del clients["{}:{}".format(addr_cli[0], addr_cli[1])]

#send_broadcast(ke semua client)
def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        send_msg(sock_cli, data)
        
def send_msg(sock_cli, data):
    sock_cli.send(data)

#Object socket server
sock_server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind server ke IP dan port tertentu
sock_server.bind(('0.0.0.0', 6666))

#Server listen
sock_server.listen(5)

#Dictionary untuk client
clients = {}

while True:
    try:
        sock_cli, addr_cli = sock_server.accept()

        #Buat Thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli))
        thread_cli.start()

        #Menambah client baru ke dictionary
        clients["[{}]:{}".format(addr_cli[0], addr_cli[1])] = (sock_cli, addr_cli, thread_cli)

    except KeyboardInterrupt:
        #Menutup object server
        sock_server.close()
        sys.exit(0)
