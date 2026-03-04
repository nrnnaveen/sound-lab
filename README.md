# Sound Lab App

🎵 A Frequency Analyzer app that converts sound waves into a visual frequency spectrum.

## Features
- Record sound from your device.
- Perform Fast Fourier Transform (FFT) to visualize frequencies.
- Detect dominant frequency (Hz) in real-time.
- Tuning Fork mode to match sounds to musical notes.

## Tech Stack
- **React Native** for mobile app.
- **Streamlit + Python** for quick web demo.
- Libraries: `react-native-audio-recorder-player`, `fft.js`, `numpy`, `scipy`, `sounddevice`.

## Folder Structure

sound-lab/
├── App.js
├── package.json
├── babel.config.js
├── android/           # auto-generated when you run react-native init
├── ios/               # auto-generated when you run react-native init
├── components/
│   └── FrequencyAnalyzer.js
└── utils/
    └── fft.js

