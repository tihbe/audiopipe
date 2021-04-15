import socket
import pyaudio
from tqdm import tqdm
from fire import Fire

DEFAULT_PORT = 63123

def server(bind_ip="0.0.0.0", port=DEFAULT_PORT, rate=48000, channels=2, block_size=4096, verbose=True):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    output=True)

    pbar = tqdm(desc="Data received", unit="bytes", unit_scale=True, disable=not verbose)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((bind_ip, port))
            while True:
                data = s.recv(block_size)
                pbar.update(len(data))
                stream.write(data)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        pbar.close()


def client(ip="127.0.0.1", port=DEFAULT_PORT, rate=48000, channels=2, block_size=1024, verbose=True):
    p = pyaudio.PyAudio()
    stereo_mix_index = None

    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if "stereo mix" in device["name"].lower():
            stereo_mix_index = i
            break

    if stereo_mix_index is None:
        print("Stereo mix not found")
        exit(1)

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input_device_index=stereo_mix_index,
                    input=True,
                    frames_per_buffer=block_size)

    pbar = tqdm(desc="Data sent", unit="bytes", unit_scale=True, disable=not verbose)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while True:
                data = stream.read(block_size)
                pbar.update(len(data))
                s.sendto(data, (ip, port))
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        pbar.close()


if __name__ == "__main__":
    Fire({"client": client, "server": server})