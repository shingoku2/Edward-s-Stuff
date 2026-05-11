/// <reference types="vite/client" />

// SpeechRecognition and SpeechRecognitionEvent are part of the Web Speech API
// but are not included in TypeScript's standard DOM lib (only the result types
// were standardized). Declare them here so useVoiceInput.ts compiles cleanly.
interface SpeechRecognitionEvent extends Event {
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare var SpeechRecognition: {
  new(): SpeechRecognition;
  prototype: SpeechRecognition;
};
