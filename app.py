import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

st.title("🎵 Sound Lab - Frequency Analyzer (WAV only)")

uploaded_file = st.file_uploader("Upload WAV file (uncompressed PCM)", type=["wav"])

if uploaded_file is not None:
    try:
        fs, data = wavfile.read(uploaded_file)
        y = data.flatten()

        # FFT
        N = len(y)
        yf = np.fft.fft(y)
        xf = np.fft.fftfreq(N, 1/fs)

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

    except Exception as e:
        st.error(f"Error reading WAV file: {e}")