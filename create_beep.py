import wave
import struct
import math

def create_beep(filename, duration_ms=300, freq=440, volume=0.5):
    framerate = 44100
    amplitude = 32767 * volume
    n_samples = int(framerate * duration_ms / 1000)
    wav_file = wave.open(filename, 'w')
    wav_file.setparams((1, 2, framerate, n_samples, 'NONE', 'not compressed'))

    for i in range(n_samples):
        sample = amplitude * math.sin(2 * math.pi * freq * i / framerate)
        wav_file.writeframes(struct.pack('h', int(sample)))

    wav_file.close()

create_beep("path_found.wav")
create_beep("error.wav", freq=220)