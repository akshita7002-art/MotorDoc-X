"""Signal-processing features: MFCC (sound) + vibration, temperature, current."""
import numpy as np
from scipy.fft import dct

AUDIO_FS = 8000   # Hz, microphone sampling rate
VIB_FS = 1000     # Hz, vibration sensor sampling rate
N_MFCC = 13
N_MELS = 26

FEATURE_NAMES = (
    [f"mfcc_{i}" for i in range(N_MFCC)]
    + ["spec_centroid", "vib_rms", "vib_kurtosis", "vib_dom_freq", "temp_c", "current_a"]
)


def _hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)


def _mel_to_hz(m):
    return 700.0 * (10 ** (m / 2595.0) - 1.0)


def _mel_filterbank(n_fft, fs, n_mels=N_MELS):
    mels = np.linspace(_hz_to_mel(0), _hz_to_mel(fs / 2), n_mels + 2)
    bins = np.floor((n_fft + 1) * _mel_to_hz(mels) / fs).astype(int)
    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for i in range(1, n_mels + 1):
        l, c, r = bins[i - 1], bins[i], bins[i + 1]
        for k in range(l, c):
            fb[i - 1, k] = (k - l) / max(c - l, 1)
        for k in range(c, r):
            fb[i - 1, k] = (r - k) / max(r - c, 1)
    return fb


def mfcc(audio, fs=AUDIO_FS, frame=512, hop=256):
    """Mean MFCC vector (N_MFCC,) over all frames of a mono audio clip."""
    audio = np.asarray(audio, dtype=float)
    audio = audio - audio.mean()
    n_frames = 1 + (len(audio) - frame) // hop
    window = np.hanning(frame)
    fb = _mel_filterbank(frame, fs)
    coeffs = []
    for i in range(n_frames):
        seg = audio[i * hop: i * hop + frame] * window
        power = np.abs(np.fft.rfft(seg)) ** 2
        mel_energy = np.log(fb @ power + 1e-10)
        coeffs.append(dct(mel_energy, type=2, norm="ortho")[:N_MFCC])
    return np.mean(coeffs, axis=0)


def spectral_centroid(audio, fs=AUDIO_FS):
    spec = np.abs(np.fft.rfft(audio - np.mean(audio)))
    freqs = np.fft.rfftfreq(len(audio), 1 / fs)
    return float(np.sum(freqs * spec) / (np.sum(spec) + 1e-12))


def vibration_features(vib, fs=VIB_FS):
    vib = np.asarray(vib, dtype=float)
    vib = vib - vib.mean()
    rms = float(np.sqrt(np.mean(vib ** 2)))
    kurt = float(np.mean(vib ** 4) / (np.mean(vib ** 2) ** 2 + 1e-12))
    spec = np.abs(np.fft.rfft(vib))
    freqs = np.fft.rfftfreq(len(vib), 1 / fs)
    dom = float(freqs[np.argmax(spec[1:]) + 1])
    return rms, kurt, dom


def extract_features(audio, vib, temp_c, current_a):
    """Build one feature vector (len == len(FEATURE_NAMES)) from raw readings."""
    rms, kurt, dom = vibration_features(vib)
    return np.concatenate([
        mfcc(audio),
        [spectral_centroid(audio), rms, kurt, dom, float(temp_c), float(current_a)],
    ])
