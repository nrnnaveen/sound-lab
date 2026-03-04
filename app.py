import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import io
import librosa
import pandas as pd
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

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

st.title("🎵 Sound Lab - Live + Upload Frequency Analyzer with Export")

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
            # FFT
            N = len(y)
            yf = fft(y)
            xf = np.fft.fftfreq(N, 1/sr)

            # Plot
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

            # Export CSV
            fft_df = pd.DataFrame({
                "Frequency(Hz)": xf[:N//2],
                "Amplitude": 2.0/N * np.abs(yf[:N//2])
            })
            csv = fft_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download FFT Data CSV", csv, "fft_data.csv", "text/csv")

            # Export PNG
            import tempfile
            tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            fig.savefig(tmpfile.name)
            st.download_button("Download FFT Plot PNG", tmpfile.read(), "fft_plot.png", "image/png")

# ---------------- Live Microphone ----------------
elif mode == "Live Microphone":
    st.info("Streaming live microphone input. Make sounds and click 'Update FFT'")

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

                # Export CSV
                fft_df = pd.DataFrame({
                    "Frequency(Hz)": xf[:N//2],
                    "Amplitude": 2.0/N * np.abs(yf[:N//2])
                })
                csv = fft_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download FFT Data CSV", csv, "fft_data.csv", "text/csv")

                # Export PNG
                import tempfile
                tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                fig.savefig(tmpfile.name)
                st.download_button("Download FFT Plot PNG", tmpfile.read(), "fft_plot.png", "image/png")
            else:
                st.warning("No audio detected yet. Make sure microphone is enabled.")