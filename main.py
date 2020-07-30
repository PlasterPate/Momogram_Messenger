import socket
import threading
import sys


def send_msg(s):
    global file_path
    while True:
        msg = input()
        if msg.startswith("/send"):
            s.send(msg.encode())
            file_path = msg[6:]
            send_file_event.set()
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
            recv_file_event.set()
            print("receiving file...")


def send_file(s2):
    while True:
        send_file_event.wait()
        print("sending file...")
        f = open(file_path, 'rb')
        data = f.read(4096)
        while data:
            s2.send(data)
            data = f.read(4096)
        s2.send("end".encode())
        f.flush()
        f.close()
        print("file sent!")
        send_file_event.clear()


def recv_file(s2):
    while True:
        recv_file_event.wait()
        with open(file_name, "wb") as f:
            while True:
                data = s2.recv(4096)
                if data.endswith(b'end'):
                    f.write(data[:-3])
                    break
                f.write(data)
        f.close()
        print("file received!")
        recv_file_event.clear()


s = socket.socket()
s2 = socket.socket()
host = "172.18.217.105"
port = 55565
port2 = 55566

print("waiting for connection...")
s.connect((host, port))
s2.connect((host, port2))

send_file_event = threading.Event()
send_file_event.clear()
recv_file_event = threading.Event()
recv_file_event.clear()

send_thread = threading.Thread(name="send", target=send_msg, args=(s,))
recv_thread = threading.Thread(name="recv", target=recv_msg, args=(s,))
send_file_thread = threading.Thread(name="send_file", target=send_file, args=(s2,))
recv_file_thread = threading.Thread(name="recv_file", target=recv_file, args=(s2,))


print("starting threads...")

send_thread.start()
print("send_thread run!!")

recv_thread.start()
print("recv_thread run!!")

send_file_thread.start()
print("send_file_thread run!!")

recv_file_thread.start()
print("recv_file_thread run!!")
print("***************")


