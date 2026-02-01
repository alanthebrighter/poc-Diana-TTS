import subprocess
import ollama
import time
import threading
import queue
import pyaudio
import wave
from faster_whisper import WhisperModel
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

volume_factor = "0.4"

piper_cmd = [
    ".diana-tts/bin/piper",
    "--model",
    # "voices/en_GB-cori-high.onnx",
    "voices/en_US-hfc_female-medium.onnx",
    # "voices/en_US-kristin-medium.onnx",
    "--length_scale",
    "0.8",
    "--noise_scale",
    "0.8",
    "--noise_w",
    "1.0",
    "--output_raw",
]
sox_cmd = [
    "sox",
    "--buffer",
    "1024",
    "-t",
    "raw",
    "-r",
    "22050",
    "-e",
    "signed-integer",
    "-b",
    "16",
    "-c",
    "1",
    "-",
    "-t",
    "raw",
    "-",
    "vol",
    volume_factor,
]
aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-c", "1"]

audio_path = "./output.wav"

"""
is_recording = False


def on_press(key):
    global is_recording
    if key == keyboard.Key.caps_lock:
        is_recording = True
        print("\nDiana is listening...")


def on_release(key):
    global is_recording
    if key == keyboard.Key.caps_lock:
        is_recording = False
        print("Diana is thinking...")


listerner = keyboard.Listener(on_press=on_press, on_release=on_release)
listerner.start()
"""

p = pyaudio.PyAudio()

model_size = "small"
print(f"Loading model: {model_size}...")
model = WhisperModel(model_size, device="cuda", compute_type="float16")

piper_proc = subprocess.Popen(
    piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0
)
sox_proc = subprocess.Popen(
    sox_cmd, stdin=piper_proc.stdout, stdout=subprocess.PIPE, bufsize=0
)
aplay_proc = subprocess.Popen(
    aplay_cmd, stdin=sox_proc.stdout, stderr=subprocess.DEVNULL, bufsize=0
)

print_queue = queue.Queue()


def animationPrinter():
    while True:
        char = print_queue.get()

        print(char, end="", flush=True)
        # time.sleep(0.14)
        time.sleep(0.04)

        print_queue.task_done()


threading.Thread(target=animationPrinter, daemon=True).start()


def record_and_transcribe():
    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )
    frames = []

    print("\nDiana is listening...")

    while os.path.exists("/tmp/diana_rec"):
        data = stream.read(CHUNK)
        frames.append(data)

    print("\nDiana is thinking...")

    # while is_recording:
    #    data = stream.read(CHUNK)
    #    frames.append(data)

    stream.stop_stream()
    stream.close()

    wf = wave.open("input.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    segments, _ = model.transcribe("input.wav", beam_size=5, language="en")
    return "".join([s.text for s in segments])


# ========================================================================================================
# DIANA START
# ========================================================================================================
print("󰗋 Diana is here! (Say 'Byebye Diana' to Diana get out)")
print("Use caps_lock to Push-To-Talk")

exitkey = ["bye-bye diana.", "bye bye diana", "bye diana"]
system_message = {
    "role": "system",
    "content": """
Role: Diana.
Persona: Sarcastic, high-intellect systems engineer. 
Traits: Blunt, tech-obsessed, minimalist. 
Expertise: Arch Linux, Kernel internals, C, Cybersecurity (CyberOps/Red Teaming), Networking.

Communication Protocol:
1. STRICT ENGLISH ONLY. If the user speaks another language, reply with a dry remark in English about 'improper encoding' or 'unsupported protocols'.
2. NO HAND-HOLDING. If the user makes a grammar mistake, do not correct it like a teacher. Instead, mirror the correct version in your reply or make a subtle jab at their 'corrupted syntax'.
3. TECH-FIRST. Every topic—even mundane ones—should be viewed through a technical lens. Food is 'fuel injection', sleep is 'system downtime'.
4. ANTI-BOT BEHAVIOR: 
   - Never start with "Sure", "I can help", or "As an AI".
   - Use varied sentence lengths. Be brief if the question is trivial.
   - Avoid 'In summary' or 'Conclusion' sections.
5. KNOWLEDGE DEPTH: Don't give everything away. If they ask about a C bug, mention memory leaks or pointers and let them find the solution.
""",
}

ollama_model = "llama3.2:latest"
chatHistory = []


terminators = (".", "!", "?", ":")
forbidden = ["*", "_", "#", "`", ">"]

while True:
    if os.path.exists("/tmp/diana_rec"):
        user_text = record_and_transcribe()
        if not user_text.strip():
            continue

        if (
            "bye" in user_text.lower() or "bye." in user_text.lower()
        ) and "diana" in user_text.lower():
            break
        print(f"> {user_text}")

        chatHistory.append({"role": "user", "content": user_text})

        model_context = [system_message] + chatHistory[-8:]
        stream = ollama.chat(model=ollama_model, messages=model_context, stream=True)

        full_response = ""
        buffer = ""

        for chunck in stream:
            text = chunck["message"]["content"]
            full_response += text
            for char in text:
                print_queue.put(char)
                if char in forbidden:
                    continue
                buffer += char
                if char in terminators:
                    piper_proc.stdin.write((buffer + "\n").encode("utf-8"))
                    piper_proc.stdin.flush()
                    buffer = ""

        chatHistory.append({"role": "assistant", "content": full_response})
        print_queue.join()
        print()
    else:
        time.sleep(0.1)
p.terminate()
piper_proc.stdin.write(("Goodbye! See you next time. \n").encode("utf-8"))
piper_proc.stdin.flush()
print("󰗋 Diana went to do her daily Arch Rice and said GOODBYE!!")
piper_proc.stdin.close()
piper_proc.wait()


"""
while True:
    userInput = input("> ")
    chatHistory.append({"role": "user", "content": userInput})

    if userInput.lower() == exitkey:
        break

    modelContext = [system_message] + chatHistory[-6:]

    stream = ollama.chat(
        model="llama3.2:1b",
        messages=modelContext,
        stream=True,
    )
    fullRespose = ""
    buffer = ""
    for chunck in stream:
        text_chunk = chunck["message"]["content"]
        fullRespose += text_chunk
        # print(text_chunk, end="", flush=True)
        # print_queue.put(text_chunk)
        for char in text_chunk:
            print_queue.put(char)
            if char in forbidden:
                continue
            buffer += char
            if char in terminators:
                if any(c.isalnum() for c in buffer):
                    # print(buffer, flush=True)
                    piper_proc.stdin.write((buffer + "\n").encode("utf-8"))
                    piper_proc.stdin.flush()
                buffer = ""

    if any(c.isalnum() for c in buffer):
        # print(buffer, flush=True)
        piper_proc.stdin.write((buffer + "\n").encode("utf-8"))
        piper_proc.stdin.flush()
        buffer = ""
    chatHistory.append({"role": "assistant", "content": fullRespose})
    print_queue.join()
    print()

piper_proc.stdin.write(("Goodbye! See you next time. \n").encode("utf-8"))
piper_proc.stdin.flush()
print("󰗋 Diana went to do her daily Arch Rice and said GOODBYE!!")
piper_proc.stdin.close()
piper_proc.wait()
"""
