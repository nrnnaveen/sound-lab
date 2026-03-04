import FFT from "fft.js";

export const computeFFT = (audioBuffer) => {
  const f = new FFT(audioBuffer.length);
  const out = f.createComplexArray();
  f.realTransform(out, audioBuffer);
  f.completeSpectrum(out);
  return out;
};
