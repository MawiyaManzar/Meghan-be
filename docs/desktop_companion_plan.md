# Meghan Desktop Companion - Implementation Plan

## 1. Vision & Scope

Build a **desktop companion device** that:
- **Lives on your desk** with an animated character on a 5" screen
- **Listens and talks** via mic and speaker
- **Syncs with the mobile app** - same user, shared state, shared conversations
- **Shows visual feedback** - mood, listening state, hearts balance, animations

### Your Hardware
- **Raspberry Pi 5** (more powerful than Pi 4, great for UI)
- **5-inch LCD screen** (touchscreen?)
- **USB/I2S microphone**
- **Speaker** (USB or 3.5mm)

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DESKTOP COMPANION (Pi 5)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐    │
│   │  MICROPHONE │───▶│ AUDIO INPUT │───▶│   VOICE CONTROLLER      │    │
│   └─────────────┘    └─────────────┘    │   (Python)              │    │
│                                          │   - Record audio        │    │
│   ┌─────────────┐    ┌─────────────┐    │   - Call STT API        │    │
│   │   SPEAKER   │◀───│ AUDIO OUTPUT│◀───│   - Call Meghan API     │    │
│   └─────────────┘    └─────────────┘    │   - Call TTS API        │    │
│                                          │   - Play response       │    │
│                                          └───────────┬─────────────┘    │
│                                                      │                  │
│   ┌─────────────────────────────────────────────────┼─────────────┐    │
│   │                    UI APPLICATION               │              │    │
│   │                    (PyQt6 / Kivy)               ▼              │    │
│   │  ┌────────────────────────────────────────────────────────┐   │    │
│   │  │                 5" SCREEN DISPLAY                      │   │    │
│   │  │  ┌──────────────────────────────────────────────────┐  │   │    │
│   │  │  │                                                  │  │   │    │
│   │  │  │              ANIMATED COMPANION                  │  │   │    │
│   │  │  │                  (Meghan)                        │  │   │    │
│   │  │  │                                                  │  │   │    │
│   │  │  │         😊 / 😔 / 🎧 / 💭 / 💬                   │  │   │    │
│   │  │  │                                                  │  │   │    │
│   │  │  │   [Current Mood]  [Hearts: 150]  [Tier: Green]   │  │   │    │
│   │  │  │                                                  │  │   │    │
│   │  │  └──────────────────────────────────────────────────┘  │   │    │
│   │  │                                                        │   │    │
│   │  │  [ TAP TO TALK ]  or  [ "Hey Meghan" wake word ]       │   │    │
│   │  └────────────────────────────────────────────────────────┘   │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS / WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         MEGHAN BACKEND (Cloud)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────────────┐    │
│   │  /api/chat    │   │  /api/users   │   │  /api/communities/ws  │    │
│   │  - messages   │   │  - state      │   │  - realtime sync      │    │
│   │  - AI response│   │  - dashboard  │   │                       │    │
│   └───────────────┘   └───────────────┘   └───────────────────────┘    │
│                                                                         │
│                   ┌───────────────────────────┐                         │
│                   │   SAME USER ACCOUNT       │                         │
│                   │   (shared with mobile)    │                         │
│                   └───────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Same API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          MOBILE APP (Phone)                             │
├─────────────────────────────────────────────────────────────────────────┤
│   Same user, same state, same conversations, same hearts               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Software Stack (On Raspberry Pi 5)

### Core Technologies

| Component | Technology | Why |
|-----------|------------|-----|
| **OS** | Raspberry Pi OS (64-bit) | Native support, well-documented |
| **UI Framework** | **PyQt6** or **Kivy** | Hardware-accelerated, touch support |
| **Audio Recording** | PyAudio / sounddevice | Reliable audio capture |
| **Audio Playback** | pygame.mixer / sounddevice | Low-latency playback |
| **HTTP Client** | httpx (async) | Async API calls to backend |
| **STT** | Whisper API (OpenAI) or Google STT | High accuracy |
| **TTS** | ElevenLabs / Google TTS / Edge TTS | Natural voice |
| **Wake Word** | Porcupine (Picovoice) or Vosk | Local, low-latency detection |

### Recommended: PyQt6 for UI

PyQt6 is better for a desktop companion because:
- Hardware-accelerated rendering on Pi 5
- Native widgets and animations
- Better performance than web-based UIs
- Touch screen support built-in

---

## 4. Project Structure (Pi-side code)

