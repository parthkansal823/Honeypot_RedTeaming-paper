import socket, time

for i in range(10):
    s = socket.create_connection(("127.0.0.1", 2222), timeout=5)
    try:
        print(i, s.recv(64))
    except Exception as e:
        print(i, "FAILED:", repr(e))
    s.close()
    time.sleep(1)