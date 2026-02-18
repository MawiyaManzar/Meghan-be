# Phase 0: Bill of Materials (BOM) and Provider Confirmation

## 1. Hardware Components

### 1.1 Core Computing Unit

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| Raspberry Pi 4 Model B | 4GB RAM | 1 | $75 | $75 | Raspberry Pi Official Store / Adafruit / SparkFun | Primary compute unit |
| MicroSD Card | 32GB Class 10 (SanDisk Ultra or equivalent) | 1 | $8 | $8 | Amazon / Adafruit | OS and application storage |
| Power Supply | Official Raspberry Pi 5V 3A USB-C Power Supply | 1 | $10 | $10 | Raspberry Pi Official Store | Reliable power delivery |
| **Subtotal** | | | | **$93** | | |

### 1.2 Audio Components

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| USB Microphone | Blue Snowball iCE or Logitech USB Desktop Mic | 1 | $35 | $35 | Amazon / Best Buy | Good quality, plug-and-play |
| Speaker | USB Powered Speaker (Logitech S120 or similar) | 1 | $15 | $15 | Amazon / Best Buy | Simple USB-powered option |
| **Alternative: Audio HAT** | ReSpeaker 2-Mics Pi HAT (optional) | 0-1 | $25 | $0-25 | Seeed Studio | If preferring HAT form factor |
| **Subtotal** | | | | **$50** | | |

### 1.3 User Interface Components

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| Tactile Button | 12mm Tactile Push Button (momentary) | 1 | $1 | $1 | Adafruit / SparkFun / Amazon | User interaction trigger |
| RGB LED | Common Cathode RGB LED (or 3 separate LEDs) | 1 | $2 | $2 | Adafruit / SparkFun | Status indicator |
| Resistors | 220Ω resistors (for LED) | 3 | $0.10 | $0.30 | Adafruit / SparkFun | Current limiting |
| Pull-up Resistor | 10kΩ resistor (for button) | 1 | $0.10 | $0.10 | Adafruit / SparkFun | Button pull-up |
| Jumper Wires | Male-to-Female jumper wires (assorted) | 1 pack | $5 | $5 | Adafruit / Amazon | GPIO connections |
| **Subtotal** | | | | **$8.40** | | |

### 1.4 Enclosure & Cables

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| Case/Enclosure | Raspberry Pi 4 Case (with ventilation) | 1 | $10 | $10 | Adafruit / Amazon | Basic protective case |
| USB Cable (Type-A to Micro-B) | For microphone connection | 1 | $3 | $3 | Amazon | If mic uses Micro-B |
| USB Extension Cable | 6ft USB-A extension (if needed) | 1 | $5 | $5 | Amazon | For flexible mic placement |
| **Subtotal** | | | | **$18** | | |

### 1.5 Development & Testing Supplies

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| Breadboard | Half-size breadboard | 1 | $5 | $5 | Adafruit / SparkFun | Prototyping (optional) |
| Heat Sinks | Raspberry Pi 4 heatsinks (set) | 1 | $5 | $5 | Adafruit / Amazon | Thermal management |
| **Subtotal** | | | | **$10** | | |

### 1.6 Spares & Contingency

| Item | Model/Specification | Quantity | Unit Price (USD) | Total (USD) | Supplier | Notes |
|------|---------------------|----------|------------------|-------------|----------|-------|
| Spare MicroSD Card | 32GB Class 10 | 1 | $8 | $8 | Amazon | Backup/imaging |
| Spare Components | Extra button, LEDs, resistors | 1 set | $5 | $5 | Adafruit | For testing/breakage |
| **Subtotal** | | | | **$13** | | |

---

## 2. Hardware Cost Summary

| Category | Cost (USD) |
|----------|------------|
| Core Computing | $93 |
| Audio Components | $50 |
| User Interface | $8.40 |
| Enclosure & Cables | $18 |
| Development Supplies | $10 |
| Spares & Contingency | $13 |
| **Total per Device** | **$192.40** |
| **For 2 Prototype Units** | **~$385** |

**Note:** Prices are approximate and may vary by region, supplier, and market conditions. Budget **$400-500** for 2 units to account for shipping, taxes, and price fluctuations.

