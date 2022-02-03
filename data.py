from scipy.io import wavfile
from pathlib import Path
from itertools import chain
import random

def apply(function, generator):
    for item in generator:
        yield function(item)

def annotate(annotation, generator):
    for item in generator:
        yield (annotation, item)

def read_wav(wav_file: Path):
    rate, data = wavfile.read(wav_file.absolute())
    assert rate == 44100 and len(data) == 11025
    return data

def load(preprocess=None, load_fails=True, load_snaps=True):
    if load_fails is True:
        fail_wav_files = Path('data/fail').glob('*.wav')
        fails = apply(read_wav, fail_wav_files)
        if preprocess is not None:
            fails = apply(preprocess, fails)
        fails = list(annotate(False, fails))
    
    if load_snaps is True:
        snap_wav_files = Path('data/snap').glob('*.wav')
        snaps = apply(read_wav, snap_wav_files)
        if preprocess is not None:
            snaps = apply(preprocess, snaps)
        snaps = list(annotate(True, snaps))
    
    delta = len(snaps) - len(fails)
    if delta > 0:
        # there are more snaps than fails
        fails += random.sample(fails, delta)
    else: # delta <= 0
        # there are more fails than snaps
        delta = abs(delta)
        snaps += random.sample(snaps, delta)
    assert len(snaps) == len(fails)
    
    return chain(fails, snaps)


def split(samples, split=3):
    samples = list(samples)
    random.shuffle(samples)

    num_samples = len(samples)
    split_i = int(num_samples / 3)

    training_set = samples[split_i:]
    test_set = samples[:split_i]

    return (training_set, test_set)
