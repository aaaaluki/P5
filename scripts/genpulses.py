#!/usr/bin/env python3 -u
import sys

from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as wavf
from scipy import signal

from config import *

PLOT = True
OUT_FILE_DIR = f'{WORKDIR}/work/samples'
ORC_DIR = f'{WORKDIR}/work/instruments'
OUT_STR = '1\tFicTabla\tADSR_A=0.02;\tADSR_D=0.1;\tADSR_S=0.4;\tADSR_R=0.1;\tfile=work/samples/{}.wav;\n'
SCALING = (2**15 - 1)
N = 64

def plot(x, title):
    if PLOT:
        plt.plot(x)
        plt.title(title)
        plt.grid()
        plt.show()


def save_wave(name, samples):
    """
    Guarda las muestras en samples en un fichero .wav PCM 16 bits y fs = 44100 Hz.
    Luego genera el fichero .orc siguiendo la plantilla definida en OUT_STR.
    """
    
    wavfile = f'{OUT_FILE_DIR}/{name}.wav'
    orcfile = f'{ORC_DIR}/{name}.orc'

    
    print(f'Saving "{name.upper()}" .wav file as: {wavfile}')
    print(f'Saving "{name.upper()}" .orc file as: {orcfile}')

    wavf.write(wavfile, SAMPLING_FREQ, samples.astype(np.int16))
    file = open(orcfile, 'w')
    file.write(OUT_STR.format(name))
    file.close()

    plot(samples, name)


if len(sys.argv) > 1 and sys.argv[1].upper() == "PLOT":
    PLOT = True

t = np.linspace(0, (N-1)/N, N)

# Sauce for WTF (Write To File): https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html

# Sine Wave
samples = SCALING*np.sin(2*np.pi*t)
save_wave('sine', samples)

# Pulse Wave
samples = SCALING*(2*(t <= 0.5) - 1)
save_wave('pulse', samples)

# Sawtooth Wave
samples = SCALING*signal.sawtooth(2 * np.pi * t)
save_wave('sawtooth', samples)

# Triangle Wave
shift = 0.75
samples = SCALING*4*np.abs(t-shift - np.floor(t-shift + 0.5)) - 1
save_wave('triangle', samples)

# White Noise
# Sauce: https://stats.stackexchange.com/a/178629
samples = np.random.normal(0, 1, N)
maxv = np.max(samples)
minv = np.min(samples)
samples = SCALING*(2*(samples - minv) / (maxv - minv) - 1)
save_wave('white-noise', samples)