```
meghan-companion/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── config.py                  # Settings (API URLs, tokens)
│
├── ui/                        # Screen UI
│   ├── __init__.py
│   ├── main_window.py         # Main PyQt6 window
│   ├── companion_widget.py    # Animated character widget
│   ├── status_bar.py          # Mood, hearts, tier display
│   ├── animations/            # Animation frames/assets
│   │   ├── idle.gif
│   │   ├── listening.gif
│   │   ├── thinking.gif
│   │   └── speaking.gif
│   └── styles.qss             # Qt stylesheet (like CSS)
│
├── voice/                     # Voice pipeline
│   ├── __init__.py
│   ├── recorder.py            # Microphone recording
│   ├── player.py              # Audio playback
│   ├── stt.py                 # Speech-to-Text client
│   ├── tts.py                 # Text-to-Speech client
│   └── wake_word.py           # Wake word detection
│
├── api/                       # Backend communication
│   ├── __init__.py
│   ├── client.py              # Meghan API client
│   ├── auth.py                # Token management
│   └── sync.py                # State sync with backend
│
├── state/                     # Local state management
│   ├── __init__.py
│   ├── user_state.py          # Current mood, tier, hearts
│   └── conversation.py        # Active conversation tracking
│
└── scripts/
    ├── setup.sh               # Initial Pi setup
    ├── start.sh               # Launch companion
    └── update.sh              # OTA update script
```

---

## 5. Implementation Phases

### Phase 1: Hardware Setup (Week 1)

**Goal:** Get the Pi 5 running with screen, mic, and speaker working.

#### Tasks:

1. **Flash Raspberry Pi OS (64-bit)**
   ```bash
   # Use Raspberry Pi Imager
   # Enable SSH, set Wi-Fi, set hostname: meghan-companion
   ```

2. **Configure 5" LCD Screen**
   ```bash
   # Most 5" screens work out of the box
   # For HDMI screens, add to /boot/config.txt:
   hdmi_group=2
   hdmi_mode=87
   hdmi_cvt=800 480 60 6 0 0 0
   hdmi_drive=2
   ```

3. **Setup Audio Devices**
   ```bash
   # List audio devices
   arecord -l  # Microphones
   aplay -l    # Speakers
   
   # Test recording
   arecord -D plughw:1,0 -f cd -t wav -d 5 test.wav
   
   # Test playback
   aplay test.wav
   ```

4. **Install Python Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pyqt6 python3-pip portaudio19-dev
   pip3 install pyaudio sounddevice httpx pygame
   ```

**Success Criteria:**
- [ ] Screen displays desktop
- [ ] Can record audio from mic
- [ ] Can play audio through speaker
- [ ] SSH access works

---

### Phase 2: Basic UI Application (Week 1-2)

**Goal:** Display an animated companion on screen with state indicators.

#### Main Window (`ui/main_window.py`)

```python
"""Main window for the Meghan Desktop Companion."""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie

class MeghanCompanion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meghan")
        self.setFixedSize(800, 480)  # 5" screen resolution
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Fullscreen kiosk
        
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Animated companion (GIF)
        self.companion_label = QLabel()
        self.companion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_animation("idle")
        layout.addWidget(self.companion_label)
        
        # Status display
        self.status_label = QLabel("Mood: Grounded | Hearts: 150 | Tier: Green")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 18px;")
        layout.addWidget(self.status_label)
        
        # Instruction
        self.instruction_label = QLabel("Tap screen or say 'Hey Meghan' to talk")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(self.instruction_label)
        
        # Dark theme
        self.setStyleSheet("background-color: #1a1a2e;")
    
    def set_animation(self, state: str):
        """Change companion animation: idle, listening, thinking, speaking."""
        animation_map = {
            "idle": "ui/animations/idle.gif",
            "listening": "ui/animations/listening.gif",
            "thinking": "ui/animations/thinking.gif",
            "speaking": "ui/animations/speaking.gif",
        }
        movie = QMovie(animation_map.get(state, animation_map["idle"]))
        movie.setScaledSize(self.companion_label.size())
        self.companion_label.setMovie(movie)
        movie.start()
    
    def update_status(self, mood: str, hearts: int, tier: str):
        """Update status bar with current user state."""
        self.status_label.setText(f"Mood: {mood} | Hearts: {hearts} | Tier: {tier}")
    
    def mousePressEvent(self, event):
        """Handle tap to start listening."""
        self.start_listening()
    
    def start_listening(self):
        """Begin recording user's voice."""
        self.set_animation("listening")
        self.instruction_label.setText("Listening...")
        # Trigger voice recording (connect to voice controller)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeghanCompanion()
    window.showFullScreen()
    sys.exit(app.exec())
