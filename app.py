from pathlib import Path
from uuid import uuid4
import threading
import asyncio

# AWS Peer Connection
import peer
# Global reference to PeerClient instance
client = None
loop = None

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
    room_id = request.query.get("room") or ROOM_ID
    return template(
        "room",
        room_id=room_id,
        template_lookup=[TEMPLATE_DIR],
    )


@app.get("/create-room")
def create_room():
    room_id = uuid4().hex[:6]
    redirect(f"/?room={room_id}")





@app.post('/chat/message')
def handle_chat():
    global client, loop
    message = request.forms.get('message')
    
    if message and client and loop:
        # Schedule the broadcast in the async loop
        asyncio.run_coroutine_threadsafe(client.broadcast_chat(message), loop)
        
        return {"status": "success"}





def send_message_to_bottle(message):
    print("test:", message)
    '''response.content_type = 'application/json'
    response.status = 200
    return json.dumps({
        "status": "message_received",
        "message": message
    })'''



def run_bottle():
    # Run Bottle app in a separate thread
    app.run(host="localhost", port=8080)

def run_peer():
    global client, loop

    # Run the AWS peer client in a dedicated asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = peer.PeerClient()
    client.message_callback = send_message_to_bottle

    loop.create_task(client.run())
    loop.run_forever()

if __name__ == "__main__":
    # Start Bottle in a separate thread
    bottle_thread = threading.Thread(target=run_bottle)
    bottle_thread.daemon = True  # Daemon thread will exit when the main program exits
    bottle_thread.start()

    # Run the AWS peer client concurrently with Bottle
    run_peer()