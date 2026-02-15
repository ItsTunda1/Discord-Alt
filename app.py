from pathlib import Path
from uuid import uuid4
import threading
import asyncio

# AWS Peer Connection
import peer
# Global reference to PeerClient instance
client = None

from bottle import Bottle, request, static_file, template, redirect

TEMPLATE_DIR = (Path(__file__).resolve().parent / "templates").as_posix()
STATIC_DIR = (Path(__file__).resolve().parent / "static").as_posix()
ROOM_ID = "lobby"

app = Bottle()

@app.get("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root=STATIC_DIR)


@app.get("/")
def index():
    return template(
        "welcome",
        template_lookup=[TEMPLATE_DIR],
    )


@app.get("/room")
def room():
    room_id = request.query.get("room") or ROOM_ID
    return template(
        "room",
        room_id=room_id,
        template_lookup=[TEMPLATE_DIR],
    )


@app.get("/create-room")
def create_room():
    room_id = uuid4().hex[:6]
    redirect(f"/room?room={room_id}")





@app.post('/chat/message')
def handle_chat():
    # 1. Properly get the message from a form or JSON
    message = request.forms.get('message')
    print(f"Recieved the message: {message}")
    if not client:
        return "Peer client not connected!"
    if message:
        # 2. Run the async chat client
        asyncio.run(client.chat(message))
        return {"status": "success", "sent": message}
    return "No message provided"





def run_bottle():
    # Run Bottle app in a separate thread
    app.run(host="localhost", port=8080)

def run_peer():
    global client
    # Run the AWS peer client in the main asyncio event loop
    client = peer.PeerClient()
    peer.asyncio.run(client.run())

if __name__ == "__main__":
    # Start Bottle in a separate thread
    bottle_thread = threading.Thread(target=run_bottle)
    bottle_thread.daemon = True  # Daemon thread will exit when the main program exits
    bottle_thread.start()

    # Run the AWS peer client concurrently with Bottle
    run_peer()