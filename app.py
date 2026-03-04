import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from pydub import AudioSegment
import io

st.title("🎵 Sound Lab - Frequency Analyzer (Any Audio)")

uploaded_file = st.file_uploader("Upload audio file (WAV, MP3, M4A)", type=["wav","mp3","m4a"])

if uploaded_file is not None:
    # Convert to uncompressed WAV in memory
    audio = AudioSegment.from_file(io.BytesIO(uploaded_file.read()))
    audio = audio.set_channels(1)  # mono
    fs = audio.frame_rate
    samples = np.array(audio.get_array_of_samples())
    
    # FFT
    N = len(samples)
    yf = fft(samples)
    xf = np.fft.fftfreq(N, 1/fs)
    
    # Plot
    plt.figure(figsize=(10,4))
    plt.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    st.pyplot(plt)
    
    peak_freq = xf[np.argmax(np.abs(yf))]
    st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")