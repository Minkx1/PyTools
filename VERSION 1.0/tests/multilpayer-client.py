import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # бачить novaengine/

import pygame
import socket
import json
import novaengine as nova

# --- Server Config ---
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# --- Мережа ---
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_HOST, SERVER_PORT))
sock.setblocking(False)  # неблокуючий режим

# --- Nova ---
app = nova.NovaEngine()
app.player1_text = ""
app.player2_text = ""

main = nova.Scene()
with main.sprites():
    txt1 = nova.TextLabel(center=True).place_centered(100, 50).bind("app.player1_text")
    txt2 = nova.TextLabel(center=True).place_centered(app.screen.get_width()-100, 50).bind("app.player2_text")

@app.main()
def main():
    nova.Utils.fill_background(nova.Colors.WHITE)
    app.run_active_scene()

    # --- Відправка дій ---
    if app.KeyPressed(pygame.K_w):
        msg = {"action": "type", "player": 1, "text": app.player1_text + "w"}
        sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))

    # --- Прийом апдейтів від сервера ---
    try:
        data = sock.recv(4096).decode("utf-8")
        for line in data.splitlines():
            if not line.strip():
                continue
            update = json.loads(line)
            app.player1_text = update.get("player1", app.player1_text)
            app.player2_text = update.get("player2", app.player2_text)
    except BlockingIOError:
        pass  # нема даних — норм

app.run()