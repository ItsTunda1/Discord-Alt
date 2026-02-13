# peer.py

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
import tkinter as tk
import aiohttp
import asyncio
import base64
import uuid
import json
import math
import sys
import os

SIGNALING_SERVER = 'ws://3.22.241.217:8080/ws'

class PeerClient:
    def __init__(self):
        self.peer_id = str(uuid.uuid4())
        self.pc = RTCPeerConnection()
        self.ws = None
        self.session = None

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

    async def input_loop(self):
        while True:
            print("> ", end="", flush=True)
            msg = await asyncio.to_thread(input)

            await self.chat(msg)

    async def setup_peer_connection(self):
        @self.pc.on("icecandidate")
        async def on_icecandidate(event):
            if event.candidate:
                print(f"[ICE] New candidate gathered: {event.candidate}")
                await self.ws.send_str(json.dumps({
                    "type": "candidate",
                    "candidate": event.candidate.to_sdp(),
                    "sdpMid": event.candidate.sdp_mid,
                    "sdpMLineIndex": event.candidate.sdp_mline_index
                }))

    async def create_offer_if_needed(self):
        # Simple rule: UUIDs ending in '0' create the offer
        if self.peer_id.endswith('0'):
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            await self.ws.send_str(json.dumps({
                "type": "offer",
                "sdp": self.pc.localDescription.sdp
            }))

    async def handle_signaling(self):
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")

                    if msg_type == "offer":
                        await self.handle_offer(data)
                    elif msg_type == "answer":
                        await self.handle_answer(data)
                    elif msg_type == "candidate":
                        await self.handle_candidate(data)
                    elif msg_type == "chat":
                        await self.handle_chat(data)
        except Exception as e:
            print(f"[!] Unexpected error in signaling handler: {e}")
            await self.close()

    async def handle_offer(self, data):
        try:
            await self.pc.setRemoteDescription(RTCSessionDescription(data["sdp"], "offer"))
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            await self.ws.send_str(json.dumps({
                "type": "answer",
                "sdp": self.pc.localDescription.sdp
            }))
        except Exception as e:
            print(f"[!] Error handling offer: {e}")

    async def handle_answer(self, data):
        try:
            await self.pc.setRemoteDescription(RTCSessionDescription(data["sdp"], "answer"))
        except Exception as e:
            print(f"[!] Error handling answer: {e}")

    async def handle_candidate(self, data):
        candidate = RTCIceCandidate(
            sdp=data["candidate"],
            sdpMid=data["sdpMid"],
            sdpMLineIndex=data["sdpMLineIndex"]
        )
        print(f"[ICE] Received candidate from peer: {candidate}")
        await self.pc.addIceCandidate(candidate)

    async def handle_chat(self, data):
        if data.get("from") != self.peer_id:
            print(f"\n[Chat] {data['message']}\n> ", end="", flush=True)

    async def run(self):
        print(f"=== Starting Peer Client ===")
        print(f"Your Peer ID: {self.peer_id}")

        await self.connect_to_signaling()
        await self.setup_peer_connection()
        await self.create_offer_if_needed()

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