---

## 3. Cloud Service Providers

### 3.1 Google Cloud Platform (STT & TTS)

**Provider:** Google Cloud Platform  
**Services:** Cloud Speech-to-Text API, Cloud Text-to-Speech API  
**Account Setup:** https://cloud.google.com/

#### 3.1.1 Speech-to-Text API

**Pricing Model:** Pay-per-use  
**Pricing:** 
- Standard Model: $0.006 per 15 seconds (~$0.024 per minute)
- Enhanced Model: $0.009 per 15 seconds (~$0.036 per minute)
- **Estimated Monthly Cost (Pilot):** $10-30 for ~500-1000 minutes of usage

**Free Tier:** 
- First 60 minutes per month free (standard model)
- Good for initial testing and low-volume pilots

**Documentation:** https://cloud.google.com/speech-to-text/docs  
**SDK:** `google-cloud-speech` (Python)

#### 3.1.2 Text-to-Speech API

**Pricing Model:** Pay-per-character  
**Pricing:**
- Standard voices: $4.00 per 1 million characters
- WaveNet/Neural2 voices: $16.00 per 1 million characters
- **Estimated Monthly Cost (Pilot):** $5-20 for ~100K-500K characters

**Free Tier:**
- First 4 million characters per month free (standard voices)
- First 1 million characters per month free (WaveNet/Neural2)

**Documentation:** https://cloud.google.com/text-to-speech/docs  
**SDK:** `google-cloud-texttospeech` (Python)

#### 3.1.3 Setup Requirements

1. **Google Cloud Account:** Create account at https://cloud.google.com/
2. **Project Creation:** Create a new GCP project (e.g., "meghan-voice-assistant")
3. **API Enablement:** Enable Speech-to-Text and Text-to-Speech APIs
4. **Service Account:** Create service account with appropriate permissions
5. **Credentials:** Download JSON key file for device authentication
6. **Billing:** Set up billing account (free tier covers initial usage)

**Estimated Total GCP Cost (Pilot):** $15-50/month

---

### 3.2 Meghan Backend (Existing)

**Provider:** Self-hosted / Current infrastructure  
**Services:** Chat API, User Management, Authentication  
**Cost:** Already part of existing infrastructure  
**Additional Cost:** Minimal (incremental API calls from voice devices)

**Endpoints Used:**
- `POST /api/auth/login-json` - Authentication
- `GET /api/auth/me` - User verification
- `POST /api/chat/conversations` - Create conversation
- `GET /api/chat/conversations` - List conversations
- `POST /api/chat/conversations/{id}/messages` - Send message
- `GET /api/users/me/state` - User state sync

**Estimated Additional Backend Cost:** $0-20/month (depending on hosting)

---

### 3.3 LLM Backend (Existing - Gemini)

**Provider:** Google AI Studio (Gemini API)  
**Services:** Already integrated in Meghan backend  
**Cost:** Already part of existing infrastructure  
**Additional Cost:** Incremental usage from voice interactions

**Estimated Additional LLM Cost:** $20-60/month (depending on usage volume)

---

## 4. Cloud Service Cost Summary

| Service | Monthly Cost (Pilot) | Notes |
|---------|---------------------|-------|
| Google Cloud STT | $10-30 | ~500-1000 minutes/month |
| Google Cloud TTS | $5-20 | ~100K-500K characters/month |
| Meghan Backend | $0-20 | Incremental hosting costs |
| LLM (Gemini) | $20-60 | Incremental API calls |
| **Total Monthly** | **$35-130** | Conservative estimate: **$50-150/month** |

**Note:** Free tiers significantly reduce costs during initial development and low-volume testing.

---

## 5. Software & Development Tools

### 5.1 Operating System

**Raspberry Pi OS (64-bit)**
- **Cost:** Free (open source)
- **Download:** https://www.raspberrypi.com/software/
- **Version:** Latest stable release (Debian-based)

### 5.2 Development Tools

