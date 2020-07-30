import socket
import threading


def send_msg(s):
    global file_path
    while True:
        msg = input()
        if msg.startswith("/send"):
            s.send(msg.encode())
            file_path = msg[6:]
            if not recv_file_thread.isAlive():
                send_file_thread.start()
                print("send_file_thread run!!")
            else:
                send_file_thread.run()
        else:
            s.send(msg.encode())


def recv_msg(s):
    global file_name
    while True:
        try:
            msg = s.recv(4096)
            if str(msg.decode()).startswith("/send"):
                file_name = str(msg.decode()[6:]).split('/')[-1]
                raise Exception("file received")
            else:
                print(msg.decode())
        except:
            print("except")
            if not recv_file_thread.isAlive():
                recv_file_thread.start()
                print("recv_file_thread run!!")
            else:
                recv_file_thread.run()

def send_file(s2):
    f = open(file_path, 'rb')
    data = f.read(4096)
    while(data):
        s2.send(data)
        data = f.read(4096)
    f.close()
    send_thread.join()
    print("file sent!")

def recv_file(s2):
    with open(file_name, "wb") as f:
        data = s2.recv(4096)
        while data:
            f.write(data)
            if not data:
                break
            data = s2.recv(4096)
    recv_thread.join()
    print("file received!")




s = socket.socket()
s2 = socket.socket()
host = "172.18.217.105"
port = 55565
port2 = 55566

print("waiting for connection...")
s.connect((host, port))
s2.connect((host, port2))

send_thread = threading.Thread(name="send", target=send_msg, args=(s,))
recv_thread = threading.Thread(name="recv", target=recv_msg, args=(s,))
send_file_thread = threading.Thread(name="send_file", target=send_file, args=(s2,))
recv_file_thread = threading.Thread(name="recv_file", target=recv_file, args=(s2,))



print("starting threads...")

recv_thread.start()
print("recv_thread run!!")

send_thread.start()
print("send_thread run!!")


