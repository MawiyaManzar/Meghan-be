## Minimal Alexa-like Voice Assistant (IoT Device) – Implementation, Timeline, and Cost

### 1. Goal & Scope

Build a **minimal physical “Alexa-like” talking assistant** that:
- **Listens** to the user via a microphone.
- **Sends audio/text to your existing Meghan backend** (FastAPI + LLM).
- **Speaks back** the response via a speaker.
- Uses **simple wake-up interaction** (button/tap or basic hotword), not full smart-speaker feature parity.

Assume:
- You already have the Meghan backend running with chat endpoints.
- Internet connectivity is via Wi‑Fi.
- 1–2 prototype devices initially (not mass production).

---

### 2. High-level Architecture

- **Hardware Device**
  - Board: Raspberry Pi 4 (or similar SBC) *or* ESP32 + small Linux host.
  - Peripherals: USB microphone (or mic hat), speaker, status LED.
  - Local software:
    - Audio capture & playback.
    - Optional wake word or “press-to-talk” button.
    - Client that calls:
      - Speech-to-Text (STT) API → text.
      - Meghan backend chat API → response text.
      - Text-to-Speech (TTS) API → audio.

- **Cloud / Backend**
  - **Existing** Meghan backend:
    - Auth + chat endpoints already implemented.
  - **Additional small services** (if needed):
    - STT/TTS integration service (could be integrated into existing backend or called directly from device).

---

### 3. Implementation Phases (MVP)

#### Phase 0 – Requirements & Technical Choices (0.5 week, 4 people in short bursts)
- **Decisions:**
  - Device platform (Raspberry Pi vs alternatives).
  - STT provider (e.g., Google Cloud STT, Whisper API, etc.).
  - TTS provider (e.g., Google Cloud TTS, Amazon Polly, ElevenLabs, etc.).
  - Interaction mode: press-to-talk button vs wake word.
- **Deliverables:**
  - Short design doc (components, APIs, data flow).
  - Confirmed bill of materials (BOM) and providers.

#### Phase 1 – Hardware & OS Setup (1–1.5 weeks)
- Set up SBC (e.g., Pi OS), Wi‑Fi, SSH.
- Integrate microphone and speaker; verify recording and playback.
- Basic device health monitoring (CPU, disk, connectivity).
- **Deliverable:** Device that can record and play back local audio clips.

#### Phase 2 – Voice Pipeline Prototype (STT → Backend → TTS) (1.5–2 weeks)
- Implement a **Python client** on the device:
  - Record audio when button is pressed (or for fixed duration).
  - Send audio to STT API, get back text.
  - Call Meghan backend chat endpoint with that text and device/user ID.
  - Receive text response.
  - Call TTS API to synthesize speech.
  - Play synthesized audio on the speaker.
- Simple logs on device for debugging.
- **Deliverable:** End-to-end **voice conversation loop** working from one device.

#### Phase 3 – Integration with Meghan User Model & Basic UX (1–1.5 weeks)
- Link device sessions to Meghan users (e.g., via token or per-device secret).
- Ensure risk tier, mood, and state are passed or inferred as needed.
- Add simple UX affordances:
  - LED on while listening / thinking / speaking.
  - Basic error prompts (e.g., “I didn’t catch that, can you repeat?”).
- **Deliverable:** Device talks to Meghan as a proper user, with basic feedback and resilience.

#### Phase 4 – Hardening, Testing, and Polish (1–2 weeks)
- Stabilize:
  - Auto-reconnect on Wi‑Fi drop.
  - Graceful handling of STT/TTS/backend timeouts.
  - Log aggregation (e.g., sending logs or metrics to a server).
- Add simple OTA update mechanism or at least scripted update flow (git pull + systemd service restart).
- Write basic documentation and scripts for re‑flashing a new device.
- **Deliverable:** Prototype ready for pilot testing with a small group of users.

---

### 4. Timeline Estimate (4 People)

Assuming **4 people**, each at ~20–30 hours/week on this effort, and moderate prior experience:

