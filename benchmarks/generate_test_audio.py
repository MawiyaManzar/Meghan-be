"""
Generates a minimal 1-second silent WAV file for use in voice load tests.
The file is saved as benchmarks/test_audio.wav

Usage:
    python benchmarks/generate_test_audio.py

Requirements: Python 3 standard library only (wave + struct).
"""

import os
import struct
import wave

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "test_audio.wav")

# ─── WAV parameters ───────────────────────────────────────────────────────────
SAMPLE_RATE   = 8000   # 8 kHz  (telephony quality — small file)
NUM_CHANNELS  = 1      # mono
SAMPLE_WIDTH  = 1      # 8-bit  (1 byte per sample)
DURATION_SEC  = 1      # 1 second → 8 000 samples → ~8 KB total file

def generate_silent_wav(path: str) -> None:
    num_frames = SAMPLE_RATE * DURATION_SEC
    # Silent = 0x80 for 8-bit unsigned PCM (midpoint, not actual 0x00)
    silence = struct.pack("B", 128) * num_frames

    with wave.open(path, "wb") as wf:
        wf.setnchannels(NUM_CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(silence)

    size_kb = os.path.getsize(path) / 1024
    print(f"[generate_test_audio] Created {path}  ({size_kb:.1f} KB)")
    print("[generate_test_audio] This is a 1-second silent WAV.")
    print("[generate_test_audio] AssemblyAI will likely return an empty transcript,")
    print("[generate_test_audio] which the voice endpoint returns as HTTP 400.")
    print("[generate_test_audio] To measure a real end-to-end voice round-trip,")
    print("[generate_test_audio] replace test_audio.wav with a real short speech clip.")

if __name__ == "__main__":
    generate_silent_wav(OUTPUT_PATH)
