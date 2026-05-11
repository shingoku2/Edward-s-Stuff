import { useEffect, useState } from "react";
import { get, post } from "@/lib/api";
import { NeonButton } from "@/components/shared/NeonButton";

interface LicenseStatus {
  valid: boolean;
  message: string;
  dev_mode?: boolean;
}

export function LicenseTab() {
  const [status, setStatus]         = useState<LicenseStatus | null>(null);
  const [key, setKey]               = useState("");
  const [validating, setValidating] = useState(false);
  const [result, setResult]         = useState("");

  useEffect(() => {
    get<LicenseStatus>("/license/status")
      .then(setStatus)
      .catch(() => setStatus({ valid: false, message: "Could not reach server" }));
  }, []);

  const validate = async () => {
    if (!key.trim()) return;
    setValidating(true);
    try {
      const res = await post<LicenseStatus>("/license/validate", { license_key: key.trim() });
      setResult(res.message);
      setStatus(res);
    } catch (e: unknown) {
      setResult(`Error: ${e instanceof Error ? e.message : "unknown"}`);
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <div className="px-4 py-3 rounded-lg border border-omnix-border bg-black/30">
        <p className="font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-1">
          Current Status
        </p>
        {status ? (
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${status.valid ? "bg-omnix-green" : "bg-omnix-red"}`}
            />
            <span className="font-body text-sm text-omnix-text">{status.message}</span>
            {status.dev_mode && (
              <span className="font-display text-[8px] uppercase text-omnix-cyan border border-omnix-cyan/30 px-1 py-0.5 rounded">
                Dev
              </span>
            )}
          </div>
        ) : (
          <span className="font-body text-sm text-omnix-muted/50">Loading...</span>
        )}
      </div>

      <div>
        <label className="block font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-2">
          License Key
        </label>
        <input
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="XXXX-XXXX-XXXX-XXXX"
          className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60 tracking-widest"
        />
      </div>

      <div className="flex items-center gap-3">
        <NeonButton onClick={validate} disabled={validating || !key.trim()}>
          {validating ? "Validating..." : "Validate License"}
        </NeonButton>
        {result && (
          <span className="font-display text-[9px] uppercase text-omnix-cyan">{result}</span>
        )}
      </div>
    </div>
  );
}
