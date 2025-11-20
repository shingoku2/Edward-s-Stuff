import React, { useEffect, useMemo, useState } from 'react';
import {
  Lock,
  Activity,
  Crosshair,
  Cpu,
  ChevronRight,
  Circle,
  Bell,
  ShieldCheck,
  MonitorSmartphone,
  SunMoon,
  MessageSquare,
  RefreshCw,
  Power,
  Wifi
} from 'lucide-react';

const CornerBrackets = () => (
  <>
    <div className="absolute -top-[1px] -left-[1px] w-12 h-12">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent" />
      <div className="absolute top-0 left-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent" />
      <div className="absolute top-2 left-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute top-2 left-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -top-[1px] -right-[1px] w-12 h-12">
      <div className="absolute top-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent" />
      <div className="absolute top-0 right-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent" />
      <div className="absolute top-2 right-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute top-2 right-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -bottom-[1px] -left-[1px] w-12 h-12">
      <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent" />
      <div className="absolute bottom-0 left-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent" />
      <div className="absolute bottom-2 left-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute bottom-2 left-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
    <div className="absolute -bottom-[1px] -right-[1px] w-12 h-12">
      <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent" />
      <div className="absolute bottom-0 right-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent" />
      <div className="absolute bottom-2 right-2 w-3 h-[2px] bg-omnix-blue/50" />
      <div className="absolute bottom-2 right-2 w-[2px] h-3 bg-omnix-blue/50" />
    </div>
  </>
);

type PanelProps = {
  children: React.ReactNode;
  className?: string;
  title?: string;
  footer?: string;
  subtitle?: string;
};

const Panel = ({ children, className = "", title, footer, subtitle }: PanelProps) => (
  <div
    className={`relative bg-omnix-panel/80 border border-omnix-blue/30 rounded-md p-6 backdrop-blur-xl shadow-[0_0_40px_rgba(0,243,255,0.08)] ${className}`}
  >
    <CornerBrackets />

    {(title || subtitle) && (
      <div className="mb-5 flex items-center justify-between">
        {title && (
          <h3 className="text-omnix-blue font-hud tracking-[0.35em] text-[11px] uppercase">{title}</h3>
        )}
        {subtitle && (
          <span className="text-[10px] font-hud tracking-[0.25em] text-omnix-blue/70 uppercase">{subtitle}</span>
        )}
      </div>
    )}
    <div className="relative">{children}</div>

    {footer && (
      <div className="mt-6 pt-4 border-t border-omnix-blue/10">
        <p className="text-center text-omnix-blue/60 font-hud tracking-[0.35em] text-[11px] uppercase">{footer}</p>
      </div>
    )}
  </div>
);

type ChatMessage = {
  id: number;
  author: 'omnix' | 'user';
  text: string;
  status?: 'processing' | 'reply';
};

type GameStatus = {
  name: string;
  mode: string;
  kd: number;
  wins: number;
  matches: number;
  online: boolean;
  provider: string;
};

