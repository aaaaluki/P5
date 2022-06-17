#!/usr/bin/env python3 -u
import numpy as np
import scipy.io.wavfile as wavf

from config import *


OUT_FILE = f'{WORKDIR}/work/samples/pulse.wav'
N = 64
DUTY_CYCLE = 0.5
C = 1

# Gen one period of pulse wave
t = np.linspace(0, C*(N-1)/N, C*N)
samples = (2**15 - 1)*(2*(t <= DUTY_CYCLE) - 1)

# Sauce: https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
wavf.write(OUT_FILE, SAMPLING_FREQ, samples.astype(np.int16))