- **Conservative MVP total:** **5–7 weeks** calendar time.
  - Phase 0: 0.5 week (part-time).
  - Phase 1: 1–1.5 weeks.
  - Phase 2: 1.5–2 weeks.
  - Phase 3: 1–1.5 weeks.
  - Phase 4: 1–2 weeks (in parallel with pilot).

If everyone is experienced with IoT, Linux, and cloud APIs, you might push this down to **3–4 very focused weeks**, but 5–7 weeks is a safer expectation for a robust MVP.

---

### 5. Work Division for 4 People

- **Person A – Hardware & Embedded Lead**
  - Select board, mic, speaker, and enclosure.
  - Flash OS, set up audio drivers.
  - Implement device-level scripts/services (systemd, startup, health checks).
  - Owns physical build and deployment scripts.

- **Person B – Voice Pipeline (STT/TTS) Engineer**
  - Evaluate and integrate STT & TTS providers.
  - Implement audio capture pipeline and HTTP/gRPC calls to STT/TTS.
  - Optimize latency and audio quality.
  - Work closely with Person A on device constraints.

- **Person C – Backend & Integration Engineer**
  - Extend or adapt Meghan backend to cleanly support voice clients (if needed).
  - Define API payloads for device → backend (metadata, device ID, user mapping).
  - Implement any glue logic for STT/TTS on server side if you centralize it.
  - Add logging, metrics, and minimal dashboards for monitoring device usage.

- **Person D – Product, UX, and QA**
  - Define interaction flows, prompts, and personality details for voice.
  - Specify UX for LEDs, button interactions, and error messages.
  - Write test scenarios; run manual and small-user testing.
  - Owns documentation (how to use the device, known issues, setup guide).

You can of course rotate responsibilities, but this split reduces context switching.

---

### 6. Cost Estimate (Prototype Stage)

#### 6.1 Hardware Costs (per device, approximate)

- **Raspberry Pi 4 (4GB)**: **$70–$120** (depending on supply/pricing in your region).
- **USB microphone or mic HAT**: **$15–$40**.
- **Speaker (small powered speaker or amplifier + driver)**: **$20–$50**.
- **LEDs, button, cables, power supply, case/enclosure**: **$30–$60**.

**Per-device total (prototype):** roughly **$135–$270**.

For **2 prototype units**, budget **$300–$500** to allow for spares and experiments.

#### 6.2 Cloud & API Costs (per month, development stage)

Rough ballpark, assuming **small pilot usage**:

- **STT**:
  - Google Cloud STT or similar: often on the order of **$1–$3 per 1,000 minutes** (very rough; check current pricing).
  - For a few thousand minutes/month in testing: **$10–$30/mo**.

- **TTS**:
  - Similar order of magnitude: **$10–$40/mo** for light pilot usage.

- **Meghan LLM backend (Gemini)**:
  - Already part of your existing costs. For incremental pilot traffic, maybe **$20–$60/mo** extra depending on usage and model pricing.

- **Misc Cloud (logging, monitoring, storage)**:
  - **$10–$30/mo** if using low-cost tiers (e.g., basic metrics and logs).

**Total recurring cloud estimate (pilot):** around **$50–$150/month**.

#### 6.3 One-time and Miscellaneous Costs

- Developer labor is usually the main cost; ignoring salaries, you might add:
  - **$50–$150** for cables, spare parts, tools (soldering iron, etc., if not already owned).
  - Optional **3D-printed or custom enclosure**: **$50–$100** per design run.

---

### 7. Summary

- With 4 people, a **minimal Alexa-like Meghan device** is feasible in about **5–7 weeks** of focused work.
- **Upfront hardware cost** for a couple of prototypes is on the order of **$300–$500**.
- **Monthly cloud cost** for a small pilot is roughly **$50–$150**, depending on STT/TTS and LLM usage.
- Clear division of responsibilities (hardware, voice pipeline, backend integration, UX/QA) will help you move in parallel and keep the scope contained to an MVP that reliably records, talks to Meghan, and speaks back.


