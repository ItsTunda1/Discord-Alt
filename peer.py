# peer.py

from aiortc import RTCPeerConnection
import aiohttp
import asyncio
import uuid
import json

SIGNALING_SERVER = 'ws://3.22.241.217:8080/ws'

class PeerClient:
    def __init__(self):
        self.peer_id = str(uuid.uuid4())
        self.pc = RTCPeerConnection()
        self.ws = None
        self.session = None

    ###
    ### Setup
    ###

    async def connect_to_signaling(self):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(SIGNALING_SERVER, max_msg_size=2**22)  # 4MB chunks
        print(f"[+] Connected to signaling server as {self.peer_id}")
        await self.register()

    async def register(self):
        await self.ws.send_str(json.dumps({
            "type": "register",
            "peer_id": self.peer_id
        }))

    async def handle_signaling(self):
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")

                    if msg_type == "chat":
                        await self.handle_chat(data)
        except Exception as e:
            print(f"[!] Unexpected error in signaling handler: {e}")
            await self.close()


    ###
    ### Chat Calls
    ###

    async def chat(self, msg):
        try:
            await self.ws.send_str(json.dumps({
                "type": "chat",
                "message": msg,
                "from": self.peer_id
            }))
        except Exception as e:
            print(f"[!] Failed to send chat message: {e}")
            await self.close()

    async def handle_chat(self, data):
        if data.get("from") != self.peer_id:
            print(f"\n[Chat] {data['message']}\n> ", end="", flush=True)



    ###
    ### Keep CLI Loop
    ###
    
    async def input_loop(self):
        while True:
            print("> ", end="", flush=True)
            msg = await asyncio.to_thread(input)

            await self.chat(msg)
    

    ###
    ### Run client
    ###

    async def run(self):
        print(f"=== Starting Peer Client ===")
        print(f"Your Peer ID: {self.peer_id}")

        await self.connect_to_signaling()

        await self.chat("Logged in")

        # Start input loop for chat
        asyncio.create_task(self.input_loop())

        # Listen to signaling messages
        await self.handle_signaling()

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.pc:
            await self.pc.close()
        if self.session:
            await self.session.close()



if __name__ == "__main__":
    client = PeerClient()

    # Run asyncio event loop
    asyncio.run(client.run())