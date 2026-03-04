import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from pydub import AudioSegment
import io

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(f):
    if f <= 0:
        return "None", 0
    note_number = 12 * np.log2(f / 440.0) + 69
    note_index = int(round(note_number)) % 12
    note_name = NOTE_NAMES[note_index]
    cents = int((note_number - round(note_number)) * 100)
    return note_name, cents

st.title("🎵 Sound Lab - Upload Frequency Analyzer (Safe)")

uploaded_file = st.file_uploader("Upload WAV/MP3/M4A", type=["wav","mp3","m4a"])
if uploaded_file is not None:
    st.audio(uploaded_file)  # playback immediately

    # Load with pydub
    audio = AudioSegment.from_file(io.BytesIO(uploaded_file.read()))
    y = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        y = y.reshape((-1, 2))
        y = y.mean(axis=1)  # convert to mono
    sr = audio.frame_rate

    # FFT
    N = len(y)
    yf = fft(y)
    xf = np.fft.fftfreq(N, 1/sr)

    # Plot FFT
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
    ax.set_title("Frequency Spectrum")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # Dominant frequency
    peak_freq = xf[np.argmax(np.abs(yf))]
    st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")

    # Note detection
    note_name, cents = freq_to_note(abs(peak_freq))
    st.info(f"Nearest Musical Note: {note_name} ({cents:+} cents deviation)")