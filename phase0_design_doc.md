# Phase 0: Design Document - Alexa-like Voice Assistant for Meghan

## 1. Technical Decisions

### 1.1 Device Platform
**Decision: Raspberry Pi 4 (4GB RAM)**

**Rationale:**
- Mature ecosystem with extensive Python libraries for audio processing
- Good balance of cost, performance, and community support
- Sufficient processing power for local audio capture/playback and network operations
- Easy GPIO access for button/LED integration
- Well-documented audio setup (USB mics, I2S audio hats)
- Alternative considered: ESP32 + Linux host (more complex, less flexible)

**Specifications:**
- Model: Raspberry Pi 4 Model B (4GB)
- OS: Raspberry Pi OS (Debian-based, 64-bit)
- Storage: 32GB+ microSD card (Class 10 or better)

### 1.2 Speech-to-Text (STT) Provider
**Decision: Google Cloud Speech-to-Text API**

**Rationale:**
- High accuracy for conversational speech
- Good latency for real-time use cases
- Competitive pricing (~$1-3 per 1000 minutes)
- Well-documented Python SDK
- Supports streaming recognition (useful for future enhancements)
- Alternative considered: OpenAI Whisper API (excellent quality but higher cost, slower for real-time)

**Configuration:**
- Language: English (en-US)
- Model: `default` (or `phone_call` for better noise handling)
- Encoding: LINEAR16 (16-bit PCM)
- Sample rate: 16000 Hz
- Single utterance mode (press-to-talk)

### 1.3 Text-to-Speech (TTS) Provider
**Decision: Google Cloud Text-to-Speech API**

