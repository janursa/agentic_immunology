#!/usr/bin/env python
"""Voice-conversation bridge between the user (browser mic/speakers) and Claude Code.

Per turn:  browser STT -> /talk -> host model composes a Claude prompt ->
`claude -p --resume` -> host model narrates the reply -> browser TTS.

The browser handles speech (Web Speech API), so this runs on a headless remote box.
It is reached via a cloudflared tunnel (public HTTPS), so /talk is guarded by a token.
"""
import os, json, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from openai import OpenAI

PORT = int(os.environ.get("VOICE_PORT", "8765"))
MODEL = os.environ.get("VOICE_MODEL", "gpt-4o-mini")
STT_MODEL = os.environ.get("VOICE_STT_MODEL", "whisper-1")   # server-side STT (browser audio -> text)
TOKEN = os.environ.get("VOICE_TOKEN", "")          # if set, /talk requires header x-voice-token
PROJECT_DIR = os.getcwd()
CLAUDE_TIMEOUT = int(os.environ.get("VOICE_CLAUDE_TIMEOUT", "600"))

client = OpenAI()
session_id = None            # ponytail: single global Claude session; add a map for concurrent users
transcript = []              # list of ("User"|"Claude", text)

COMPOSE_SYS = (
    "You bridge a user speaking by voice and Claude Code, a coding agent working in their project. "
    "Given the conversation so far and the user's latest spoken message, output the single prompt to send "
    "to Claude Code now. Usually pass the user's intent through almost verbatim as a clear instruction; "
    "only fix obvious speech-to-text noise. Output ONLY the prompt, nothing else."
)
NARRATE_SYS = (
    "You are a voice host relaying Claude Code's output to a user listening by voice. "
    "Summarize the output in 1-3 short spoken sentences. No markdown, no code blocks, no bullet points. "
    "If Claude asked a question or needs a decision, relay it clearly so the user can answer."
)


def chat(system, msgs):
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "system", "content": system}] + msgs
    )
    return r.choices[0].message.content.strip()


def host_compose(user_text):
    msgs = [{"role": "user" if who == "User" else "assistant", "content": f"[{who}] {t}"}
            for who, t in transcript[-10:]]
    msgs.append({"role": "user", "content": f"[User] {user_text}\n\nWrite the prompt to send to Claude Code now."})
    return chat(COMPOSE_SYS, msgs)


def transcribe(audio_bytes, ctype="audio/webm"):
    ext = "mp4" if "mp4" in ctype else "ogg" if "ogg" in ctype else "webm"
    r = client.audio.transcriptions.create(model=STT_MODEL, file=(f"speech.{ext}", audio_bytes))
    return (r.text or "").strip()


def ask_claude(prompt):
    global session_id
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]
    r = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
    if r.returncode != 0:
        return f"(Claude error: {(r.stderr or r.stdout)[:300]})"
    data = json.loads(r.stdout)
    session_id = data.get("session_id", session_id)
    return data.get("result", "") or "(empty response)"


def handle_turn(user_text):
    prompt = host_compose(user_text)
    claude_out = ask_claude(prompt)
    reply = chat(NARRATE_SYS, [{"role": "user", "content": claude_out}])
    transcript.append(("User", user_text))
    transcript.append(("Claude", claude_out))
    return {"prompt": prompt, "claude": claude_out, "reply": reply}