```

**Success Criteria:**
- [ ] Fullscreen UI displays on 5" screen
- [ ] Animated character shows on screen
- [ ] Tap-to-talk triggers listening state
- [ ] Status bar shows mood/hearts/tier

---

### Phase 3: Voice Pipeline (Week 2-3)

**Goal:** Record → STT → Backend → TTS → Play

#### Voice Controller (`voice/controller.py`)

```python
"""Voice pipeline controller."""
import asyncio
import sounddevice as sd
import numpy as np
from voice.stt import transcribe_audio
from voice.tts import synthesize_speech
from api.client import MeghanClient

class VoiceController:
    def __init__(self, api_client: MeghanClient, on_state_change=None):
        self.client = api_client
        self.on_state_change = on_state_change  # Callback to update UI
        self.sample_rate = 16000
        self.recording = False
        
    def notify(self, state: str, message: str = ""):
        """Notify UI of state change."""
        if self.on_state_change:
            self.on_state_change(state, message)
    
    async def listen_and_respond(self):
        """Full conversation cycle."""
        try:
            # 1. LISTENING - Record audio
            self.notify("listening", "Listening...")
            audio_data = await self.record_audio(duration=5)
            
            # 2. THINKING - Transcribe with STT
            self.notify("thinking", "Understanding...")
            user_text = await transcribe_audio(audio_data, self.sample_rate)
            
            if not user_text.strip():
                self.notify("idle", "I didn't catch that. Try again?")
                return
            
            # 3. THINKING - Get response from Meghan backend
            self.notify("thinking", "Thinking...")
            response = await self.client.send_message(user_text)
            
            # 4. SPEAKING - Synthesize and play response
            self.notify("speaking", response.content)
            audio_response = await synthesize_speech(response.content)
            await self.play_audio(audio_response)
            
            # 5. Return to idle
            self.notify("idle", "")
            
        except Exception as e:
            self.notify("idle", f"Oops, something went wrong: {e}")
    
    async def record_audio(self, duration: float = 5) -> np.ndarray:
        """Record audio from microphone."""
        frames = int(duration * self.sample_rate)
        audio = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype='int16')
        sd.wait()
        return audio.flatten()
    
    async def play_audio(self, audio_data: bytes):
        """Play audio through speaker."""
        # Using pygame for playback
        import pygame
        import io
        pygame.mixer.init()
        pygame.mixer.music.load(io.BytesIO(audio_data))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
```

#### STT Client (`voice/stt.py`) - Using OpenAI Whisper

```python
"""Speech-to-Text using OpenAI Whisper API."""
import httpx
import io
import wave
import numpy as np

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

async def transcribe_audio(audio_data: np.ndarray, sample_rate: int) -> str:
    """Transcribe audio using Whisper API."""
    # Convert numpy array to WAV bytes
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())
    wav_buffer.seek(0)
    
    # Call Whisper API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WHISPER_API_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"file": ("audio.wav", wav_buffer, "audio/wav")},
            data={"model": "whisper-1"}
        )
        response.raise_for_status()
        return response.json()["text"]
```

#### TTS Client (`voice/tts.py`) - Using Edge TTS (Free!)

```python
"""Text-to-Speech using Edge TTS (free, high quality)."""
import edge_tts
import asyncio

async def synthesize_speech(text: str, voice: str = "en-US-AriaNeural") -> bytes:
    """Convert text to speech using Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data
```

**Success Criteria:**
- [ ] Tap screen → records voice → transcribes text
- [ ] Text sent to Meghan backend → gets AI response
- [ ] Response spoken back through speaker
- [ ] UI shows listening/thinking/speaking states

---

### Phase 4: Backend Integration & Sync (Week 3-4)

**Goal:** Connect to Meghan backend with same user account as mobile app.

#### API Client (`api/client.py`)

```python
"""Meghan Backend API Client."""
import httpx
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatResponse:
    content: str
    success: bool
    error: Optional[str] = None

@dataclass
class UserState:
    mood: str
    tier: str
    hearts: int
    source: str

class MeghanClient:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip("/")
        self.token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.conversation_id: Optional[int] = None
    
    async def get_user_state(self) -> UserState:
        """Fetch current user state from backend."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/users/me/state",
                headers=self.headers
            )
            resp.raise_for_status()
            data = resp.json()
            return UserState(
                mood=data.get("mood", "Grounded"),
                tier=data.get("tier", "Green"),
                hearts=data.get("xp", 0),  # Map XP to hearts
                source=data.get("source", "Others")
            )
    
    async def create_conversation(self, mode: str = "talk") -> int:
        """Create a new conversation."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/chat/conversations",
                headers=self.headers,
                json={"mode": mode}
            )
            resp.raise_for_status()
            self.conversation_id = resp.json()["id"]
            return self.conversation_id
    
    async def send_message(self, content: str) -> ChatResponse:
        """Send message and get AI response."""
        if not self.conversation_id:
            await self.create_conversation()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat/conversations/{self.conversation_id}/messages",
                headers=self.headers,
                json={"content": content, "role": "user"}
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Get AI response from the response
            ai_message = data.get("ai_response", {})
            return ChatResponse(
                content=ai_message.get("content", "I'm here for you."),
                success=True
            )
    
    async def get_dashboard(self) -> dict:
        """Get full dashboard data for display."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/users/me/dashboard",
                headers=self.headers
            )
            resp.raise_for_status()
            return resp.json()