| Tool | Cost | Notes |
|------|------|-------|
| Python 3.11+ | Free | Pre-installed with Raspberry Pi OS |
| Git | Free | Version control |
| VS Code / SSH | Free | Remote development |
| **Total** | **$0** | All open source |

---

## 6. Provider Contact Information & Links

### 6.1 Hardware Suppliers

**Raspberry Pi Official Store:**
- Website: https://www.raspberrypi.com/
- Shipping: Worldwide
- Notes: Official source, may have stock limitations

**Adafruit Industries:**
- Website: https://www.adafruit.com/
- Shipping: US-based, international shipping available
- Notes: Excellent documentation, good for components

**SparkFun Electronics:**
- Website: https://www.sparkfun.com/
- Shipping: US-based, international shipping available
- Notes: Good selection of components

**Amazon:**
- Website: https://www.amazon.com/
- Shipping: Varies by region
- Notes: Convenient, competitive pricing, fast shipping

**Seeed Studio:**
- Website: https://www.seeedstudio.com/
- Shipping: China-based, worldwide shipping
- Notes: Good for audio HATs and specialized components

### 6.2 Cloud Service Providers

**Google Cloud Platform:**
- Website: https://cloud.google.com/
- Support: https://cloud.google.com/support
- Documentation: https://cloud.google.com/docs
- Billing: Pay-as-you-go, free tier available

**Meghan Backend:**
- Current infrastructure (self-hosted or existing provider)
- No additional provider needed

---

## 7. Procurement Checklist

### Phase 0 (Planning)
- [ ] Review and approve BOM
- [ ] Set up Google Cloud account and enable APIs
- [ ] Obtain Google Cloud service account credentials
- [ ] Verify Meghan backend API accessibility from device network

### Phase 1 (Hardware Setup)
- [ ] Order Raspberry Pi 4 (4GB) + accessories
- [ ] Order USB microphone and speaker
- [ ] Order GPIO components (button, LED, resistors, wires)
- [ ] Order enclosure and cables
- [ ] Order spares and development supplies

### Phase 2 (Software Setup)
- [ ] Flash Raspberry Pi OS to microSD card
- [ ] Configure Wi-Fi and SSH access
- [ ] Install Python dependencies
- [ ] Set up Google Cloud credentials on device
- [ ] Test audio capture and playback

---

## 8. Budget Summary

### One-Time Costs (Per Device)

| Category | Cost (USD) |
|----------|------------|
| Hardware | $192.40 |
| Shipping & Handling | $10-20 |
| **Total per Device** | **~$200-210** |

### Recurring Costs (Monthly)

| Service | Cost (USD/month) |
|---------|------------------|
| Google Cloud (STT + TTS) | $15-50 |
| Meghan Backend (incremental) | $0-20 |
| LLM (Gemini, incremental) | $20-60 |
| **Total Monthly** | **$35-130** |

### Prototype Budget (2 Devices)

- **Hardware (2 units):** $400-500
- **Monthly Cloud Services (pilot):** $50-150
- **Total First Month:** $450-650
- **Ongoing Monthly:** $50-150

---

## 9. Risk Mitigation

### 9.1 Hardware Availability
- **Risk:** Raspberry Pi stock shortages
- **Mitigation:** Order early, consider alternatives (Raspberry Pi 5, Orange Pi, etc.)

### 9.2 Cloud Service Costs
- **Risk:** Higher than expected usage
- **Mitigation:** Set up billing alerts, monitor usage dashboard, implement usage caps

### 9.3 Component Compatibility
- **Risk:** Audio devices not working with Raspberry Pi
- **Mitigation:** Order from suppliers with good return policies, test components early

---

## 10. Approval & Sign-off

**Technical Decisions:**
- [x] Device Platform: Raspberry Pi 4 (4GB)
- [x] STT Provider: Google Cloud Speech-to-Text
- [x] TTS Provider: Google Cloud Text-to-Speech
- [x] Interaction Mode: Press-to-talk button

**BOM Approval:**
- [ ] Hardware components reviewed and approved
- [ ] Cloud services reviewed and approved
- [ ] Budget approved

**Next Steps:**
- Proceed to Phase 1: Hardware & OS Setup

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Prepared By:** Phase 0 Planning Team
