import React from 'react';
import {
  Lock,
  Activity,
  ChevronRight,
  Circle,
  Bell,
  ShieldCheck,
  MonitorSmartphone,
  SunMoon,
  Power,
  RefreshCw,
  Cpu,
} from 'lucide-react';
import Panel from './Panel';

type SettingsPanelProps = {
  activeProvider: string;
  setActiveProvider: (provider: string) => void;
  activeSetting: 'overlay' | 'general' | 'notifications' | 'privacy';
  setActiveSetting: (setting: 'overlay' | 'general' | 'notifications' | 'privacy') => void;
  overlayMode: 'compact' | 'immersive';
  setOverlayMode: (mode: 'compact' | 'immersive') => void;
  lockPosition: boolean;
  setLockPosition: (locked: boolean) => void;
  generalSettings: { autoStart: boolean; energySaver: boolean; showTooltips: boolean };
  notificationSettings: { desktop: boolean; sound: boolean; aiUpdates: boolean };
  privacySettings: { streamerMode: boolean; redactLogs: boolean; shareUsage: boolean };
  toggleSetting: (group: 'general' | 'notifications' | 'privacy', key: any) => void;
  settingsMenu: { id: 'overlay' | 'general' | 'notifications' | 'privacy'; label: string; icon: React.ElementType }[];
};

const SettingsPanel = ({
  activeProvider,
  setActiveProvider,
  activeSetting,
  setActiveSetting,
  overlayMode,
  setOverlayMode,
  lockPosition,
  setLockPosition,
  generalSettings,
  notificationSettings,
  privacySettings,
  toggleSetting,
  settingsMenu,
}: SettingsPanelProps) => (
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
              onClick={() => setLockPosition(!lockPosition)}
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
);

export default SettingsPanel;