export default function OmnixHUD() {
  const [activeProvider, setActiveProvider] = useState('hybridnex');
  const [activeSetting, setActiveSetting] = useState<'overlay' | 'general' | 'notifications' | 'privacy'>('overlay');
  const [overlayMode, setOverlayMode] = useState<'compact' | 'immersive'>('immersive');
  const [lockPosition, setLockPosition] = useState(true);
  const [generalSettings, setGeneralSettings] = useState({ autoStart: true, energySaver: false, showTooltips: true });
  const [notificationSettings, setNotificationSettings] = useState({ desktop: true, sound: false, aiUpdates: true });
  const [privacySettings, setPrivacySettings] = useState({ streamerMode: true, redactLogs: true, shareUsage: false });
  const [gameStatus, setGameStatus] = useState<GameStatus>({
    name: 'Counter-Strike',
    mode: 'Competitive',
    kd: 1.29,
    wins: 118,
    matches: 19,
    online: true,
    provider: 'omnix-scan'
  });
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, author: 'omnix', text: 'Hello! I am monitoring your current match.' },
    { id: 2, author: 'user', text: 'Hi! How can you assist me?' },
    { id: 3, author: 'omnix', text: 'Analyzing the game now...', status: 'processing' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const settingsMenu = useMemo(
    () => [
      { id: 'overlay' as const, label: 'Overlay Mode', icon: MonitorSmartphone },
      { id: 'general' as const, label: 'General', icon: SunMoon },
      { id: 'notifications' as const, label: 'Notifications', icon: Bell },
      { id: 'privacy' as const, label: 'Privacy', icon: ShieldCheck }
    ],
    []
  );

  useEffect(() => {
    setGameStatus(prev => ({ ...prev, provider: activeProvider }));
  }, [activeProvider]);

  const appendMessage = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setMessages(prev => {
      const nextId = prev[prev.length - 1]?.id ? prev[prev.length - 1].id + 1 : 1;
      const userMessage: ChatMessage = { id: nextId, author: 'user', text: trimmed };
      const acknowledgment: ChatMessage = {
        id: nextId + 1,
        author: 'omnix',
        text: `Routing to ${activeProvider.toUpperCase()}...`,
        status: 'reply'
      };

      return [...prev, userMessage, acknowledgment];
    });

    setChatInput('');
  };

  type SettingGroup = 'general' | 'notifications' | 'privacy';
  type SettingStateMap = {
    general: typeof generalSettings;
    notifications: typeof notificationSettings;
    privacy: typeof privacySettings;
  };

  const toggleSetting = <T extends SettingGroup>(group: T, key: keyof SettingStateMap[T]) => {
    const updateMap: { [K in SettingGroup]: React.Dispatch<React.SetStateAction<SettingStateMap[K]>> } = {
      general: setGeneralSettings,
      notifications: setNotificationSettings,
      privacy: setPrivacySettings
    };

    updateMap[group](prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050915] via-[#060c1c] to-[#0b1630] text-omnix-text font-body p-10 flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_20%_20%,rgba(0,243,255,0.08),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(255,42,42,0.08),transparent_30%),radial-gradient(circle_at_60%_80%,rgba(0,243,255,0.05),transparent_25%)]" />
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/asfalt-light.png')] opacity-20" />

      <div className="w-full max-w-7xl relative">
        <div className="relative border border-omnix-blue/40 rounded-lg p-8 bg-[#040915]/90 backdrop-blur-strong shadow-[0_0_60px_rgba(0,243,255,0.12)] overflow-hidden">
          <CornerBrackets />

          <header className="mb-8 relative flex items-start justify-between">
            <div>
              <h1 className="text-6xl font-hud font-black tracking-[0.35em] text-transparent bg-clip-text bg-gradient-to-b from-white via-omnix-blue to-omnix-blue drop-shadow-[0_0_30px_rgba(0,243,255,0.65)]">
                OMNIX
              </h1>
              <p className="text-omnix-blue tracking-[0.35em] text-xs font-hud mt-1 uppercase opacity-80">- All Knowing AI Companion -</p>
            </div>

            <div className="flex items-center gap-3 text-omnix-blue/70 text-[10px] font-hud tracking-[0.35em] uppercase">
              <div className="h-px w-16 bg-gradient-to-r from-transparent via-omnix-blue/40 to-omnix-blue/70" />
              <span className="flex items-center gap-2">
                <Wifi className={`w-4 h-4 ${gameStatus.online ? 'text-omnix-blue' : 'text-omnix-red'}`} />
                {gameStatus.online ? 'Network Synced' : 'Reconnecting'}
              </span>
              <div className="h-px w-16 bg-gradient-to-l from-transparent via-omnix-blue/40 to-omnix-blue/70" />
            </div>
          </header>

          <div className="grid grid-cols-[330px_minmax(420px,1fr)_330px] gap-6">
            <div className="flex flex-col">
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
            </div>

            <div className="flex flex-col items-center justify-center relative gap-8">
              <div className="relative w-full flex flex-col items-center">
                <div className="absolute -inset-4 opacity-30 bg-[radial-gradient(circle_at_center,rgba(0,243,255,0.15),transparent_60%)]" />
                <div className="relative w-80 h-80 flex items-center justify-center">
                  <div className="absolute inset-0 clip-hexagon-border border border-omnix-blue/35 shadow-[0_0_25px_rgba(0,243,255,0.25)]" />
                  <div className="absolute inset-2 clip-hexagon-border border border-omnix-blue/20" />
                  <div className="absolute inset-6 rounded-full border-2 border-omnix-blue/30" />
                  <div className="absolute inset-8 rounded-full border-t-2 border-omnix-blue animate-spin-slow" />

                  <div className="relative w-48 h-48 rounded-full border-2 border-omnix-blue/40 flex items-center justify-center bg-[#071124] shadow-[0_0_35px_rgba(0,243,255,0.1)]">
                    <div className="text-center z-10">
                      <div className="mx-auto w-20 h-20 mb-3 flex items-center justify-center">
                        <Crosshair className="w-full h-full text-omnix-red drop-shadow-[0_0_14px_rgba(255,42,42,0.75)]" />
                      </div>
                      <p className="text-omnix-blue text-[11px] tracking-[0.3em] font-hud uppercase">{gameStatus.name}</p>
                      <p className="text-[10px] text-omnix-text/80 tracking-[0.25em] font-hud uppercase">{gameStatus.mode}</p>
                    </div>
                  </div>

                  <div className="absolute -top-7 left-1/2 -translate-x-1/2">
                    <div className="relative px-4 py-1 bg-[#040915] border border-omnix-blue/40 shadow-[0_0_18px_rgba(0,243,255,0.25)]">
                      <p className="text-omnix-blue text-[11px] tracking-[0.4em] font-hud uppercase">Game Detected</p>
                      <div className="absolute -top-1 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-omnix-blue/60 to-transparent" />
                    </div>
                  </div>

                  <div className="absolute -bottom-9 left-1/2 -translate-x-1/2 flex items-center gap-2 text-[11px] font-hud tracking-[0.3em] uppercase">
                    <Circle className={`w-2.5 h-2.5 ${gameStatus.online ? 'text-green-400 fill-green-400' : 'text-omnix-red fill-omnix-red'} animate-pulse`} />
                    <span className={gameStatus.online ? 'text-green-400' : 'text-omnix-red'}>{gameStatus.online ? 'Online' : 'Offline'}</span>
                  </div>
                </div>
              </div>

              <div className="w-full flex items-center justify-center gap-10">
                <div className="text-center">
                  <p className="text-omnix-blue text-[11px] tracking-[0.35em] font-hud mb-1 uppercase">K/D</p>
                  <p className="text-3xl font-bold text-omnix-text drop-shadow-[0_0_12px_rgba(0,243,255,0.3)]">{gameStatus.kd.toFixed(2)}</p>
                </div>

                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 clip-hexagon border border-omnix-red/50 bg-omnix-red/15 flex items-center justify-center shadow-neon-red">
                    <Crosshair className="w-6 h-6 text-omnix-red" />
                  </div>
                </div>

                <div className="text-center">
                  <p className="text-omnix-blue text-[11px] tracking-[0.35em] font-hud mb-1 uppercase">Wins</p>
                  <p className="text-3xl font-bold text-omnix-text drop-shadow-[0_0_12px_rgba(0,243,255,0.3)]">{gameStatus.wins}</p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className="text-omnix-blue text-[11px] tracking-[0.35em] font-hud mb-1 uppercase">Match</p>
                  <p className="text-xl font-bold text-omnix-text">{gameStatus.matches}</p>
                </div>
                <div className="h-px w-12 bg-gradient-to-r from-transparent via-omnix-blue/50 to-transparent" />
                <div className="flex items-center gap-2 text-omnix-blue/80 text-[11px] tracking-[0.3em] font-hud uppercase">
                  <RefreshCw className="w-4 h-4 animate-spin-slow" />
                  Routing via <span className="text-omnix-text">{activeProvider.toUpperCase()}</span>
                </div>
              </div>

              <div className="text-[10px] font-hud tracking-[0.3em] text-omnix-blue/70 uppercase">
                Scanner: {gameStatus.provider.toUpperCase()}
              </div>
            </div>

            <div className="flex flex-col">
              <Panel className="flex-1 flex flex-col" title="Settings" footer="Settings" subtitle="Control">
                <div className="flex-1 flex flex-col gap-6">
                  <ul className="space-y-3">
                    {settingsMenu.map(item => {
                      const Icon = item.icon;
                      const isActive = activeSetting === item.id;

                      return (
                        <li
                          key={item.id}
                          className={`group cursor-pointer flex items-center justify-between px-3 py-3 rounded-md border transition-all ${
                            isActive
                              ? 'border-omnix-blue bg-omnix-blue/10 shadow-[0_0_18px_rgba(0,243,255,0.18)]'
                              : 'border-omnix-blue/10 hover:border-omnix-blue/40 hover:bg-omnix-blue/5'
                          }`}
                          onClick={() => setActiveSetting(item.id)}
                        >
                          <div className="flex items-center gap-3">
                            <Icon className="w-4 h-4 text-omnix-blue" />
                            <span className="text-omnix-text/90">{item.label}</span>
                          </div>
                          <ChevronRight
                            className={`w-4 h-4 transition-colors ${
                              isActive ? 'text-omnix-blue' : 'text-omnix-blue/50 group-hover:text-omnix-blue'
                            }`}
                          />
                        </li>
                      );
                    })}
                  </ul>

                  <div className="p-4 border border-omnix-blue/25 rounded-md bg-[#050c1a] space-y-4 shadow-[0_0_20px_rgba(0,243,255,0.05)]">
                    {activeSetting === 'overlay' && (
                      <>
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <p className="text-omnix-text font-semibold">Overlay Layout</p>
                            <p className="text-xs text-omnix-blue/60">Switch between focused HUD or immersive view.</p>
                          </div>
                          <div className="flex gap-2">
                            {(['compact', 'immersive'] as const).map(mode => (
                              <button
                                key={mode}
                                onClick={() => setOverlayMode(mode)}
                                className={`px-3 py-2 text-xs rounded-md border ${
                                  overlayMode === mode
                                    ? 'border-omnix-blue bg-omnix-blue/20 text-omnix-blue'
                                    : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/60'
                                }`}
                              >
                                {mode === 'compact' ? 'Compact' : 'Immersive'}
                              </button>
                            ))}
                          </div>
                        </div>
                        <button
                          onClick={() => setLockPosition(prev => !prev)}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm transition-colors ${
                            lockPosition ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2">
                            <Lock className="w-4 h-4" />
                            Lock Overlay Position
                          </span>
                          <span className="uppercase tracking-[0.2em] text-xs">{lockPosition ? 'Locked' : 'Free'}</span>
                        </button>
                      </>
                    )}

                    {activeSetting === 'general' && (
                      <div className="space-y-3">
                        <button
                          onClick={() => toggleSetting('general', 'autoStart')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            generalSettings.autoStart ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><Power className="w-4 h-4" /> Auto-launch on startup</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.autoStart ? 'On' : 'Off'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('general', 'energySaver')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            generalSettings.energySaver ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><Activity className="w-4 h-4" /> Energy saver mode</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.energySaver ? 'On' : 'Off'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('general', 'showTooltips')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            generalSettings.showTooltips ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><SunMoon className="w-4 h-4" /> HUD tooltips</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.showTooltips ? 'On' : 'Off'}</span>
                        </button>
                      </div>
                    )}

                    {activeSetting === 'notifications' && (
                      <div className="space-y-3">
                        <button
                          onClick={() => toggleSetting('notifications', 'desktop')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            notificationSettings.desktop ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><MonitorSmartphone className="w-4 h-4" /> Desktop alerts</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.desktop ? 'On' : 'Off'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('notifications', 'sound')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            notificationSettings.sound ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><Bell className="w-4 h-4" /> Sound cues</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.sound ? 'On' : 'Mute'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('notifications', 'aiUpdates')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            notificationSettings.aiUpdates ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><RefreshCw className="w-4 h-4" /> AI status pings</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.aiUpdates ? 'On' : 'Off'}</span>
                        </button>
                      </div>
                    )}

                    {activeSetting === 'privacy' && (
                      <div className="space-y-3">
                        <button
                          onClick={() => toggleSetting('privacy', 'streamerMode')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            privacySettings.streamerMode ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> Streamer-safe mode</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.streamerMode ? 'On' : 'Off'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('privacy', 'redactLogs')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            privacySettings.redactLogs ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><Lock className="w-4 h-4" /> Redact sensitive logs</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.redactLogs ? 'On' : 'Off'}</span>
                        </button>
                        <button
                          onClick={() => toggleSetting('privacy', 'shareUsage')}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-md border text-sm ${
                            privacySettings.shareUsage ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                          }`}
                        >
                          <span className="flex items-center gap-2"><Circle className="w-4 h-4" /> Share usage metrics</span>
                          <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.shareUsage ? 'On' : 'Off'}</span>
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="mt-4">
                    <div className="flex items-center gap-2 mb-4">
                      <Cpu className="w-4 h-4 text-omnix-blue" />
                      <h4 className="text-omnix-blue font-hud tracking-[0.35em] text-[11px] uppercase">AI Provider</h4>
                    </div>
                    <div className="space-y-3">
                      <div
                        onClick={() => setActiveProvider('synapse')}
                        className={`cursor-pointer px-4 py-3 border rounded-md flex items-center gap-4 transition-all ${
                          activeProvider === 'synapse'
                            ? 'border-omnix-blue bg-omnix-blue/10 shadow-[0_0_14px_rgba(0,243,255,0.2)]'
                            : 'border-omnix-blue/20 hover:border-omnix-blue/50'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            activeProvider === 'synapse' ? 'border-omnix-blue' : 'border-omnix-blue/30'
                          }`}
                        >
                          {activeProvider === 'synapse' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full" />}
                        </div>
                        <span className="font-hud tracking-[0.3em] text-sm text-omnix-text uppercase">Synapse</span>
                      </div>

                      <div
                        onClick={() => setActiveProvider('hybridnex')}
                        className={`cursor-pointer px-4 py-3 border rounded-md flex items-center gap-4 transition-all ${
                          activeProvider === 'hybridnex'
                            ? 'border-omnix-blue bg-omnix-blue/10 shadow-[0_0_14px_rgba(0,243,255,0.2)]'
                            : 'border-omnix-blue/20 hover:border-omnix-blue/50'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            activeProvider === 'hybridnex' ? 'border-omnix-blue' : 'border-omnix-blue/30'
                          }`}
                        >
                          {activeProvider === 'hybridnex' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full" />}
                        </div>
                        <span className="font-hud tracking-[0.3em] text-sm text-omnix-text uppercase">Hybridnex</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Panel>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
