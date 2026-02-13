# server.py

import aiohttp
from aiohttp import web
import json
import traceback

connected_peers = {}  # peer_id -> {"ws": ws, "ip": ip}

async def websocket_handler(request):
    ws = web.WebSocketResponse(max_msg_size=2**22)  # 4MB chunks
    await ws.prepare(request)

    peer_ip = request.remote
    peer_id = None  # We will capture this from the "register" message
    
    print(f"[+] Client connected from {peer_ip}")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)

                # Handle peer registration
                if data.get("type") == "register":
                    peer_id = data.get("peer_id", "unknown")
                    connected_peers[peer_id] = {"ws": ws, "ip": peer_ip}
                    print(f"[+] Registered peer: {peer_id} from {peer_ip}")
                    continue

                disconnected = []
                message_text = json.dumps(data)
                for pid, peer_info in list(connected_peers.items()):
                    peer_ws = peer_info["ws"]
                    if peer_ws is not ws:
                        success = await send_to_peer(peer_ws, msg.data, is_binary=False)
                        if not success:
                            disconnected.append(pid)
                
                # Clean up disconnected peers
                for pid in disconnected:
                    remove_peer(pid)

                print(f"[Server] Received type: {data.get('type')}, size: {len(message_text)} bytes")
                print(f"[Server] Message: {message_text}")

            elif msg.type == aiohttp.WSMsgType.BINARY:
                print(f"[Server] Binary message received: {len(msg.data)} bytes")
                disconnected = []
                for pid, peer_info in list(connected_peers.items()):
                    peer_ws = peer_info["ws"]
                    if peer_ws is not ws:
                        success = await send_to_peer(peer_ws, msg.data, is_binary=True)
                        if not success:
                            disconnected.append(pid)

                # Clean up disconnected peers
                for pid in disconnected:
                    remove_peer(pid)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"[!] WebSocket error from {peer_ip}: {ws.exception()}")

    except Exception as e:
        traceback.print_exc()
        print(f"[!] Exception from {peer_ip}: {e}")

    finally:
        if peer_id:
            remove_peer(peer_id)

    return ws

def remove_peer(pid):
    if pid in connected_peers:
        del connected_peers[pid]
        print(f"[!] Removed peer {pid}")

async def send_to_peer(peer_ws, data, is_binary=False):
    try:
        if is_binary:
            await peer_ws.send_bytes(data)
        else:
            await peer_ws.send_str(data)
        return True
    except Exception as e:
        print(f"[!] Error sending to peer: {e}")
        traceback.print_exc()
        return False

# Add a route to list connected peers
async def peer_list_handler(request):
    peer_list = [
        {"peer_id": pid, "ip": info["ip"]}
        for pid, info in connected_peers.items()
    ]
    return web.json_response(peer_list)

async def pretty_peer_page(request):
    peer_list = [
        {"peer_id": pid, "ip": info["ip"]}
        for pid, info in connected_peers.items()
    ]
    html = f"""
        <html>
        <head>
            <title>Connected Peers</title>
            <style>
                body {{
                    background-color: #121212;
                    color: #e0e0e0;
                    font-family: Consolas, monospace;
                    padding: 20px;
                }}
                pre {{
                    background-color: #1e1e1e;
                    padding: 20px;
                    border-radius: 8px;
                    overflow: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                }}
            </style>
            <script>
                async function fetchPeers() {{
                    try {{
                        const res = await fetch('/peers');
                        const peers = await res.json();
                        document.getElementById('peerlist').textContent = JSON.stringify(peers, null, 4);
                    }} catch (e) {{
                        document.getElementById('peerlist').textContent = 'Error loading peers: ' + e;
                    }}
                }}
                setInterval(fetchPeers, 1000);
                window.onload = fetchPeers;
            </script>
        </head>
        <body>
            <h1>Connected Peers</h1>
            <pre id="peerlist">{json.dumps(peer_list, indent=4)}</pre>
        </body>
        </html>
    """
    return web.Response(text=html, content_type='text/html')



app = web.Application(client_max_size=1024**3)  # allow up to 1GB per message
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/peers', peer_list_handler)
app.router.add_get('/peers.html', pretty_peer_page)



if __name__ == '__main__':
    print("[*] WebSocket signaling server starting on port 8080")
    web.run_app(app, port=8080)






"""
ssh -i "server.pem" ubuntu@3.22.241.217

    ### EDIT
    nano signaling_server.py
    alt + \ (go to top)
    alt + t (delete all after)
    right click (paste)
    ctrl + x (write)

    ### KILLING
    sudo lsof -i :8080  # find PID
    sudo kill -9 <PID>

source venv/bin/activate

python3 signaling_server.py
"""


"""
Shows ALL Peers

http://3.22.241.217:8080/peers.html
"""