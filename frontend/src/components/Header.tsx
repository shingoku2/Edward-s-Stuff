import React from 'react';
import { Wifi } from 'lucide-react';

type HeaderProps = {
  gameStatus: {
    online: boolean;
  };
};

const Header = ({ gameStatus }: HeaderProps) => (
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
);

export default Header;
