import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const headers = {
  "content-type": "application/json",
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "authorization, apikey, content-type",
};

Deno.serve(async (request) => {
  if (request.method === "OPTIONS") return new Response("ok", { headers });
  if (request.method !== "POST") {
    return Response.json({ valid: false, message: "Method not allowed." }, { status: 405, headers });
  }
  try {
    const { license_key, installation_id } = await request.json();
    if (typeof license_key !== "string" || typeof installation_id !== "string") {
      return Response.json({ valid: false, message: "Invalid request." }, { status: 400, headers });
    }
    const admin = createClient(
      Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
      { auth: { persistSession: false } },
    );
    const { data, error } = await admin.from("licenses")
      .select("id,status,expires_at,seat_limit").eq("key", license_key).maybeSingle();
    if (error) throw error;
    if (!data) return Response.json({ valid: false, message: "License key not found." }, { status: 404, headers });
    if (data.status !== "active") {
      return Response.json({ valid: false, message: `License is ${data.status}.` }, { status: 403, headers });
    }
    if (data.expires_at && new Date(data.expires_at) < new Date()) {
      return Response.json({ valid: false, message: "License expired." }, { status: 403, headers });
    }
    const { data: seats, error: seatError } = await admin.from("license_installations")
      .select("installation_id").eq("license_id", data.id);
    if (seatError) throw seatError;
    const registered = seats?.some((seat) => seat.installation_id === installation_id);
    if (!registered && (seats?.length ?? 0) >= (data.seat_limit ?? 1)) {
      return Response.json({ valid: false, message: "License seat limit reached." }, { status: 409, headers });
    }
    await admin.from("license_installations").upsert(
      { license_id: data.id, installation_id, last_seen_at: new Date().toISOString() },
      { onConflict: "license_id,installation_id" },
    );
    return Response.json({ valid: true, message: "License valid." }, { headers });
  } catch (error) {
    console.error("license validation failed", error);
    return Response.json({ valid: false, message: "License service error." }, { status: 500, headers });
  }
});
