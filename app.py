import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import io
import librosa

# Musical note mapping
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(f):
    if f <= 0:
        return "None", 0
    note_number = 12 * np.log2(f / 440.0) + 69
    note_index = int(round(note_number)) % 12
    note_name = NOTE_NAMES[note_index]
    cents = int((note_number - round(note_number)) * 100)
    return note_name, cents

st.title("🎵 Sound Lab - Live + Upload Frequency Analyzer")

mode = st.radio("Select Input Mode", ["Live Microphone", "Upload Audio"])

# ---------------- Upload Audio ----------------
if mode == "Upload Audio":
    uploaded_file = st.file_uploader("Upload WAV/MP3/M4A", type=["wav","mp3","m4a"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        # Audio playback shown immediately
        st.audio(audio_bytes)

        # Process uploaded audio for FFT
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
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

# ---------------- Live Microphone ----------------
elif mode == "Live Microphone":
    st.info("Streaming live microphone input. Make sounds to see frequency spectrum.")

    from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

    class FFTProcessor(AudioProcessorBase):
        def __init__(self):
            self.fft_result = None
            self.sample_rate = 44100

        def recv(self, frame):
            audio = frame.to_ndarray()[:,0]  # mono
            self.fft_result = audio
            return frame

    ctx = webrtc_streamer(
        key="live-fft",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=FFTProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )

    if ctx.audio_processor:
        st.write("Make a sound and click 'Update FFT'")
        if st.button("Update FFT"):
            y = ctx.audio_processor.fft_result
            if y is not None and len(y) > 0:
                N = len(y)
                yf = fft(y)
                xf = np.fft.fftfreq(N, 1/ctx.audio_processor.sample_rate)

                # Plot FFT
                fig, ax = plt.subplots(figsize=(10,4))
                ax.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
                ax.set_title("Frequency Spectrum (Live Mic)")
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Amplitude")
                st.pyplot(fig)

                # Dominant frequency
                peak_freq = xf[np.argmax(np.abs(yf))]
                st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")

                # Note detection
                note_name, cents = freq_to_note(abs(peak_freq))
                st.info(f"Nearest Musical Note: {note_name} ({cents:+} cents deviation)")
            else:
                st.warning("No audio detected yet. Make sure microphone is enabled.")