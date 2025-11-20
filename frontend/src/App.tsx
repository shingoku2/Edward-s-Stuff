import React, { useState } from 'react';
import {
  Settings, Bell, Lock, Activity,
  Send, Crosshair, Trophy, Cpu, Layers, ChevronRight, Circle
} from 'lucide-react';

// Geometric Corner Brackets Component
const CornerBrackets = () => (
  <>
    {/* Top Left */}
    <div className="absolute -top-[1px] -left-[1px] w-12 h-12">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent"></div>
      <div className="absolute top-0 left-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent"></div>
      <div className="absolute top-2 left-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute top-2 left-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Top Right */}
    <div className="absolute -top-[1px] -right-[1px] w-12 h-12">
      <div className="absolute top-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent"></div>
      <div className="absolute top-0 right-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent"></div>
      <div className="absolute top-2 right-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute top-2 right-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Bottom Left */}
    <div className="absolute -bottom-[1px] -left-[1px] w-12 h-12">
      <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-0 left-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-2 left-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute bottom-2 left-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Bottom Right */}
    <div className="absolute -bottom-[1px] -right-[1px] w-12 h-12">
      <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-0 right-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-2 right-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute bottom-2 right-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
  </>
);

// Reusable HUD Panel Component
const Panel = ({ children, className = "", title, footer }: { children: React.ReactNode, className?: string, title?: string, footer?: string }) => (
  <div className={`relative bg-omnix-panel border border-omnix-blue/20 rounded-sm p-6 backdrop-blur-md ${className}`}>
    <CornerBrackets />

    {title && (
      <h3 className="text-omnix-blue font-hud tracking-[0.3em] text-xs mb-6 uppercase">
        {title}
      </h3>
    )}
    {children}
    {footer && (
      <div className="mt-6 pt-4 border-t border-omnix-blue/10">
        <p className="text-center text-omnix-blue/50 font-hud tracking-[0.3em] text-xs uppercase">
          {footer}
        </p>
      </div>
    )}
  </div>
);

