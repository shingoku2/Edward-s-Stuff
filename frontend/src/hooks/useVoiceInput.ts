export function useVoiceInput(onTranscript: (text: string) => void) {
  const start = () => {
    const SR =
      (window as unknown as Record<string, unknown>).SpeechRecognition ||
      (window as unknown as Record<string, unknown>).webkitSpeechRecognition;
    if (!SR) return;
    const rec = new (SR as new () => SpeechRecognition)();
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e: SpeechRecognitionEvent) =>
      onTranscript(e.results[0][0].transcript);
    rec.start();
  };
  return { start };
}
