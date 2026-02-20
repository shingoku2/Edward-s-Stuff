import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import './App.css'

interface AppConfig {
  ai_provider: string
  ollama_base_url: string
  ollama_model: string
  overlay_opacity: number
  theme: string
}

interface GameInfo {
  name: string
  exe: string
  process_name: string
  pid: number
  path: string
  version?: string
}

interface MacroStep {
  type: string
  key?: string
  duration_ms?: number
  button?: string
  x?: number
  y?: number
  scroll_amount?: number
}

interface Macro {
  id: string
  name: string
  description: string
  steps: MacroStep[]
  game_profile_id?: string
  repeat: number
  enabled: boolean
}

// Placeholder stats – replace with real game data from backend when available
interface GameStats {
  kd: string
  match: string
  wins: string
}

interface KeybindConfig {
  overlay_hotkey: string
}

interface GameProfile {
  id: string
  display_name: string
  exe_names: string[]
  system_prompt: string
  default_provider: string
  default_model: string | null
  overlay_mode_default: string
  extra_settings?: Record<string, unknown>
  is_builtin?: boolean
}

interface KnowledgeChunk {
  id: string
  text: string
  source_id: string
  pack_id: string
}

const SETTINGS_TABS = ['General', 'Game Profiles', 'Knowledge Packs', 'Keybindings', 'Macros', 'App Appearance', 'Overlay Appearance'] as const
type SettingsTabIndex = 0 | 1 | 2 | 3 | 4 | 5 | 6

function KnowledgePacksTabInline({ gameProfiles, onAdded }: { gameProfiles: GameProfile[]; onAdded: () => void }) {
  const [gameProfileId, setGameProfileId] = useState('')
  const [packId, setPackId] = useState('default')
  const [sourceId, setSourceId] = useState('manual')
  const [text, setText] = useState('')
  const addChunks = () => {
    if (!gameProfileId.trim()) return
    const chunks: KnowledgeChunk[] = text
      .split(/\n\n+/)
      .map((t) => t.trim())
      .filter(Boolean)
      .map((paragraph, i) => ({
        id: `chunk-${Date.now()}-${i}`,
        text: paragraph,
        source_id: sourceId,
        pack_id: packId,
      }))
    if (chunks.length === 0) return
    invoke('knowledge_add_chunks', { gameProfileId, chunks })
      .then(() => { setText(''); onAdded(); })
      .catch(console.error)
  }
  return (
    <div className="settings-form-block">
      <label>Game profile</label>
      <select value={gameProfileId} onChange={(e) => setGameProfileId(e.target.value)}>
        <option value="">Select...</option>
        {gameProfiles.map((p) => (
          <option key={p.id} value={p.id}>{p.display_name || p.id}</option>
        ))}
      </select>
      <label>Pack ID</label>
      <input value={packId} onChange={(e) => setPackId(e.target.value)} />
      <label>Source ID</label>
      <input value={sourceId} onChange={(e) => setSourceId(e.target.value)} />
      <label>Content (paragraphs separated by blank lines)</label>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={5} placeholder="Paste or type text..." />
      <button type="button" className="btn btn-primary" onClick={addChunks}>Add chunks</button>
    </div>
  )
}

