<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Room</title>
    <style>
      :root {
        --blue: #0a47e6;
        --dark: #2b2b2b;
        --bubble-blue: #0a47e6;
        --bubble-gray: #e1e1e1;
        --input-gray: #d9d9d9;
        --ink: #ffffff;
        --ink-dark: #1b1b1b;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        background: var(--dark);
        color: var(--ink);
      }

      .app {
        min-height: 100vh;
        height: 100vh;
        display: flex;
        flex-direction: column;
      }

      .topbar {
        background: var(--blue);
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 18px;
        font-weight: 700;
        font-size: 1.1rem;
      }

      .topbar-left {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .back-link {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: none;
        color: var(--ink);
        text-decoration: none;
        display: grid;
        place-items: center;
        font-size: 1.1rem;
      }

      .back-link:focus-visible {
        outline: 2px solid #ffffff;
        outline-offset: 2px;
      }

      .topbar .title {
        letter-spacing: 0.02em;
      }

      .screen {
        flex: 1;
        padding: 18px;
        display: flex;
        min-height: 0;
      }

      .chat {
        display: flex;
        flex-direction: column;
        gap: 14px;
        flex: 1;
        overflow-y: auto;
        padding-right: 6px;
        scroll-behavior: smooth;
        min-height: 0;
        scrollbar-width: none;
        -ms-overflow-style: none;
      }

      .chat::-webkit-scrollbar {
        width: 0;
        height: 0;
        display: none;
      }

      .bubble {
        padding: 12px 14px;
        border-radius: 16px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.3;
        word-break: break-word;
      }

      .bubble.left {
        background: var(--bubble-gray);
        color: var(--ink-dark);
        align-self: flex-start;
      }

      .bubble.right {
        background: var(--bubble-blue);
        color: var(--ink);
        align-self: flex-end;
      }

      .bottombar {
        background: var(--blue);
        height: 70px;
        padding: 0 16px;
      }

      .composer {
        height: 100%;
        display: flex;
        align-items: center;
      }

      .composer form {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .input-wide {
        flex: 1;
        height: 26px;
        background: var(--input-gray);
        border: none;
        border-radius: 2px;
        padding: 0 8px;
        font-size: 0.9rem;
        color: var(--ink-dark);
        min-width: 0;
      }

      .send {
        width: 26px;
        height: 26px;
        background: #ffffff;
        clip-path: polygon(10% 10%, 90% 50%, 10% 90%);
        border: none;
        padding: 0;
        cursor: pointer;
      }

      .send:focus-visible {
        outline: 2px solid #ffffff;
        outline-offset: 2px;
      }
    </style>
  </head>
  <body>
    <main class="app">
      <div class="topbar">
        <div class="topbar-left">
          <a class="back-link" href="/" aria-label="Back to home">&lt;</a>
          <span class="title">Cord</span>
        </div>
        <span>Main Room</span>
      </div>
      <div class="screen">
        <div class="chat"></div>
      </div>
      <div class="bottombar">
        <div class="composer">
          <form method="post" action="/chat/message">
            <input
              name="message"
              class="input-wide"
              id="messageInput"
              type="text"
              aria-label="Message"
            />
            <button
              class="send"
              id="sendButton"
              type="submit"
              aria-label="Send"
            ></button>
          </form>
        </div>
      </div>
    </main>
    <script>
      const chat = document.querySelector(".chat");
      const messageInput = document.getElementById("messageInput");
      const form = document.querySelector(".bottombar form");
      const peerId = crypto.randomUUID();
      const socket = new WebSocket("ws://3.22.241.217:8080/ws");
      const messages = [];

      function renderMessages(forceScroll = false) {
        const distanceFromBottom =
          chat.scrollHeight - chat.scrollTop - chat.clientHeight;
        const shouldScroll = forceScroll || distanceFromBottom < 80;
        chat.innerHTML = "";
        messages.forEach((message) => {
          const bubble = document.createElement("div");
          bubble.className = `bubble ${message.type === "sent" ? "right" : "left"}`;
          bubble.textContent = message.content;
          chat.appendChild(bubble);
        });
        if (shouldScroll) {
          chat.scrollTop = chat.scrollHeight;
        }
      }

      function clampMessage(text) {
        const trimmed = text.trim();
        if (trimmed.length <= 200) {
          return trimmed;
        }
        return `${trimmed.slice(0, 197)}...`;
      }

      function addMessage(type, payload, forceScroll = false) {
        const content = payload.content ?? payload.message ?? "";
        messages.push({ type, content });
        renderMessages(forceScroll);
      }

      socket.addEventListener("open", () => {
        socket.send(
          JSON.stringify({
            type: "register",
            peer_id: peerId,
          }),
        );
      });

      socket.addEventListener("message", (event) => {
        let payload = null;
        try {
          payload = JSON.parse(event.data);
        } catch (err) {
          payload = { type: "unknown", raw: String(event.data) };
        }
        addMessage("received", payload);
      });

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = messageInput.value.trim();
        if (!text || socket.readyState !== WebSocket.OPEN) {
          return;
        }

        const payload = {
          type: "chat",
          content: clampMessage(text),
          message: clampMessage(text),
          from: peerId,
        };
        socket.send(JSON.stringify(payload));
        addMessage("sent", payload, true);
        messageInput.value = "";
      });
    </script>
  </body>
</html>
