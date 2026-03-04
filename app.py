import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft

st.title("🎵 Sound Lab - Frequency Analyzer (Upload Mode)")

uploaded_file = st.file_uploader("Upload a WAV file", type=["wav"])

if uploaded_file is not None:
    fs, data = wavfile.read(uploaded_file)
    y = data.flatten()
    N = len(y)
    yf = fft(y)
    xf = np.fft.fftfreq(N, 1/fs)

    plt.figure(figsize=(10,4))
    plt.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    st.pyplot(plt)

    peak_freq = xf[np.argmax(np.abs(yf))]
    st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")