import React from "react";
import { SafeAreaView, StyleSheet, Text } from "react-native";
import FrequencyAnalyzer from "./components/FrequencyAnalyzer";

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>🎵 Sound Lab</Text>
      <FrequencyAnalyzer />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center", padding: 20 },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 20 }
});
