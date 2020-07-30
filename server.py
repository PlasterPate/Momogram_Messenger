import socket
import threading


def send_message(client):
    global file_path
    while True :
        message = input()
        if(message.startswith("/send")):
            client.send(message.encode())
            file_path = message[6:]
            send_file_event.set()
        else:
            client.send(message.encode())


def recv_message(client):
    global file_name
    while True:
        try:
            message = client.recv(4096)
            if str(message.decode()).startswith("/send"):
                file_name = str(message.decode()[6:]).split('/')[-1]
                raise Exception("file received")
            else:
                print(message.decode('utf-8'))
        except:
            recv_file_event.set()


def send_file(client2):
    while True:
        send_file_event.wait()
        print("sending file -> ", file_path)
        f = open(file_path, 'rb')
        data = f.read(4096)
        while (data):
            client2.send(data)
            data = f.read(4096)
        client2.send("end".encode())
        f.close()
        print("file sent!")
        send_file_event.clear()


def recv_file(client2):
    while True:
        recv_file_event.wait()
        print("receving file <- ", file_name)
        with open(file_name, 'wb') as q:
            while True:
                data = client2.recv(4096)
                if data.endswith(b'end'):
                    q.write(data[:-3])
                    break
                q.write(data)
        q.close()
        print("file received")
        recv_file_event.clear()


s = socket.socket()
s2 = socket.socket()

host = "172.18.218.33"
port = 55565
port2 = 55566

s.bind((host, port))
s.listen(5)
s2.bind((host, port2))
s2.listen(5)
client, addr = s.accept()
client2, addr2 = s2.accept()

print("connected to movahed: ", client)
print("connected to file movahed: ", client2)

send_file_event = threading.Event()
recv_file_event = threading.Event()

recv_thread = threading.Thread(name="recv", target=recv_message, args=(client,))
send_thread = threading.Thread(name="send", target=send_message, args=(client,))
file_send_thread = threading.Thread(name="filesend", target=send_file, args=(client2,))
file_recv_thread = threading.Thread(name="filerecv", target=recv_file, args=(client2,))

print("starting threads")
send_thread.start()
recv_thread.start()
file_send_thread.start()
file_recv_thread.start()