export default function OmnixHUD() {
  const [activeProvider, setActiveProvider] = useState('hybridnex');

  return (
    <div className="min-h-screen bg-omnix-dark text-omnix-text font-body p-8 flex items-center justify-center bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]">
      {/* Main HUD Container */}
      <div className="w-full max-w-7xl relative">
        <div className="relative border border-omnix-blue/30 rounded-sm p-8 bg-omnix-dark/95 backdrop-blur-lg">
          <CornerBrackets />

          {/* Header */}
          <header className="mb-10 relative">
            <div className="flex items-center gap-4">
              {/* Left decorative line */}
              <div className="flex-1 flex items-center gap-1">
                <div className="h-[2px] flex-1 bg-gradient-to-r from-transparent via-omnix-blue/50 to-omnix-blue"></div>
                <div className="w-2 h-2 border border-omnix-blue rotate-45"></div>
                <div className="w-1 h-1 bg-omnix-blue"></div>
              </div>

              {/* Logo */}
              <div className="text-center">
                <h1 className="text-7xl font-hud font-black tracking-wider">
                  <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-omnix-blue to-omnix-blue drop-shadow-[0_0_20px_rgba(0,243,255,0.8)]">
                    OMNIX
                  </span>
                </h1>
                <p className="text-omnix-blue tracking-[0.4em] text-xs font-hud mt-2 uppercase opacity-80">
                  - All Knowing AI Companion -
                </p>
              </div>

              {/* Right decorative line */}
              <div className="flex-1 flex items-center gap-1">
                <div className="w-1 h-1 bg-omnix-blue"></div>
                <div className="w-2 h-2 border border-omnix-blue rotate-45"></div>
                <div className="h-[2px] flex-1 bg-gradient-to-l from-transparent via-omnix-blue/50 to-omnix-blue"></div>
              </div>
            </div>
          </header>

        <div className="grid grid-cols-12 gap-6 h-[600px]">

          {/* LEFT COLUMN: Chat/Overlay */}
          <div className="col-span-3 flex flex-col">
            <Panel className="flex-1 flex flex-col" footer="OVERLAY">
              <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                {/* AI Message */}
                <div className="bg-omnix-blueDim/50 border-l-2 border-omnix-blue p-3 rounded-sm">
                  <p className="text-omnix-blue text-sm font-body">Hello!</p>
                </div>
                {/* User Message */}
                <div className="bg-white/5 border-l-2 border-white/30 p-3 rounded-sm">
                  <p className="text-omnix-text text-sm">HII How can I assist-you?</p>
                </div>
                {/* AI Processing with spinner */}
                <div className="bg-omnix-blueDim/50 border-l-2 border-omnix-blue p-3 rounded-sm">
                  <div className="flex items-center gap-3">
                    <div className="relative w-8 h-8">
                      <div className="absolute inset-0 border-2 border-omnix-blue/20 rounded-full"></div>
                      <div className="absolute inset-0 border-t-2 border-omnix-blue rounded-full animate-spin"></div>
                      <div className="absolute inset-2 border border-dashed border-omnix-blue/40 rounded-full"></div>
                    </div>
                    <p className="text-omnix-blue text-sm">Sure, analyzing the game now...</p>
                  </div>
                </div>
              </div>
            </Panel>
          </div>

          {/* CENTER COLUMN: Game Detection */}
          <div className="col-span-5 flex flex-col items-center justify-center relative gap-8">
            {/* Hexagonal Frame */}
            <div className="relative">
              {/* Outer hexagonal border */}
              <div className="relative w-72 h-72 flex items-center justify-center">
                <div className="absolute inset-0 clip-hexagon-border border-2 border-omnix-blue/40"></div>

                {/* Animated rotating ring */}
                <div className="absolute inset-3">
                  <div className="absolute inset-0 border-2 border-omnix-blue/20 rounded-full"></div>
                  <div className="absolute inset-0 border-t-2 border-omnix-blue rounded-full animate-spin-slow"></div>
                </div>

                {/* Inner content circle */}
                <div className="relative w-48 h-48 rounded-full border-2 border-omnix-blue/30 flex items-center justify-center bg-omnix-panel">
                  <div className="text-center z-10">
                    {/* CS:GO Icon placeholder */}
                    <div className="mx-auto w-20 h-20 mb-3 flex items-center justify-center">
                      <Crosshair className="w-full h-full text-omnix-red drop-shadow-[0_0_10px_rgba(255,42,42,0.6)]" />
                    </div>
                  </div>
                </div>

                {/* Top label */}
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                  <div className="relative px-4 py-1 bg-omnix-dark border-l border-r border-omnix-blue/40">
                    <p className="text-omnix-blue text-xs tracking-[0.3em] font-hud uppercase">Game Detected</p>
                    <div className="absolute -top-1 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-omnix-blue/60 to-transparent"></div>
                  </div>
                </div>

                {/* Bottom status */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex items-center gap-2">
                  <Circle className="w-2 h-2 text-green-500 fill-green-500 animate-pulse" />
                  <span className="text-green-400 text-xs tracking-widest uppercase">Online</span>
                </div>
              </div>
            </div>

            {/* Stats Row */}
            <div className="w-full flex items-center justify-center gap-8">
              {/* K/D Stat */}
              <div className="text-center">
                <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">K/D</p>
                <p className="text-2xl font-bold text-omnix-text">1.52</p>
              </div>

              {/* Center Hexagon Icon */}
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 clip-hexagon border-2 border-omnix-red/60 bg-omnix-red/10 flex items-center justify-center">
                  <Crosshair className="w-6 h-6 text-omnix-red" />
                </div>
              </div>

              {/* Wins Stat */}
              <div className="text-center">
                <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">Wins</p>
                <p className="text-2xl font-bold text-omnix-text">∞</p>
              </div>
            </div>

            {/* Match stat */}
            <div className="text-center">
              <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">Match</p>
              <p className="text-xl font-bold text-omnix-text">24</p>
            </div>
          </div>

          {/* RIGHT COLUMN: Settings */}
          <div className="col-span-4 flex flex-col">
            <Panel className="flex-1 flex flex-col" title="SETTINGS" footer="SETTINGS">
              <div className="flex-1 flex flex-col gap-6">
                {/* Settings Menu */}
                <ul className="space-y-3">
                  <li className="group cursor-pointer flex items-center justify-between px-3 py-3 hover:bg-omnix-blue/5 border border-transparent hover:border-omnix-blue/20 transition-all rounded-sm">
                    <div className="flex items-center gap-3">
                      <Circle className="w-4 h-4 text-omnix-blue" />
                      <span className="text-omnix-text">Overlay Mode</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-omnix-blue/50 group-hover:text-omnix-blue transition-colors" />
                  </li>
                  <li className="group cursor-pointer flex items-center justify-between px-3 py-3 hover:bg-omnix-blue/5 border border-transparent hover:border-omnix-blue/20 transition-all rounded-sm">
                    <div className="flex items-center gap-3">
                      <Circle className="w-4 h-4 text-omnix-blue" />
                      <span className="text-omnix-text">General</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-omnix-blue/50 group-hover:text-omnix-blue transition-colors" />
                  </li>
                  <li className="group cursor-pointer flex items-center justify-between px-3 py-3 hover:bg-omnix-blue/5 border border-transparent hover:border-omnix-blue/20 transition-all rounded-sm">
                    <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-omnix-blue" />
                      <span className="text-omnix-text">Notifications</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-omnix-blue/50 group-hover:text-omnix-blue transition-colors" />
                  </li>
                  <li className="group cursor-pointer flex items-center justify-between px-3 py-3 hover:bg-omnix-blue/5 border border-transparent hover:border-omnix-blue/20 transition-all rounded-sm">
                    <div className="flex items-center gap-3">
                      <Lock className="w-4 h-4 text-omnix-blue" />
                      <span className="text-omnix-text">Privacy</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-omnix-blue/50 group-hover:text-omnix-blue transition-colors" />
                  </li>
                </ul>

                {/* AI Provider Section */}
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Cpu className="w-4 h-4 text-omnix-blue" />
                    <h4 className="text-omnix-blue font-hud tracking-[0.3em] text-xs uppercase">AI Provider</h4>
                  </div>
                  <div className="space-y-3">
                    <div
                      onClick={() => setActiveProvider('synapse')}
                      className={`cursor-pointer px-4 py-3 border rounded-sm flex items-center gap-4 transition-all ${activeProvider === 'synapse' ? 'border-omnix-blue bg-omnix-blue/5' : 'border-omnix-blue/20 hover:border-omnix-blue/40'}`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${activeProvider === 'synapse' ? 'border-omnix-blue' : 'border-omnix-blue/30'}`}>
                        {activeProvider === 'synapse' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full"></div>}
                      </div>
                      <span className="font-hud tracking-widest text-sm text-omnix-text">SYNAPSE</span>
                    </div>

                    <div
                      onClick={() => setActiveProvider('hybridnex')}
                      className={`cursor-pointer px-4 py-3 border rounded-sm flex items-center gap-4 transition-all ${activeProvider === 'hybridnex' ? 'border-omnix-blue bg-omnix-blue/5' : 'border-omnix-blue/20 hover:border-omnix-blue/40'}`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${activeProvider === 'hybridnex' ? 'border-omnix-blue' : 'border-omnix-blue/30'}`}>
                         {activeProvider === 'hybridnex' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full"></div>}
                      </div>
                      <span className="font-hud tracking-widest text-sm text-omnix-text">HYBRIDNEX</span>
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
