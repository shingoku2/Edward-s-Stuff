import React from 'react';
import CornerBrackets from './CornerBrackets';

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

export default Panel;
