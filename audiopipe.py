import socket
import pyaudio
from tqdm import tqdm
from fire import Fire

DEFAULT_PORT = 63123
DEFAULT_BITRATE = 48000


def devices(p=pyaudio.PyAudio()):
    for i in range(p.get_device_count()):
        yield i, p.get_device_info_by_index(i)


def get_device_index_by_name(name, p=pyaudio.PyAudio()):
    for i, device in devices(p):
        if name.lower() in device["name"].lower():
            return i

    return None


def print_devices():
    for _, device in devices():
        print(device["name"])


def start_server(
    bind_ip="0.0.0.0",
    port=DEFAULT_PORT,
    rate=DEFAULT_BITRATE,
    channels=2,
    block_size=4096,
    verbose=True,
    device_name="",
):
    p = pyaudio.PyAudio()
    device_index = get_device_index_by_name(device_name, p) if device_name else None
    if device_name and device_index is None:
        print(f"Device '{device_name}' not found.")
        exit(1)

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        output=True,
        output_device_index=device_index,
    )
    pbar = tqdm(
        desc="Data received", unit="bytes", unit_scale=True, disable=not verbose
    )

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


def start_client(
    ip="127.0.0.1",
    port=DEFAULT_PORT,
    rate=DEFAULT_BITRATE,
    channels=2,
    block_size=1024,
    verbose=True,
    device_name="stereo mix",
):
    p = pyaudio.PyAudio()
    device_index = get_device_index_by_name(device_name, p) if device_name else None
    if device_name and device_index is None:
        print(f"Device '{device_name}' not found.")
        exit(1)

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=block_size,
    )
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
    Fire(
        {"client": start_client, "server": start_server, "list_devices": print_devices}
    )
