import React, { useState } from "react";
import { View, Button, Text } from "react-native";
import AudioRecorderPlayer from "react-native-audio-recorder-player";
import FFT from "fft.js";

const audioRecorderPlayer = new AudioRecorderPlayer();

export default function FrequencyAnalyzer() {
  const [frequency, setFrequency] = useState(null);

  const startRecording = async () => {
    const result = await audioRecorderPlayer.startRecorder();
    console.log("Recording started:", result);
    // Stop after 3 seconds and analyze
    setTimeout(async () => {
      const stopResult = await audioRecorderPlayer.stopRecorder();
      console.log("Recording stopped:", stopResult);

      // Here you can process stopResult for FFT
      // Example: fake frequency for demo
      setFrequency(Math.floor(Math.random() * 1000));
    }, 3000);
  };

  return (
    <View>
      <Button title="Start Recording" onPress={startRecording} />
      {frequency && <Text style={{ marginTop: 20 }}>Detected Frequency: {frequency} Hz</Text>}
    </View>
  );
}