PAGE = """<!doctype html><meta charset=utf-8>
<title>Claude Voice</title>
<style>
 body{font:16px/1.5 system-ui;max-width:680px;margin:2rem auto;padding:0 1rem;background:#111;color:#eee}
 button{font-size:1.2rem;padding:.7rem 1.4rem;border:0;border-radius:8px;cursor:pointer}
 #mic{background:#3b82f6;color:#fff}#mic.on{background:#ef4444}
 #status{margin-left:.8rem;color:#888;font-size:.9rem}
 .msg{margin:.6rem 0;padding:.5rem .8rem;border-radius:8px;white-space:pre-wrap}
 .u{background:#1e3a5f}.c{background:#2a2a2a}.sys{background:#3a1e1e;color:#f99;font-size:.9rem}
 #interim{color:#9bf;min-height:1.4em;margin:.6rem 0;font-style:italic}
 #log{margin-top:1rem;border-top:1px solid #333;padding-top:.5rem}
</style>
<h2>Claude voice conversation</h2>
<button id=mic>🎤 Hold-free: click to record</button>
<span id=status></span>
<div id=interim></div>
<div id=log></div>
<script>
// Push-to-talk: click to start recording, click again to stop+send. STT is server-side
// (Whisper), so any browser with MediaRecorder works. No VAD/threshold guessing.
const K = new URLSearchParams(location.search).get('k') || '';
const mic=document.getElementById('mic'), log=document.getElementById('log'),
      status=document.getElementById('status'), interim=document.getElementById('interim');
let stream, rec, chunks=[], recording=false, busy=false, MIME='', t0=0, ticker;
function add(cls, who, txt){ const d=document.createElement('div'); d.className='msg '+cls; d.innerHTML='<b>'+who+':</b> '+txt; log.appendChild(d); d.scrollIntoView(); }
function setStatus(s){ status.textContent=s; }
function speak(txt, done){ const u=new SpeechSynthesisUtterance(txt); u.onend=done; u.onerror=done; speechSynthesis.speak(u); }
function pickMime(){
  const types=['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'];
  for(const t of types){ if(window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) return t; }
  return '';
}
async function ensureMic(){
  if(stream) return;
  stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
  MIME = pickMime();
}
function startRec(){
  chunks=[];
  try{ rec = MIME ? new MediaRecorder(stream,{mimeType:MIME}) : new MediaRecorder(stream); }
  catch(e){ add('sys','error','cannot record audio in this browser: '+e); return false; }
  rec.ondataavailable = e => { if(e.data.size) chunks.push(e.data); };
  rec.onstop = () => {
    const blob = new Blob(chunks,{type: rec.mimeType||MIME||'audio/webm'});
    if(blob.size>0) sendAudio(blob);
    else add('sys','error','no audio captured (0 bytes) — mic may be muted or wrong input device');
  };
  rec.start(); t0=performance.now();
  ticker=setInterval(()=>{ interim.textContent='● recording '+((performance.now()-t0)/1000).toFixed(1)+'s — click to stop & send'; },100);
  return true;
}
async function sendAudio(blob){
  busy=true; interim.textContent='transcribing '+(blob.size/1024|0)+' KB…'; setStatus('thinking…');
  try{
    const r=await fetch('/talk',{method:'POST',headers:{'content-type':(blob.type||'audio/webm'),'x-voice-token':K},body:blob});
    if(r.status===403){ add('sys','error','bad/missing token in URL'); busy=false; interim.textContent=''; return; }
    const j=await r.json();
    if(j.user) add('u','You', j.user);
    add('c','Claude', j.reply);
    interim.textContent=''; setStatus('speaking…');
    speak(j.reply, ()=>{ setStatus(''); });
  }catch(err){ add('sys','error', err); }
  busy=false;
}
mic.onclick = async () => {
  if(!navigator.mediaDevices || !window.MediaRecorder){ alert('This browser cannot record audio.'); return; }
  if(busy){ return; }
  if(!recording){
    try{ await ensureMic(); }catch(e){ add('sys','error','microphone blocked — allow the mic (camera/lock icon in address bar), then click again'); return; }
    if(!startRec()) return;
    recording=true; mic.classList.add('on'); mic.textContent='⏹ Stop & send';
    speechSynthesis.cancel();
  } else {
    recording=false; clearInterval(ticker); mic.classList.remove('on'); mic.textContent='🎤 Click to record';
    if(rec && rec.state==='recording') rec.stop();
  }
};
</script>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.split("?")[0] == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/talk":
            self._send(404, "{}")
            return
        if TOKEN and self.headers.get("x-voice-token", "") != TOKEN:
            self._send(403, json.dumps({"reply": "forbidden"}))
            return
        n = int(self.headers.get("content-length", 0))
        body = self.rfile.read(n)
        ctype = self.headers.get("content-type", "")
        try:
            if ctype.startswith("audio/"):
                text = transcribe(body, ctype)
            else:
                text = json.loads(body or b"{}").get("text", "").strip()
        except Exception as e:
            self._send(200, json.dumps({"reply": f"Transcription failed: {e}", "user": ""}))
            return
        if not text:
            self._send(200, json.dumps({"reply": "I didn't catch that.", "user": ""}))
            return
        try:
            out = handle_turn(text)
            out["user"] = text
            self._send(200, json.dumps(out))
        except Exception as e:
            self._send(200, json.dumps({"reply": f"Something broke: {e}", "user": text}))


if __name__ == "__main__":
    print(f"Voice server on http://localhost:{PORT}  (project: {PROJECT_DIR}, model: {MODEL})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
