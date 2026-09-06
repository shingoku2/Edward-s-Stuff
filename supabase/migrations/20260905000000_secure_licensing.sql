create table if not exists public.license_installations (
    license_id uuid not null references public.licenses(id) on delete cascade,
    installation_id uuid not null,
    last_seen_at timestamptz not null default now(),
    primary key (license_id, installation_id)
);

alter table public.licenses enable row level security;
alter table public.license_installations enable row level security;
revoke all on table public.licenses from anon, authenticated;
revoke all on table public.license_installations from anon, authenticated;

comment on table public.license_installations is
    'Private license seats managed only by the validate-license Edge Function.';
