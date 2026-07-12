---
description: Start a voice-conversation web app for this Claude Code session
allowed-tools: Bash
---

Start the voice conversation app for the **current project directory**, then give the user the URL.

1. Run the launcher (it starts the server + a public localhost.run tunnel and prints one URL). Run it so cwd is the current project directory, and capture its output:

   ```
   bash <repo>/plugins/voice-conversation/start.sh
   ```
   (the symlinked source lives in the repo; `start.sh` self-locates `server.py` next to it.)

2. Read the line beginning `OPEN_THIS_URL:` from the output and give the user exactly that `https://….lhr.life/?k=…` link.

3. Tell the user: open it in **Chrome**, click **Start talking**, and speak. The link's `?k=` token is required — without it the server returns 403.

Notes: host model = `gpt-4o-mini` (`VOICE_MODEL` to override), port via `VOICE_PORT`. Each launch kills any prior instance and mints a fresh token/URL.
