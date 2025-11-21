import React, { useEffect, useMemo, useState } from 'react';
import { Bell, MonitorSmartphone, ShieldCheck, SunMoon } from 'lucide-react';
import CornerBrackets from './components/CornerBrackets';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import GameStatusPanel from './components/GameStatusPanel';
import SettingsPanel from './components/SettingsPanel';

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
          <Header gameStatus={gameStatus} />

          <div className="grid grid-cols-[330px_minmax(420px,1fr)_330px] gap-6">
            <div className="flex flex-col">
              <ChatPanel
                messages={messages}
                chatInput={chatInput}
                setChatInput={setChatInput}
                appendMessage={appendMessage}
                activeProvider={activeProvider}
              />
            </div>

            <GameStatusPanel gameStatus={gameStatus} activeProvider={activeProvider} />

            <div className="flex flex-col">
              <SettingsPanel
                activeProvider={activeProvider}
                setActiveProvider={setActiveProvider}
                activeSetting={activeSetting}
                setActiveSetting={setActiveSetting}
                overlayMode={overlayMode}
                setOverlayMode={setOverlayMode}
                lockPosition={lockPosition}
                setLockPosition={setLockPosition}
                generalSettings={generalSettings}
                notificationSettings={notificationSettings}
                privacySettings={privacySettings}
                toggleSetting={toggleSetting}
                settingsMenu={settingsMenu}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}