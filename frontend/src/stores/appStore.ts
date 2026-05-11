import { create } from "zustand";

export type AIStatus = "idle" | "thinking" | "error";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  streaming?: boolean;
}

interface AppState {
  messages: ChatMessage[];
  aiStatus: AIStatus;
  appendChatToken: (token: string) => void;
  finalizeChatMessage: (override?: string) => void;
  addUserMessage: (content: string) => void;
  clearChat: () => void;
  currentGame: { name: string | null; id: string | null };
  setCurrentGame: (game: { name: string | null; id: string | null }) => void;
  cpu: number;
  ram: number;
  setStats: (cpu: number, ram: number) => void;
  overlayVisible: boolean;
  toggleOverlay: () => void;
  setAIStatus: (s: AIStatus) => void;
  settingsOpen: boolean;
  setSettingsOpen: (v: boolean) => void;
}

let _streamBuffer = "";

export const useAppStore = create<AppState>((set) => ({
  messages:       [],
  aiStatus:       "idle",
  currentGame:    { name: null, id: null },
  cpu:            0,
  ram:            0,
  overlayVisible: false,
  settingsOpen:   false,

  appendChatToken: (token) => {
    _streamBuffer += token;
    set((s) => {
      const msgs = [...s.messages];
      const last = msgs[msgs.length - 1];
      if (last?.streaming) {
        msgs[msgs.length - 1] = { ...last, content: _streamBuffer };
      } else {
        msgs.push({
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: _streamBuffer,
          timestamp: Date.now(),
          streaming: true,
        });
      }
      return { messages: msgs };
    });
  },

  finalizeChatMessage: (override) => {
    set((s) => {
      const msgs = [...s.messages];
      const last = msgs[msgs.length - 1];
      if (last?.streaming) {
        msgs[msgs.length - 1] = {
          ...last,
          content: override ?? _streamBuffer,
          streaming: false,
        };
      }
      _streamBuffer = "";
      return { messages: msgs };
    });
  },

  addUserMessage: (content) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { id: `u-${Date.now()}`, role: "user", content, timestamp: Date.now() },
      ],
    })),

  clearChat:       () => set({ messages: [] }),
  setCurrentGame:  (game) => set({ currentGame: game }),
  setStats:        (cpu, ram) => set({ cpu, ram }),
  toggleOverlay:   () => set((s) => ({ overlayVisible: !s.overlayVisible })),
  setAIStatus:     (aiStatus) => set({ aiStatus }),
  setSettingsOpen: (settingsOpen) => set({ settingsOpen }),
}));
