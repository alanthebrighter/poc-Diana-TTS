import subprocess
import ollama
import time
import threading
import queue

print_queue = queue.Queue()

volume_factor = "0.4"

piper_cmd = [
    ".diana-tts/bin/piper",
    "--model",
    # "voices/en_GB-cori-high.onnx",
    "voices/en_US-hfc_female-medium.onnx",
    # "voices/en_US-kristin-medium.onnx",
    "--length_scale",
    "0.7",
    "--output_raw",
]
sox_cmd = [
    "sox",
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

piper_proc = subprocess.Popen(
    piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0
)
sox_proc = subprocess.Popen(
    sox_cmd, stdin=piper_proc.stdout, stdout=subprocess.PIPE, bufsize=0
)
aplay_proc = subprocess.Popen(
    aplay_cmd, stdin=sox_proc.stdout, stderr=subprocess.DEVNULL, bufsize=0
)

print("󰗋 Diana is here! (Use 'Byebye Diana' to Diana get out)")
exitkey = "byebye diana"


terminators = (".", "!", "?", ":")
forbidden = ["*", "_", "#", "`"]

while True:
    userInput = input("> ")

    if userInput.lower() == exitkey:
        break

    stream = ollama.chat(
        model="dianav5:latest",
        messages=[{"role": "user", "content": userInput}],
        stream=True,
    )

    buffer = ""
    for chunck in stream:
        text_chunk = chunck["message"]["content"]
        # print(text_chunk, end="", flush=True)
        for char in text_chunk:
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

    print()


print("󰗋 Diana went to do her daily Arch Rice and said GOODBYE!!")
piper_proc.stdin.close()
piper_proc.wait()
