export function ScanLine() {
  return (
    <div className="fixed inset-0 pointer-events-none z-10 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.8) 2px, rgba(0,0,0,0.8) 4px)",
        }}
      />
      <div className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-omnix-cyan/20 to-transparent animate-scan" />
    </div>
  );
}
