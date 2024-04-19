
import os
import pyaudio
import numpy as np
import time

p = pyaudio.PyAudio()

info = p.get_default_output_device_info()

duration = 1
fs = 44100

print('crunch crunch')

def make_sin(frequency):
    return (np.sin(2 * np.pi * np.arange(fs * duration) * frequency / fs)).astype(np.float32).tobytes()

print('too slow')

stream = p.open(format=pyaudio.paFloat32,
        channels=1,
        rate=fs,
        output=True)
print('ready to stream')
time.sleep(1)

print('st 1')
stream.write(make_sin(440))
print('st 2')
stream.write(make_sin(800))

#stream.stop_stream()
#stream.close()

#p.terminate()

