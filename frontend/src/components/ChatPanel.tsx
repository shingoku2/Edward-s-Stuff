import React from 'react';
import { Circle, MessageSquare } from 'lucide-react';
import Panel from './Panel';

type ChatMessage = {
  id: number;
  author: 'omnix' | 'user';
  text: string;
  status?: 'processing' | 'reply';
};

type ChatPanelProps = {
  messages: ChatMessage[];
  chatInput: string;
  setChatInput: (value: string) => void;
  appendMessage: (text: string) => void;
  activeProvider: string;
};

const ChatPanel = ({ messages, chatInput, setChatInput, appendMessage, activeProvider }: ChatPanelProps) => (
  <Panel className="flex-1 flex flex-col" footer="Overlay" subtitle="Live Link">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2 text-xs text-omnix-blue/80 font-hud tracking-[0.3em] uppercase">
        <Circle className="w-3 h-3 text-omnix-blue fill-omnix-blue animate-pulse" />
        Session Chat
      </div>
      <span className="text-[10px] text-omnix-blue/60">{messages.length} events</span>
    </div>

    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
      {messages.map(message => (
        <div
          key={message.id}
          className={`relative p-3 rounded-md border border-omnix-blue/20 bg-gradient-to-r ${
            message.author === 'omnix'
              ? 'from-omnix-blue/20 via-omnix-blue/5 to-transparent'
              : 'from-white/10 via-white/5 to-transparent'
          }`}
        >
          <div className="absolute left-[-6px] top-1/2 -translate-y-1/2 w-1 h-8 bg-omnix-blue" />
          <div className="flex items-center gap-3">
            {message.author === 'omnix' ? (
              <div className="flex items-center gap-2 text-omnix-blue text-xs font-hud tracking-[0.2em] uppercase">
                <MessageSquare className="w-4 h-4" />
                OMNIX
              </div>
            ) : (
              <div className="flex items-center gap-2 text-omnix-text text-xs font-hud tracking-[0.2em] uppercase">
                <Circle className="w-3 h-3 text-omnix-blue/70" />
                You
              </div>
            )}
            <p className="text-sm text-omnix-text/90 leading-relaxed flex-1">{message.text}</p>
          </div>
          {message.status === 'processing' && (
            <div className="flex items-center gap-3 mt-2 text-omnix-blue text-[11px] tracking-[0.2em]">
              <div className="relative w-6 h-6">
                <div className="absolute inset-0 border-2 border-omnix-blue/20 rounded-full" />
                <div className="absolute inset-0 border-t-2 border-omnix-blue rounded-full animate-spin" />
              </div>
              Analyzing the game now...
            </div>
          )}
          {message.status === 'reply' && (
            <div className="mt-2 text-[11px] text-omnix-blue/70 font-hud tracking-[0.25em] uppercase">
              Awaiting response
            </div>
          )}
        </div>
      ))}
    </div>

    <div className="mt-5 space-y-3">
      <div className="flex gap-2">
        <input
          value={chatInput}
          onChange={e => setChatInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && appendMessage(chatInput)}
          placeholder="Type a command or ask for guidance..."
          className="flex-1 bg-[#060e1c] border border-omnix-blue/40 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-omnix-blue text-omnix-text placeholder:text-omnix-text/40"
        />
        <button
          onClick={() => appendMessage(chatInput)}
          className="px-4 py-2 bg-omnix-blue/15 border border-omnix-blue/60 text-omnix-blue font-hud tracking-[0.25em] text-xs uppercase hover:bg-omnix-blue/25 transition-colors rounded-md"
        >
          Send
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {[
          { label: 'Ask for strategy', text: 'Give me a quick strat for this round.' },
          { label: 'Request macro', text: 'Prepare a recoil-control macro.' },
          { label: 'Status check', text: 'Are overlays locked in place?' },
          { label: 'Provider switch', text: `Confirm ${activeProvider.toUpperCase()} routing.` }
        ].map(action => (
          <button
            key={action.label}
            onClick={() => appendMessage(action.text)}
            className="text-left px-3 py-2 border border-omnix-blue/25 hover:border-omnix-blue/60 hover:bg-omnix-blue/10 text-xs text-omnix-text rounded-md transition-all"
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  </Panel>
);

export default ChatPanel;
