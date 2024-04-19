import os
from pathlib import Path
import torchaudio
import pyaudio
from pydub import AudioSegment

file1 = "speech.de.wav"
file2 = "speech.fr.wav"


with open(file1, 'rb') as file:         
        de_data = file.read()

with open(file2, 'rb') as file:
        fr_data = file.read()


metadata = torchaudio.info(de_data)
print(metadata)

metadata = torchaudio.info(fr_data)
print( metadata)


print("Setting up audio")
p = pyaudio.PyAudio()
print("Opening stream")
stream = p.open(format=p.get_format_from_width(2), channels=2, rate=16000, output=True)
print("Sending data to audio")
chunk_size = 256  # Adjust the chunk size as needed
offset = 0
out_wave1 = de_data[44:]
out_wave2 = fr_data[44:]
new_wave = [0] * 4 * len(out_wave1)
while offset < len(out_wave1):
    new_wave[offset*2] = out_wave1[offset]
    new_wave[offset*2+1] = out_wave1[offset+1]
    new_wave[offset*2+2] = out_wave2[offset]
    new_wave[offset*2+3] = out_wave2[offset+1]
    offset += 2


offset = 0

while offset < len(new_wave):
    chunk = new_wave[offset:offset + chunk_size]
    stream.write(bytes(chunk))

    offset += chunk_size



