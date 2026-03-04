import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa

st.title("🎵 Sound Lab - Frequency Analyzer (Mobile-Friendly)")

uploaded_file = st.file_uploader(
    "Upload audio file (WAV, MP3, M4A)", type=["wav","mp3","m4a"]
)

if uploaded_file is not None:
    # Load audio using librosa
    y, sr = librosa.load(uploaded_file, sr=None, mono=True)  # preserve original rate

    # FFT
    N = len(y)
    yf = np.fft.fft(y)
    xf = np.fft.fftfreq(N, 1/sr)

    # Plot
    plt.figure(figsize=(10,4))
    plt.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    st.pyplot(plt)

    # Dominant frequency
    peak_freq = xf[np.argmax(np.abs(yf))]
    st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")