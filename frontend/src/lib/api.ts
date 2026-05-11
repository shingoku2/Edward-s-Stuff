const BASE   = `http://localhost:${import.meta.env.VITE_OMNIX_PORT ?? "7432"}/api/v2`;
const WS_URL = `ws://localhost:${import.meta.env.VITE_OMNIX_PORT ?? "7432"}/ws`;

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const get  = <T>(path: string) => api<T>(path);
export const post = <T>(path: string, body: unknown) =>
  api<T>(path, { method: "POST", body: JSON.stringify(body) });
export const del  = <T>(path: string) => api<T>(path, { method: "DELETE" });
export { WS_URL };