**Rationale:**
- Natural-sounding voices with good emotional range
- Consistent with STT provider (single vendor, simpler auth)
- Reasonable pricing (~$4 per 1M characters)
- Multiple voice options (can choose warm, friendly voice matching Meghan's personality)
- SSML support for prosody control
- Alternative considered: ElevenLabs (excellent quality but more expensive, Amazon Polly (good but separate AWS account needed)

**Configuration:**
- Voice: `en-US-Neural2-F` (warm, friendly female voice) or `en-US-Journey-F`
- Audio encoding: MP3 or LINEAR16
- Sample rate: 24000 Hz
- SSML: Enabled for natural pauses and emphasis

### 1.4 Interaction Mode
**Decision: Press-to-Talk Button**

**Rationale:**
- Simpler implementation (no wake word detection model needed)
- Lower latency (no continuous listening)
- Better privacy (only records when user explicitly presses)
- Lower power consumption
- More reliable for MVP (wake word detection requires training/tuning)
- Future enhancement: Can add wake word detection later if desired

**Hardware:**
- Tactile button connected to GPIO pin
- LED indicator for visual feedback (listening/processing/speaking states)

---

## 2. System Architecture

### 2.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Assistant Device                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Hardware   │  │   Audio      │  │   Client     │     │
│  │   Layer      │  │   Pipeline   │  │   Service    │     │
│  │              │  │              │  │              │     │
│  │ - Button     │  │ - Capture    │  │ - STT API    │     │
│  │ - LED        │  │ - Playback   │  │ - Backend    │     │
│  │ - Mic        │  │ - Format     │  │ - TTS API    │     │
│  │ - Speaker    │  │   Conversion │  │ - State Mgmt │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / Wi-Fi
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Services                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Google     │  │   Meghan     │  │   Google     │     │
│  │   Cloud STT  │  │   Backend    │  │   Cloud TTS  │     │
│  │              │  │              │  │              │     │
│  │ - Audio →    │  │ - Chat API   │  │ - Text →     │     │
│  │   Text       │  │ - Auth       │  │   Audio      │     │
│  │              │  │ - User State │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Details

#### 2.2.1 Hardware Layer
- **Raspberry Pi 4**: Main compute unit
- **USB Microphone**: Audio input (e.g., USB condenser mic)
- **Speaker**: Audio output (USB speaker or 3.5mm jack + amplifier)
- **GPIO Button**: User interaction trigger
- **Status LED**: Visual feedback (RGB LED or simple LED)

#### 2.2.2 Audio Pipeline
- **Audio Capture**: `pyaudio` or `sounddevice` library
- **Format Conversion**: `pydub` for audio format handling
- **Playback**: `pyaudio` or `pygame` for audio output
- **Noise Reduction**: Optional local preprocessing (can be added later)

#### 2.2.3 Client Service
- **STT Client**: Google Cloud Speech-to-Text Python SDK
- **Backend Client**: HTTP client (requests/httpx) for Meghan API
- **TTS Client**: Google Cloud Text-to-Speech Python SDK
- **State Manager**: Local state storage (JSON file) for device ID, auth token, user context

---

## 3. Data Flow

### 3.1 Complete Conversation Flow

```
User presses button
    │
    ▼
[LED: BLUE (Listening)]
    │
    ▼
Record audio (3-10 seconds, or until button release)
    │
    ▼
[LED: YELLOW (Processing)]
    │
    ▼
Convert audio to WAV/FLAC format
    │
    ▼
Send audio to Google Cloud STT API
    │
    │ POST /v1/speech:recognize
    │ Body: { audio: { content: base64_audio }, config: {...} }
    │
    ▼
Receive transcript text
    │
    ▼
Authenticate with Meghan backend (JWT token)
    │
    │ GET /api/auth/me (if token exists)
    │ OR
    │ POST /api/auth/login-json (if no token)
    │
    ▼
Send message to Meghan chat API
    │
    │ POST /api/chat/conversations/{conversation_id}/messages
    │ Body: { content: transcript_text, mode: "talk" }
    │ Headers: Authorization: Bearer <token>
    │
    ▼
Receive AI response text
    │
    ▼
Send text to Google Cloud TTS API
    │
    │ POST /v1/text:synthesize
    │ Body: { input: { text: response_text }, voice: {...}, audioConfig: {...} }
    │
    ▼
Receive audio bytes (MP3 or LINEAR16)
    │
    ▼
[LED: GREEN (Speaking)]
    │
    ▼
Play audio on speaker
    │
    ▼
[LED: OFF (Idle)]
    │
    ▼
Ready for next interaction
```

### 3.2 Error Handling Flow

```
If STT fails:
    → Play error sound: "I didn't catch that, can you repeat?"
    → Return to idle state

If Backend API fails (401):
    → Prompt user to re-authenticate (via web interface or device config)
    → Store error, retry on next interaction

If Backend API fails (network/timeout):
    → Play error sound: "I'm having trouble connecting, please try again"
    → Retry up to 2 times with exponential backoff

If TTS fails:
    → Fallback: Use local TTS (espeak/pyttsx3) with degraded quality
    → Log error for debugging
```

---

## 4. API Integration Details

### 4.1 Google Cloud STT API

**Endpoint:** `https://speech.googleapis.com/v1/speech:recognize`

**Request Format:**
```json
{
  "config": {
    "encoding": "LINEAR16",
    "sampleRateHertz": 16000,
    "languageCode": "en-US",
    "model": "default",
    "enableAutomaticPunctuation": true
  },
  "audio": {
    "content": "<base64_encoded_audio>"
  }
}
```

**Response Format:**
```json
{
  "results": [
    {
      "alternatives": [
        {
          "transcript": "Hello Meghan, how are you?",
          "confidence": 0.95
        }
      ]
    }
  ]
}
```

### 4.2 Meghan Backend API

**Authentication:**
- Device stores JWT token locally (encrypted file)
- Token obtained via initial setup: user logs in via web interface, token copied to device config
- Token refresh: If 401, device prompts for re-authentication

**Chat Endpoint:**
```
POST /api/chat/conversations/{conversation_id}/messages
Headers:
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
Body:
{
  "content": "User's transcribed text",
  "mode": "talk"  // or "plan" if we add mode switching
}
```

**Response:**
```json
{
  "id": "msg_123",
  "conversation_id": "conv_456",
  "role": "assistant",
  "content": "AI response text here",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Conversation Management:**
- Device creates one conversation per user session (or reuses last conversation)
- Conversation ID stored locally for continuity

### 4.3 Google Cloud TTS API

**Endpoint:** `https://texttospeech.googleapis.com/v1/text:synthesize`

**Request Format:**
```json
{
  "input": {
    "text": "Hello! I'm here to help you."
  },
  "voice": {
    "languageCode": "en-US",
    "name": "en-US-Neural2-F",
    "ssmlGender": "FEMALE"
  },
  "audioConfig": {
    "audioEncoding": "MP3",
    "sampleRateHertz": 24000,
    "speakingRate": 1.0,
    "pitch": 0.0
  }
}
```

**Response Format:**
```json
{
  "audioContent": "<base64_encoded_mp3_audio>"
}
```

---

## 5. Device State Management

### 5.1 Local Storage Structure

**File:** `/home/pi/meghan_device/config.json` (encrypted or permissions-restricted)

```json
{
  "device_id": "meghan_device_001",
  "user_id": 123,
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_expires_at": "2024-02-15T10:00:00Z",
  "conversation_id": "conv_456",
  "last_sync": "2024-01-15T09:00:00Z",
  "user_context": {
    "name": "Alex",
    "mood": "anxious",
    "risk_tier": "medium"
  }
}
```

### 5.2 State Synchronization

- On startup: Fetch user state from `/api/users/me/state` to update local context
- After each interaction: Optionally sync user state if mood/tier changed
- Token refresh: Check token expiry, refresh if needed (or prompt re-auth)

---

## 6. Hardware Integration

### 6.1 GPIO Pin Assignment

- **Button**: GPIO 18 (with pull-up resistor)
- **LED Red**: GPIO 23 (for errors)
- **LED Green**: GPIO 24 (for speaking)
- **LED Blue**: GPIO 25 (for listening/processing)

### 6.2 Button Behavior

- **Short press (< 1s)**: Start recording, continue until button release
- **Long press (> 3s)**: Cancel current operation, return to idle
- **Double press**: Future: Switch conversation mode (talk/plan)

### 6.3 LED States

- **OFF**: Idle, ready for input
- **BLUE (solid)**: Listening/recording
- **YELLOW (solid)**: Processing (STT → Backend → TTS)
- **GREEN (solid)**: Speaking/playing audio
- **RED (blinking)**: Error state
- **BLUE (blinking)**: Wi-Fi disconnected, retrying

---

## 7. Security Considerations

### 7.1 Authentication
- JWT tokens stored in encrypted file (`config.json` with 600 permissions)
- Token never logged or exposed in error messages
- Token refresh handled gracefully

### 7.2 Network Security
- All API calls over HTTPS
- Device certificate validation enabled
- Wi-Fi credentials stored securely (wpa_supplicant)

### 7.3 Privacy
- Audio recordings not stored locally (only sent to STT API)
- Transcripts optionally logged for debugging (can be disabled)
- User can request device reset (clears all local data)

---

## 8. Deployment & Operations

### 8.1 Initial Setup Script
- Wi-Fi configuration
- Google Cloud credentials setup (service account JSON)
- Meghan backend authentication (web-based token copy)
- Audio device testing
- Systemd service installation

### 8.2 Systemd Service
- Service name: `meghan-voice-assistant.service`
- Auto-start on boot
- Restart on failure
- Logs to `/var/log/meghan/assistant.log`

### 8.3 Health Monitoring
- Periodic health check: Ping backend API
- Wi-Fi connectivity check
- Audio device availability check
- Log rotation and cleanup

---

## 9. Future Enhancements (Post-MVP)

- Wake word detection (e.g., "Hey Meghan")
- Multi-turn conversation context
- Voice activity detection (VAD) for automatic recording start/stop
- Local audio preprocessing (noise reduction, echo cancellation)
- OTA updates mechanism
- Multiple user profiles per device
- Offline mode with local LLM (if device resources allow)

---

## 10. Dependencies & Libraries

### Python Libraries
- `google-cloud-speech` - STT API client
- `google-cloud-texttospeech` - TTS API client
- `requests` or `httpx` - HTTP client for Meghan backend
- `pyaudio` or `sounddevice` - Audio capture/playback
- `pydub` - Audio format conversion
- `RPi.GPIO` - GPIO control for button/LED
- `cryptography` - Token encryption (optional)

### System Packages
- `python3-pip`
- `portaudio19-dev` (for pyaudio)
- `ffmpeg` (for audio conversion)
- `alsa-utils` (for audio device management)

---

## 11. Testing Strategy

### Unit Tests
- Audio format conversion
- API client wrappers (mocked)
- State management functions

### Integration Tests
- End-to-end flow: Button press → STT → Backend → TTS → Playback
- Error handling scenarios
- Token refresh flow

### Manual Testing
- Real-world audio quality testing
- Network failure scenarios
- Multi-user testing
- Long-running stability (24+ hours)

---

## 12. Success Criteria

- Device successfully records audio when button pressed
- Audio transcribed accurately (>90% accuracy for clear speech)
- Backend API integration works (chat messages sent/received)
- TTS audio plays clearly on speaker
- Complete conversation loop works end-to-end
- Error handling graceful (no crashes, clear user feedback)
- Device stable for 24+ hours continuous operation
- Setup process documented and repeatable
