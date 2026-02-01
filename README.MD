---

# `wakeup_diana.py` — Technical Summary

## Overview

This script implements a **fully local voice assistant** named **Diana**, combining **Speech-to-Text (STT)**, a **local LLM**, **streaming Text-to-Speech (TTS)**, and **real-time audio I/O**.
The architecture prioritizes **low latency**, **continuous streaming**, and **manual control (Push-to-Talk)**.

---

## Core Components

### 1. Audio Input (STT)

* **Library:** `pyaudio`
* **Format:** 16-bit PCM, mono, 16 kHz
* **Control:** Records audio while `/tmp/diana_rec` exists (external Push-to-Talk, e.g. Caps Lock)
* **STT Engine:** `faster-whisper` (`small` model, CUDA + FP16)

Flow:

```
Microphone → PCM buffer → input.wav → Whisper → Text
```

---

### 2. Language Model (LLM)

* **Backend:** `ollama`
* **Model:** `qwen3:1.7b`
* **Mode:** Token streaming
* **Context Handling:** Sliding window of the last 8 messages + fixed system prompt

**System Persona (Diana):**

* Sarcastic, high-intellect systems engineer
* Strong technical bias (Arch Linux, kernel internals, C, cybersecurity, networking)
* Strict English-only responses
* Anti “helpful assistant” behavior
* Intentionally non hand-holding

---

### 3. Voice Output (Streaming TTS)

Unix-style streaming pipeline:

```
LLM (text stream)
 → Piper (TTS, raw PCM)
   → Sox (volume/gain)
     → aplay (direct playback)
```

* **TTS Engine:** `piper`
* **Voice Model:** `en_GB-cori-high.onnx`
* **Sample Rate:** 22050 Hz
* **Key Feature:** Speech starts **before** the full LLM response is finished

Audio is triggered **sentence by sentence**, using punctuation terminators (`. ! ? :`).

---

### 4. Terminal Text Animation

* Dedicated daemon thread (`animationPrinter`)
* Uses `queue.Queue`
* Simulates character-by-character typing
* Synchronized with the LLM token stream

---

## Runtime Control

* Main loop runs continuously
* Activated only when `/tmp/diana_rec` exists
* Voice-based exit commands:

  * `"bye diana"`, `"bye-bye diana"`, etc.
* Graceful shutdown:

  * Final spoken message
  * Proper process and pipe termination
  * PyAudio cleanup

---

## Design Characteristics

* Fully **offline / local**
* Perceptibly low latency
* Producer–consumer architecture
* Heavy use of **chained Unix processes**
* Clear separation between:

  * audio capture
  * transcription
  * reasoning
  * speech synthesis
  * presentation

---

## Possible Extensions

* Voice Activity Detection (VAD) instead of a sentinel file
* In-memory audio buffers (no `input.wav`)
* Automatic language detection
* Better prosody control per audio chunk
* Persistent long-term memory via embeddings

---
# Diana Voice Assistant

Low-latency local voice assistant with STT + LLM + streaming TTS.

## Demo

<video src="./demo.mp4" width="900"></video>
