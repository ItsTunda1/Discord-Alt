<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Welcome</title>
    <style>
      :root {
        --blue: #0a47e6;
        --dark: #2b2b2b;
        --light: #f3f3f3;
        --ink: #ffffff;
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

      .topbar .title {
        letter-spacing: 0.02em;
      }

      .screen {
        flex: 1;
        padding: 18px;
        display: flex;
        align-items: flex-start;
      }

      .welcome-form {
        width: 100%;
      }

      .welcome-row {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
      }

      .label {
        font-size: 1.1rem;
        color: var(--light);
        min-width: 86px;
      }

      .input {
        flex: 1;
        height: 28px;
        border: 1px solid #8a8a8a;
        background: var(--dark);
        color: var(--ink);
        padding: 0 8px;
      }

      .search {
        padding: 10px;
        background: var(--blue);
        border-radius: 4px;
        display: grid;
        place-items: center;
        font-weight: 700;
        border: none;
        color: var(--ink);
        cursor: pointer;
      }

      .create-room {
        position: fixed;
        right: 18px;
        bottom: 96px;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #f2efe6;
        color: #2b2b2b;
        display: grid;
        place-items: center;
        font-size: 2rem;
        text-decoration: none;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
      }

      .create-room:focus-visible {
        outline: 2px solid #ffffff;
        outline-offset: 3px;
      }

      .bottombar {
        background: var(--blue);
        height: 70px;
      }
    </style>
  </head>
  <body>
    <main class="app">
      <div class="topbar">
        <span class="title">Cord</span>
      </div>
      <div class="screen">
        <form class="welcome-row welcome-form" action="/room" method="get">
          <label class="label" for="roomInput">Room ID:</label>
          <input class="input" id="roomInput" name="room" type="text" />
          <button class="search" type="submit">Join</button>
        </form>
      </div>
      <div class="bottombar"></div>
    </main>
    <a class="create-room" href="/create-room" aria-label="Create room">+</a>
  </body>
</html>
