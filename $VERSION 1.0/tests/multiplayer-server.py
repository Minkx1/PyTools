import socket
import select
import json

HOST = "0.0.0.0"
PORT = 5000

player1_text = ""
player2_text = ""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

clients = []

print(f"Server running on {HOST}:{PORT}")

while True:
    rlist, _, _ = select.select([server] + clients, [], [], 0.05)
    for s in rlist:
        if s is server:
            conn, addr = server.accept()
            conn.setblocking(False)
            clients.append(conn)
            print("Client connected:", addr)
        else:
            try:
                data = s.recv(4096).decode("utf-8")
                if not data:
                    clients.remove(s)
                    continue
                for line in data.splitlines():
                    msg = json.loads(line)
                    if msg["player"] == 1:
                        player1_text = msg["text"]
                    elif msg["player"] == 2:
                        player2_text = msg["text"]
            except:
                clients.remove(s)

    # Розсилка стану
    state = json.dumps({"player1": player1_text, "player2": player2_text}) + "\n"
    for c in clients:
        try:
            c.sendall(state.encode("utf-8"))
        except:
            clients.remove(c)
