#!/usr/bin/env python3 -u
from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as wavf
from scipy import signal

from config import *


PLOT = True
OUT_FILE_DIR = f'{WORKDIR}/work/samples'
SCALING = (2**15 - 1)
N = 64

def plot(x):
    if PLOT:
        plt.plot(x)
        plt.grid()
        plt.show()


t = np.linspace(0, (N-1)/N, N)

# Sauce for WTF (Write To File): https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html

# Sine Wave
samples = SCALING*np.sin(2*np.pi*t)
wavf.write(f'{OUT_FILE_DIR}/sine.wav', SAMPLING_FREQ, samples.astype(np.int16))
plot(samples)

# Pulse Wave
samples = SCALING*(2*(t <= 0.5) - 1)
wavf.write(f'{OUT_FILE_DIR}/pulse.wav', SAMPLING_FREQ, samples.astype(np.int16))
plot(samples)

# Sawtooth Wave
samples = SCALING*signal.sawtooth(2 * np.pi * t)
wavf.write(f'{OUT_FILE_DIR}/sawtooth.wav', SAMPLING_FREQ, samples.astype(np.int16))
plot(samples)

# Triangle Wave
samples = SCALING*4*np.abs(t - np.floor(t + 0.5)) - 1
wavf.write(f'{OUT_FILE_DIR}/triangle.wav', SAMPLING_FREQ, samples.astype(np.int16))
plot(samples)

# White Noise
# Sauce: https://stats.stackexchange.com/a/178629
samples = SCALING*np.random.normal(0, 1, N)
maxv = np.max(samples)
minv = np.min(samples)
samples = 2*(samples - minv) / (maxv - minv) - 1
wavf.write(f'{OUT_FILE_DIR}/white-noise.wav', SAMPLING_FREQ, samples.astype(np.int16))
plot(samples)