```

#### Device Authentication Flow

Two options for logging in:

**Option A: QR Code Login (Recommended)**
1. Mobile app generates a QR code with temporary token
2. Desktop companion scans QR with camera (or display QR on phone)
3. Companion exchanges temp token for access token
4. Same user on both devices!

**Option B: Device Pairing Code**
1. Companion displays 6-digit code
2. User enters code in mobile app settings
3. Backend links device to user account

#### Real-time Sync (`api/sync.py`)

```python
"""Real-time sync with backend via WebSocket."""
import asyncio
import json
import websockets

class StateSync:
    def __init__(self, ws_url: str, token: str, on_update=None):
        self.ws_url = ws_url
        self.token = token
        self.on_update = on_update
    
    async def connect(self):
        """Connect to backend WebSocket for real-time updates."""
        uri = f"{self.ws_url}/api/device/sync?token={self.token}"
        
        async with websockets.connect(uri) as ws:
            while True:
                try:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    if data["type"] == "state_update":
                        # User state changed (from mobile app)
                        if self.on_update:
                            self.on_update(data["payload"])
                    
                    elif data["type"] == "hearts_update":
                        # Hearts balance changed
                        if self.on_update:
                            self.on_update({"hearts": data["hearts"]})
                            
                except websockets.ConnectionClosed:
                    # Reconnect after 5 seconds
                    await asyncio.sleep(5)
                    await self.connect()
```

**Success Criteria:**
- [ ] Companion logs in with same user as mobile app
- [ ] Conversations appear in both devices
- [ ] Hearts earned on companion show in app
- [ ] State changes sync in real-time

---

### Phase 5: Wake Word & Polish (Week 4-5)

**Goal:** Add "Hey Meghan" wake word and polish the experience.

#### Wake Word Detection (`voice/wake_word.py`)

Using Picovoice Porcupine (free tier: 3 custom wake words):

```python
"""Wake word detection using Porcupine."""
import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, access_key: str, on_wake=None):
        self.on_wake = on_wake
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=["meghan_raspberry-pi.ppn"]  # Custom wake word
        )
        self.pa = pyaudio.PyAudio()
        self.stream = None
    
    def start(self):
        """Start listening for wake word."""
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        
        print("Listening for 'Hey Meghan'...")
        
        while True:
            pcm = self.stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            
            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                if self.on_wake:
                    self.on_wake()
    
    def stop(self):
        if self.stream:
            self.stream.close()
        self.porcupine.delete()
```

**Alternative: Free wake word with Vosk**

```python
"""Free wake word detection using Vosk."""
import vosk
import pyaudio
import json

class VoskWakeWord:
    def __init__(self, model_path: str, wake_phrase: str = "hey meghan"):
        self.model = vosk.Model(model_path)
        self.wake_phrase = wake_phrase.lower()
        
    def listen_for_wake(self, on_wake):
        rec = vosk.KaldiRecognizer(self.model, 16000)
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1,
                         rate=16000, input=True, frames_per_buffer=8000)
        
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                if self.wake_phrase in text:
                    on_wake()
```

---

## 6. Backend Changes Required

### New Endpoint: Device Registration

Add to your backend for device pairing:

```python
# app/routers/devices.py

