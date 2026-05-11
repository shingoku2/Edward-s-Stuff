import { useEffect, useRef, useCallback } from "react";
import { WS_URL } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";

type WSMessage =
  | { type: "token"; data: string }
  | { type: "done" }
  | { type: "error"; data: string }
  | { type: "game_changed"; data: { name: string | null; id: string | null } }
  | { type: "pong" };

export function useOmnixWS() {
  const wsRef = useRef<WebSocket | null>(null);
  const { setCurrentGame, appendChatToken, finalizeChatMessage, setAIStatus } = useAppStore();

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen    = () => setAIStatus("idle");
    ws.onmessage = (event) => {
      const msg: WSMessage = JSON.parse(event.data);
      switch (msg.type) {
        case "token":        appendChatToken(msg.data); break;
        case "done":         finalizeChatMessage(); setAIStatus("idle"); break;
        case "error":        finalizeChatMessage(`[ERROR] ${msg.data}`); setAIStatus("error"); break;
        case "game_changed": setCurrentGame(msg.data); break;
      }
    };
    ws.onclose   = () => setTimeout(connect, 3000);
    wsRef.current = ws;
  }, [appendChatToken, finalizeChatMessage, setAIStatus, setCurrentGame]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  const sendChat = useCallback(
    (message: string, gameContext?: Record<string, unknown>) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        setAIStatus("thinking");
        wsRef.current.send(
          JSON.stringify({ type: "chat", message, game_context: gameContext ?? {} })
        );
      }
    },
    [setAIStatus]
  );

  return { sendChat };
}
