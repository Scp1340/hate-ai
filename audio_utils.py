# audio_utils.py
import pyaudio
from typing import Tuple
from types import SimpleNamespace

def find_best_input_device(p: pyaudio.PyAudio, preferred_rates: Tuple[int, ...]) -> Tuple[int, int, str]:
    default_info = p.get_default_input_device_info()
    dev_idx = default_info['index']
    dev_name = default_info['name']
    max_channels = default_info['maxInputChannels']
    supported_rates = []
    for rate in preferred_rates:
        try:
            stream = p.open(format=pyaudio.paInt16,
                            channels=min(1, max_channels),
                            rate=rate,
                            input=True,
                            frames_per_buffer=1024,
                            start=False)
            stream.close()
            supported_rates.append(rate)
        except Exception:
            continue
    if supported_rates:
        best_rate = supported_rates[0]
    else:
        best_rate = int(default_info.get('defaultSampleRate', 16000))
    return dev_idx, best_rate, dev_name

def open_best_input_stream(p: pyaudio.PyAudio, preferred_rates: Tuple[int, ...], frames_per_buffer: int):
    dev_idx, rate, dev_name = find_best_input_device(p, preferred_rates)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    input_device_index=dev_idx,
                    frames_per_buffer=frames_per_buffer)
    return SimpleNamespace(stream=stream, sample_rate=rate, device_name=dev_name)

def find_best_output_device(p: pyaudio.PyAudio, preferred_rates: Tuple[int, ...]) -> Tuple[int, int, str]:
    default_info = p.get_default_output_device_info()
    dev_idx = default_info['index']
    dev_name = default_info['name']
    supported_rates = []
    for rate in preferred_rates:
        try:
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=rate,
                            output=True,
                            frames_per_buffer=1024,
                            start=False)
            stream.close()
            supported_rates.append(rate)
        except Exception:
            continue
    if supported_rates:
        best_rate = supported_rates[0]
    else:
        best_rate = int(default_info.get('defaultSampleRate', 24000))
    return dev_idx, best_rate, dev_name

def open_best_output_stream(p: pyaudio.PyAudio, preferred_rates: Tuple[int, ...], frames_per_buffer: int):
    dev_idx, rate, dev_name = find_best_output_device(p, preferred_rates)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    output=True,
                    output_device_index=dev_idx,
                    frames_per_buffer=frames_per_buffer)
    return SimpleNamespace(stream=stream, sample_rate=rate, device_name=dev_name)