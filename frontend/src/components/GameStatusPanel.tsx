import React from 'react';
import { Crosshair, Circle, RefreshCw } from 'lucide-react';

type GameStatus = {
  name: string;
  mode: string;
  kd: number;
  wins: number;
  matches: number;
  online: boolean;
  provider: string;
};

type GameStatusPanelProps = {
  gameStatus: GameStatus;
  activeProvider: string;
};

const GameStatusPanel = ({ gameStatus, activeProvider }: GameStatusPanelProps) => (
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
);

export default GameStatusPanel;