@router.post("/api/devices/register")
async def register_device(
    device_info: DeviceRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a companion device for the user."""
    device = Device(
        user_id=current_user.id,
        device_type="desktop_companion",
        device_name=device_info.name,
        last_seen=datetime.utcnow()
    )
    db.add(device)
    db.commit()
    return {"device_id": device.id, "status": "registered"}


@router.websocket("/api/device/sync")
async def device_sync_ws(websocket: WebSocket, token: str):
    """WebSocket for real-time sync between devices."""
    # Authenticate
    user = authenticate_token(token)
    await websocket.accept()
    
    # Add to user's device connections
    connections[user.id].add(websocket)
    
    try:
        while True:
            # Receive heartbeat or sync requests
            data = await websocket.receive_json()
            # Handle sync logic
    finally:
        connections[user.id].discard(websocket)
```

### Modify Chat Endpoint for Device Source

```python
# In chat router, add device_type field
class MessageCreate(BaseModel):
    content: str
    role: str = "user"
    device_type: str = "mobile"  # "mobile" or "desktop_companion"
```

---

## 7. Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CONVERSATION FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. USER says "Hey Meghan" or TAPS screen                               │
│          │                                                              │
│          ▼                                                              │
│  2. UI → LISTENING state (animation changes)                            │
│          │                                                              │
│          ▼                                                              │
│  3. RECORD 5 seconds of audio                                           │
│          │                                                              │
│          ▼                                                              │
│  4. UI → THINKING state                                                 │
│          │                                                              │
│          ▼                                                              │
│  5. SEND audio to Whisper STT → get text                                │
│          │                                                              │
│          ▼                                                              │
│  6. SEND text to Meghan /api/chat/messages → get AI response            │
│          │                                                              │
│          ▼                                                              │
│  7. UI → SPEAKING state                                                 │
│          │                                                              │
│          ▼                                                              │
│  8. SEND response to Edge TTS → get audio                               │
│          │                                                              │
│          ▼                                                              │
│  9. PLAY audio through speaker                                          │
│          │                                                              │
│          ▼                                                              │
│  10. UI → IDLE state (back to listening for wake word)                  │
│                                                                         │
│  Meanwhile: WebSocket keeps state synced with mobile app                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Cost Breakdown (Updated for Desktop Companion)

### Hardware (You Already Have)
- Raspberry Pi 5: ✅ Already have
- 5" Screen: ✅ Already have
- Mic: ✅ Already have
- Speaker: ✅ Already have

### Cloud APIs (Monthly)

| Service | Provider | Cost |
|---------|----------|------|
| **STT** | OpenAI Whisper | ~$0.006/min → ~$3-10/mo |
| **TTS** | Edge TTS | **FREE** |
| **LLM** | Gemini (existing) | Already included |
| **Wake Word** | Picovoice (free tier) | **FREE** (3 wake words) |
| **Backend** | Your existing hosting | Already included |

**Estimated Monthly: $3-15** (mainly STT)

### Free Alternatives
- STT: Vosk (offline, free, less accurate)
- TTS: Edge TTS (free, excellent quality)
- Wake Word: Vosk (free, less reliable)

---

## 9. Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | Week 1 | Hardware working (screen, mic, speaker) |
| **Phase 2** | Week 1-2 | Basic UI with animated companion |
| **Phase 3** | Week 2-3 | Voice pipeline (STT → Backend → TTS) |
| **Phase 4** | Week 3-4 | Backend sync, same user as mobile |
| **Phase 5** | Week 4-5 | Wake word, polish, testing |

**Total: 4-5 weeks for MVP**

---

## 10. Quick Start Commands

```bash
# SSH into Pi
ssh pi@meghan-companion.local

# Clone project
git clone https://github.com/your-repo/meghan-companion.git
cd meghan-companion

# Install dependencies
pip3 install -r requirements.txt

# Configure
cp config.example.py config.py
# Edit config.py with your API keys and backend URL

# Run
python3 main.py
```

---

## 11. Questions to Decide

Before starting implementation:

1. **Wake word or tap-only?**
   - Wake word needs Picovoice account or Vosk setup
   - Tap-only is simpler for MVP

2. **Device authentication method?**
   - QR code scan (needs Pi camera)
   - Pairing code (simpler)
   - Manual token entry (simplest but worst UX)

3. **Screen touchscreen or display-only?**
   - Touchscreen: tap to talk
   - Display-only: button to talk, or wake word only

4. **Companion character design?**
   - Simple animated GIFs
   - Lottie animations (smoother)
   - Custom character design needed

---

## Next Steps

1. ✅ Read and confirm this plan
2. Set up Pi 5 with OS and test hardware
3. Create basic UI prototype
4. Implement voice pipeline
5. Connect to Meghan backend
6. Add sync and polish
