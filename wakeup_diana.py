import subprocess
import ollama
import time
import threading
import queue


def animationPrinter():
    while True:
        char = print_queue.get()

        print(char, end="", flush=True)
        # time.sleep(0.14)
        time.sleep(0.04)

        print_queue.task_done()


print_queue = queue.Queue()
threading.Thread(target=animationPrinter, daemon=True).start()

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
system_message = {
    "role": "system",
    "content": "You're Diana, my cyber assistant friend, You only speak English",
}
chatHistory = []


terminators = (".", "!", "?", ":")
forbidden = ["*", "_", "#", "`", ">"]

while True:
    userInput = input("> ")
    chatHistory.append({"role": "user", "content": userInput})

    if userInput.lower() == exitkey:
        break

    modelContext = [system_message] + chatHistory[-6:]

    stream = ollama.chat(
        model="dianav5:latest",
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
