import streamlit as st
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fft import fft

st.title("🎵 Sound Lab - Frequency Analyzer")

duration = st.slider("Recording Duration (seconds)", 1, 5, 3)

if st.button("Record Sound"):
    st.write("Recording...")
    fs = 44100  # Sample rate
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    st.write("Recording complete!")

    # FFT
    y = recording.flatten()
    N = len(y)
    yf = fft(y)
    xf = np.fft.fftfreq(N, 1/fs)
    
    # Plot
    plt.figure(figsize=(10,4))
    plt.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    st.pyplot(plt)
    
    # Detect peak frequency
    peak_freq = xf[np.argmax(np.abs(yf))]
    st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")