function App() {
  const [config, setConfig] = useState<AppConfig | null>(null)
  const [game, setGame] = useState<GameInfo | null>(null)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [macrosOpen, setMacrosOpen] = useState(false)
  const [models, setModels] = useState<string[]>([])
  const [macros, setMacros] = useState<Macro[]>([])
  const [settingsForm, setSettingsForm] = useState({ model: '', theme: 'dark', opacity: 0.95, baseUrl: 'http://localhost:11434' })
  const [settingsTabIndex, setSettingsTabIndex] = useState<SettingsTabIndex>(0)
  const [keybindForm, setKeybindForm] = useState<KeybindConfig>({ overlay_hotkey: 'ctrl+shift+g' })
  const [gameProfiles, setGameProfiles] = useState<GameProfile[]>([])
  const [profileEdit, setProfileEdit] = useState<GameProfile | null>(null)
  const [macroEdit, setMacroEdit] = useState<Macro | null>(null)
  const [macroStepsJson, setMacroStepsJson] = useState('[]')
  const [overlayMode, setOverlayMode] = useState<'compact' | 'full'>('compact')
  const [gameStats, setGameStats] = useState<GameStats>({ kd: '—', match: '—', wins: '—' })

  useEffect(() => {
    invoke<AppConfig>('get_config').then(setConfig).catch(console.error)
    invoke<GameInfo | null>('get_detected_game').then(setGame).catch(console.error)
    invoke<string[]>('list_ollama_models').then(setModels).catch(() => setModels([]))
    invoke<Macro[]>('get_macros').then(setMacros).catch(() => setMacros([]))
    const interval = setInterval(() => {
      invoke<GameInfo | null>('get_detected_game').then(setGame).catch(() => {})
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!config) return
    setSettingsForm((s) => ({
      ...s,
      model: config.ollama_model,
      theme: config.theme,
      opacity: config.overlay_opacity,
      baseUrl: config.ollama_base_url || 'http://localhost:11434',
    }))
  }, [config])

  const openSettings = (tab: SettingsTabIndex = 0) => {
    setSettingsTabIndex(tab)
    setSettingsOpen(true)
    invoke<AppConfig>('get_config').then((c) => { setConfig(c); setSettingsForm((s) => ({ ...s, model: c.ollama_model, theme: c.theme, opacity: c.overlay_opacity, baseUrl: c.ollama_base_url || 'http://localhost:11434' })); }).catch(() => {})
    invoke<KeybindConfig>('get_keybinds').then(setKeybindForm).catch(() => {})
    invoke<GameProfile[]>('get_game_profiles').then(setGameProfiles).catch(() => [])
  }

  useEffect(() => {
    const unlisten = listen<string>('message-received', (e) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: e.payload }])
      setLoading(false)
    })
    return () => {
      unlisten.then((fn) => fn())
    }
  }, [])

  const sendMessage = () => {
    if (!message.trim() || loading) return
    const userMsg = message.trim()
    setMessage('')
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    invoke('send_message', { message: userMsg }).catch((err) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${err}` }])
      setLoading(false)
    })
  }

  const saveSettings = () => {
    invoke('save_settings', {
      settings: {
        ai: { provider: 'ollama', model: settingsForm.model, base_url: settingsForm.baseUrl },
        ui: { theme: settingsForm.theme, opacity: settingsForm.opacity },
      },
    })
      .then(() => {
        invoke<AppConfig>('get_config').then(setConfig)
      })
      .catch(console.error)
  }

  const saveKeybinds = () => {
    invoke('save_keybinds', { config: keybindForm })
      .then(() => {})
      .catch(console.error)
  }

  const toggleOverlay = () => {
    invoke('toggle_overlay').catch(console.error)
  }

  return (
    <div className="app">
      <div className="brand">
        <div className="brand-text">
          <h1 className="brand-title">OMNIX</h1>
          <p className="brand-tagline">-ALL KNOWING AI COMPANION-</p>
        </div>
        <button type="button" className="link-macros" onClick={() => setMacrosOpen(true)}>Macros</button>
      </div>

      <div className="main-grid">
        <section className="panel panel-chat">
          <div className="panel-inner">
            <div className="messages">
              {messages.length === 0 && (
                <p className="placeholder">Ask your gaming assistant anything.</p>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`message-bubble message-${m.role}`}>
                  <div className="message-content">{m.content}</div>
                </div>
              ))}
              {loading && (
                <div className="message-bubble message-assistant">
                  <div className="message-content">Analyzing...</div>
                  <div className="loading-rings">
                    <span className="ring ring-outer" />
                    <span className="ring ring-mid" />
                    <span className="ring ring-inner" />
                    <span className="ring-dot" />
                  </div>
                </div>
              )}
            </div>
            <div className="input-row">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Type a message..."
                disabled={loading}
              />
              <button type="button" className="btn btn-send" onClick={sendMessage} disabled={loading}>
                Send
              </button>
            </div>
          </div>
        </section>

        <section className="panel panel-game">
          <div className="panel-inner">
            <h2 className="panel-heading">GAME DETECTED</h2>
            <div className="game-logo-wrap">
              <div className="game-logo-octagon">
                {game ? (
                  <span className="game-name">{game.name}</span>
                ) : (
                  <span className="game-name game-name-none">No game</span>
                )}
              </div>
            </div>
            <div className="game-status">
              <span className="status-dot" />
              <span>{game ? 'ONLINE' : 'OFFLINE'}</span>
            </div>
            <div className="game-stats">
              <div className="stat-col">
                <span className="stat-label">K/D</span>
                <span className="stat-value stat-positive">{gameStats.kd}</span>
              </div>
              <div className="stat-col">
                <span className="stat-label">MATCH</span>
                <span className="stat-value">{gameStats.match}</span>
              </div>
              <div className="stat-col">
                <span className="stat-label">WINS</span>
                <span className="stat-value stat-wins">{gameStats.wins}</span>
              </div>
            </div>
          </div>
        </section>

        <section className="panel panel-settings">
          <div className="panel-inner">
            <h2 className="panel-heading">
              <span className="heading-icon">⊙</span> SETTINGS
            </h2>
            <ul className="settings-menu">
              <li className={`settings-item ${overlayMode === 'compact' ? 'selected' : ''}`} onClick={() => openSettings(6)}>
                <span className="item-icon">⊕</span>
                <span>Overlay Mode</span>
                <span className="item-chevron">›</span>
              </li>
              <li className="settings-item" onClick={() => openSettings(0)}>
                <span className="item-icon">○</span>
                <span>General</span>
                <span className="item-chevron">›</span>
              </li>
              <li className="settings-item" onClick={() => openSettings(0)}>
                <span className="item-icon">◔</span>
                <span>Notifications</span>
                <span className="item-chevron">›</span>
              </li>
              <li className="settings-item" onClick={() => openSettings(0)}>
                <span className="item-icon">🔒</span>
                <span>Privacy</span>
                <span className="item-chevron">›</span>
              </li>
            </ul>
            <h2 className="panel-heading">
              <span className="heading-icon">◉</span> AI PROVIDER
            </h2>
            <ul className="provider-list">
              <li className="provider-item">
                <span className="item-icon">○</span>
                <span>OLLAMA</span>
              </li>
              <li className="provider-item selected">
                <span className="item-icon">◉</span>
                <span>{config?.ollama_model || 'Model'}</span>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <footer className="bottom-bar">
        <button type="button" className="btn-bottom btn-overlay" onClick={toggleOverlay}>
          OVERLAY
        </button>
        <button type="button" className="btn-bottom btn-settings" onClick={() => openSettings(0)}>
          SETTINGS
        </button>
      </footer>

      {macrosOpen && (
        <div className="modal-overlay" onClick={() => setMacrosOpen(false)}>
          <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
            <h2>Macros</h2>
            <ul className="macro-list">
              {macros.map((m) => (
                <li key={m.id} className="macro-item">
                  <span className="macro-name">{m.name}</span>
                  <span className="macro-desc">{m.description || `${m.steps.length} steps`}</span>
                  <button type="button" className="btn btn-primary btn-sm" onClick={() => { invoke('execute_macro', { macroData: m }); setMacrosOpen(false); }}>
                    Run
                  </button>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => { invoke('delete_macro', { id: m.id }); setMacros((prev) => prev.filter((x) => x.id !== m.id)); }}>
                    Delete
                  </button>
                </li>
              ))}
            </ul>
            {macros.length === 0 && <p className="placeholder">No macros.</p>}
            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setMacrosOpen(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {settingsOpen && (
        <div className="modal-overlay" onClick={() => setSettingsOpen(false)}>
          <div className="modal modal-settings" onClick={(e) => e.stopPropagation()}>
            <h2>Settings</h2>
            <div className="settings-tabs">
              {SETTINGS_TABS.map((label, i) => (
                <button
                  key={label}
                  type="button"
                  className={`settings-tab-btn ${settingsTabIndex === i ? 'active' : ''}`}
                  onClick={() => setSettingsTabIndex(i as SettingsTabIndex)}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="settings-tab-content">
              {settingsTabIndex === 0 && (
                <>
                  <label>Ollama base URL</label>
                  <input
                    type="text"
                    value={settingsForm.baseUrl}
                    onChange={(e) => setSettingsForm((s) => ({ ...s, baseUrl: e.target.value }))}
                    placeholder="http://localhost:11434"
                  />
                  <label>Model</label>
                  <select
                    value={settingsForm.model}
                    onChange={(e) => setSettingsForm((s) => ({ ...s, model: e.target.value }))}
                  >
                    {models.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                    {models.length === 0 && <option value="">No models</option>}
                  </select>
                  <div className="modal-actions">
                    <button type="button" className="btn btn-primary" onClick={saveSettings}>Save</button>
                  </div>
                </>
              )}
              {settingsTabIndex === 1 && (
                <>
                  <div className="settings-section">
                    <button type="button" className="btn btn-primary btn-sm" onClick={() => setProfileEdit({ id: '', display_name: '', exe_names: [], system_prompt: '', default_provider: 'ollama', default_model: null, overlay_mode_default: 'compact', is_builtin: false })}>Add profile</button>
                    <ul className="macro-list">
                      {gameProfiles.map((p) => (
                        <li key={p.id} className="macro-item">
                          <span className="macro-name">{p.display_name}</span>
                          <span className="macro-desc">{p.exe_names.join(', ') || p.id}</span>
                          <button type="button" className="btn btn-primary btn-sm" onClick={() => setProfileEdit({ ...p })}>Edit</button>
                          <button type="button" className="btn btn-ghost btn-sm" onClick={() => { invoke('delete_game_profile', { id: p.id }); setGameProfiles((prev) => prev.filter((x) => x.id !== p.id)); }}>Delete</button>
                        </li>
                      ))}
                    </ul>
                    {gameProfiles.length === 0 && <p className="placeholder">No game profiles.</p>}
                  </div>
                  {profileEdit !== null && (
                    <div className="settings-form-block">
                      <h3>{profileEdit.id ? 'Edit profile' : 'New profile'}</h3>
                      <label>ID</label>
                      <input value={profileEdit.id} onChange={(e) => setProfileEdit((p) => p && { ...p, id: e.target.value })} disabled={!!profileEdit.id} />
                      <label>Display name</label>
                      <input value={profileEdit.display_name} onChange={(e) => setProfileEdit((p) => p && { ...p, display_name: e.target.value })} />
                      <label>Executables (comma-separated)</label>
                      <input value={(profileEdit.exe_names || []).join(', ')} onChange={(e) => setProfileEdit((p) => p && { ...p, exe_names: e.target.value.split(',').map((x) => x.trim()).filter(Boolean) })} />
                      <label>System prompt</label>
                      <textarea value={profileEdit.system_prompt} onChange={(e) => setProfileEdit((p) => p && { ...p, system_prompt: e.target.value })} rows={3} />
                      <label>Default model</label>
                      <input value={profileEdit.default_model || ''} onChange={(e) => setProfileEdit((p) => p && { ...p, default_model: e.target.value || null })} placeholder="ollama model" />
                      <div className="modal-actions">
                        <button type="button" className="btn btn-ghost" onClick={() => setProfileEdit(null)}>Cancel</button>
                        <button type="button" className="btn btn-primary" onClick={() => { invoke('save_game_profile', { profile: profileEdit }).then(() => { setGameProfiles((prev) => { const idx = prev.findIndex((x) => x.id === profileEdit.id); const next = [...prev]; if (idx >= 0) next[idx] = profileEdit; else next.push(profileEdit); return next; }); setProfileEdit(null); }); }}>Save</button>
                      </div>
                    </div>
                  )}
                </>
              )}
              {settingsTabIndex === 2 && (
                <>
                  <p className="placeholder">Add text chunks to the knowledge index for a game profile.</p>
                  <KnowledgePacksTabInline
                    gameProfiles={gameProfiles}
                    onAdded={() => invoke<string[]>('list_ollama_models').then(() => {})}
                  />
                </>
              )}
              {settingsTabIndex === 3 && (
                <>
                  <label>Overlay hotkey</label>
                  <input
                    type="text"
                    value={keybindForm.overlay_hotkey}
                    onChange={(e) => setKeybindForm((k) => ({ ...k, overlay_hotkey: e.target.value }))}
                    placeholder="ctrl+shift+g"
                  />
                  <div className="modal-actions">
                    <button type="button" className="btn btn-primary" onClick={saveKeybinds}>Save</button>
                  </div>
                </>
              )}
              {settingsTabIndex === 4 && (
                <>
                  <div className="settings-section">
                    {macroEdit === null ? (
                      <>
                        <button type="button" className="btn btn-primary btn-sm" onClick={() => { setMacroEdit({ id: `macro-${Date.now()}`, name: '', description: '', steps: [], game_profile_id: undefined, repeat: 1, enabled: true }); setMacroStepsJson('[]'); }}>Create macro</button>
                        <ul className="macro-list">
                          {macros.map((m) => (
                            <li key={m.id} className="macro-item">
                              <span className="macro-name">{m.name}</span>
                              <span className="macro-desc">{m.description || `${m.steps.length} steps`}</span>
                              <button type="button" className="btn btn-primary btn-sm" onClick={() => invoke('execute_macro', { macroData: m })}>Run</button>
                              <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setMacroEdit(m); setMacroStepsJson(JSON.stringify(m.steps.map((s) => ({ type: s.type, key: s.key, duration_ms: s.duration_ms, button: s.button })), null, 2)); }}>Edit</button>
                              <button type="button" className="btn btn-ghost btn-sm" onClick={() => { invoke('delete_macro', { id: m.id }); setMacros((prev) => prev.filter((x) => x.id !== m.id)); }}>Delete</button>
                            </li>
                          ))}
                        </ul>
                      </>
                    ) : (
                      <div className="settings-form-block">
                        <h3>{macroEdit.id.startsWith('macro-') ? 'New macro' : 'Edit macro'}</h3>
                        <label>Name</label>
                        <input value={macroEdit.name} onChange={(e) => setMacroEdit((m) => m && { ...m, name: e.target.value })} />
                        <label>Description</label>
                        <input value={macroEdit.description} onChange={(e) => setMacroEdit((m) => m && { ...m, description: e.target.value })} />
                        <label>{'Steps (JSON: [{"type":"delay","duration_ms":100},{"type":"key_press","key":"h"}])'}</label>
                        <textarea value={macroStepsJson} onChange={(e) => setMacroStepsJson(e.target.value)} rows={4} />
                        <div className="modal-actions">
                          <button type="button" className="btn btn-ghost" onClick={() => setMacroEdit(null)}>Cancel</button>
                          <button
                            type="button"
                            className="btn btn-primary"
                            onClick={() => {
                              try {
                                const steps = JSON.parse(macroStepsJson) as MacroStep[]
                                const macroToSave: Macro = { ...macroEdit, steps }
                                invoke('save_macro', { macroData: macroToSave }).then(() => { setMacros((prev) => prev.filter((x) => x.id !== macroToSave.id).concat([macroToSave])); setMacroEdit(null); }).catch(console.error)
                              } catch (e) {
                                console.error('Invalid steps JSON', e)
                              }
                            }}
                          >
                            Save
                          </button>
                        </div>
                      </div>
                    )}
                    {macros.length === 0 && macroEdit === null && <p className="placeholder">No macros.</p>}
                  </div>
                </>
              )}
              {settingsTabIndex === 5 && (
                <>
                  <label>Theme</label>
                  <select value={settingsForm.theme} onChange={(e) => setSettingsForm((s) => ({ ...s, theme: e.target.value }))}>
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                  </select>
                  <div className="modal-actions">
                    <button type="button" className="btn btn-primary" onClick={saveSettings}>Save</button>
                  </div>
                </>
              )}
              {settingsTabIndex === 6 && (
                <>
                  <label>Overlay opacity</label>
                  <input
                    type="range"
                    min="0.5"
                    max="1"
                    step="0.05"
                    value={settingsForm.opacity}
                    onChange={(e) => setSettingsForm((s) => ({ ...s, opacity: parseFloat(e.target.value) }))}
                  />
                  <span>{settingsForm.opacity}</span>
                  <div className="modal-actions">
                    <button type="button" className="btn btn-primary" onClick={saveSettings}>Save</button>
                  </div>
                </>
              )}
            </div>
            <div className="modal-actions modal-actions-footer">
              <button type="button" className="btn btn-ghost" onClick={() => setSettingsOpen(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
