from pathlib import Path
from uuid import uuid4

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


if __name__ == "__main__":
    app.run(host="localhost", port=8080)
