-- Feedback database for UAV Manufacturing Readiness & Scale-up Kit
-- Run once in the Supabase SQL Editor.

create extension if not exists pgcrypto;

create table if not exists public.feedback (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    app_version text not null,
    source text not null default 'streamlit_app',
    session_id uuid not null,
    assessment_stage text,
    role text,
    rating smallint check (rating between 1 and 5),
    assessment_useful text check (assessment_useful in ('yes', 'partly', 'no')),
    feedback_type text,
    comment text,
    improvement_request text,
    status text not null default 'new',
    ai_theme text,
    ai_priority text,
    ai_summary text,
    ai_recommended_action text,
    github_issue_url text,
    metadata jsonb not null default '{}'::jsonb
);

create index if not exists feedback_created_at_idx on public.feedback (created_at desc);
create index if not exists feedback_status_idx on public.feedback (status);
create index if not exists feedback_type_idx on public.feedback (feedback_type);
create index if not exists feedback_rating_idx on public.feedback (rating);
create index if not exists feedback_ai_theme_idx on public.feedback (ai_theme);

alter table public.feedback enable row level security;

revoke all on public.feedback from anon, authenticated;
grant insert on public.feedback to anon, authenticated;

-- Public app users may submit feedback but may not read, update or delete rows.
drop policy if exists "allow feedback insert" on public.feedback;
create policy "allow feedback insert"
on public.feedback
for insert
to anon, authenticated
with check (true);

comment on table public.feedback is
'Structured product feedback. Does not store manufacturing-assessment answers or company technical data.';
