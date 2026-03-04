import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import io
import librosa
import pandas as pd
import tempfile
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import time

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

st.title("🎵 Sound Lab - Live + Upload Frequency Analyzer with Export & Waveform")

mode = st.radio("Select Input Mode", ["Live Microphone", "Upload Audio"])

# ---------------- Upload Audio ----------------
if mode == "Upload Audio":
    uploaded_file = st.file_uploader("Upload WAV or MP3", type=["wav","mp3"])
    if uploaded_file is not None:
        st.audio(uploaded_file)
        try:
            y, sr = librosa.load(io.BytesIO(uploaded_file.read()), sr=None, mono=True)
        except Exception:
            st.error("Cannot read file. Please upload standard WAV or MP3.")
        else:
            # Waveform
            fig_wf, ax_wf = plt.subplots(figsize=(10,2))
            ax_wf.plot(y)
            ax_wf.set_title("Waveform")
            ax_wf.set_xlabel("Samples")
            ax_wf.set_ylabel("Amplitude")
            st.pyplot(fig_wf)

            # FFT
            N = len(y)
            yf = fft(y)
            xf = np.fft.fftfreq(N, 1/sr)
            peak_idx = np.argmax(np.abs(yf[:N//2]))
            fig_fft, ax_fft = plt.subplots(figsize=(10,4))
            ax_fft.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]))
            ax_fft.plot(xf[peak_idx], 2.0/N * np.abs(yf[peak_idx]), 'ro')
            ax_fft.set_title("Frequency Spectrum")
            ax_fft.set_xlabel("Frequency (Hz)")
            ax_fft.set_ylabel("Amplitude")
            st.pyplot(fig_fft)

            # Dominant frequency
            peak_freq = xf[peak_idx]
            st.success(f"Dominant Frequency: {abs(peak_freq):.2f} Hz")

            # Note detection
            note_name, cents = freq_to_note(abs(peak_freq))
            st.info(f"Nearest Musical Note: {note_name} ({cents:+} cents deviation)")

            # Export CSV
            fft_df = pd.DataFrame({
                "Frequency(Hz)": xf[:N//2],
                "Amplitude": 2.0/N * np.abs(yf[:N//2])
            })
            csv = fft_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download FFT Data CSV", csv, "fft_data.csv", "text/csv")

            # Export PNG
            tmpfile_fft = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            fig_fft.savefig(tmpfile_fft.name)
            st.download_button("Download FFT Plot PNG", tmpfile_fft.read(), "fft_plot.png", "image/png")

            tmpfile_wf = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            fig_wf.savefig(tmpfile_wf.name)
            st.download_button("Download Waveform PNG", tmpfile_wf.read(), "waveform.png", "image/png")

# ---------------- Live Microphone ----------------
elif mode == "Live Microphone":
    st.info("Streaming live microphone input. Waveform + FFT animate in real-time!")

    class AnimatedFFTProcessor(AudioProcessorBase):
        def __init__(self):
            self.audio_data = None
            self.sample_rate = 44100
            self.peak_freq = 0
            self.note_name = ""
            self.cents = 0

        def recv(self, frame):
            audio = frame.to_ndarray()[:,0]  # mono
            self.audio_data = audio
            if len(audio) > 0:
                yf = fft(audio)
                xf = np.fft.fftfreq(len(audio), 1/self.sample_rate)
                peak_idx = np.argmax(np.abs(yf[:len(xf)//2]))
                self.peak_freq = abs(xf[peak_idx])
                self.note_name, self.cents = freq_to_note(self.peak_freq)
            return frame

    ctx = webrtc_streamer(
        key="animated-live-fft",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AnimatedFFTProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )

    if ctx.audio_processor:
        waveform_placeholder = st.empty()
        fft_placeholder = st.empty()
        info_placeholder = st.empty()

        while True:
            y = ctx.audio_processor.audio_data
            if y is not None and len(y) > 0:
                # Waveform
                fig_wf, ax_wf = plt.subplots(figsize=(10,2))
                ax_wf.plot(y, color='blue')
                ax_wf.set_title("Live Waveform")
                ax_wf.set_xlabel("Samples")
                ax_wf.set_ylabel("Amplitude")
                waveform_placeholder.pyplot(fig_wf)

                # FFT
                N = len(y)
                yf = fft(y)
                xf = np.fft.fftfreq(N, 1/ctx.audio_processor.sample_rate)
                peak_idx = np.argmax(np.abs(yf[:N//2]))
                fig_fft, ax_fft = plt.subplots(figsize=(10,4))
                ax_fft.plot(xf[:N//2], 2.0/N * np.abs(yf[:N//2]), color='green')
                ax_fft.plot(xf[peak_idx], 2.0/N * np.abs(yf[peak_idx]), 'ro')
                ax_fft.set_title("Live Frequency Spectrum")
                ax_fft.set_xlabel("Frequency (Hz)")
                ax_fft.set_ylabel("Amplitude")
                fft_placeholder.pyplot(fig_fft)

                # Info
                info_placeholder.markdown(
                    f"**Dominant Frequency:** {ctx.audio_processor.peak_freq:.2f} Hz  \n"
                    f"**Nearest Note:** {ctx.audio_processor.note_name} ({ctx.audio_processor.cents:+} cents deviation)"
                )

            time.sleep(0.3)  # refresh every 0.3 seconds