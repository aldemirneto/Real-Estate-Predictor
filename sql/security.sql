-- ═══════════════════════════════════════════════════════════════════════════
-- DATABASE SECURITY HARDENING
-- Run once as superuser (postgres) after init.sql
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 1. API schema — the web app only ever sees this schema ────────────────

CREATE SCHEMA IF NOT EXISTS api;

-- ── 2. Read-only role for the web application ─────────────────────────────

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 're_web_reader') THEN
        CREATE ROLE re_web_reader NOLOGIN NOINHERIT NOCREATEDB NOCREATEROLE;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 're_web_app') THEN
        CREATE ROLE re_web_app LOGIN PASSWORD 'CHANGE_ME_BEFORE_DEPLOY' INHERIT;
    END IF;
END $$;

ALTER ROLE re_web_app INHERIT;
GRANT re_web_reader TO re_web_app;

-- Lock out of public schema completely
REVOKE ALL ON SCHEMA public FROM re_web_reader;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM re_web_reader;

-- Allow usage of api schema only
GRANT USAGE ON SCHEMA api TO re_web_reader;

-- ── 3. Masked views in api schema ─────────────────────────────────────────
-- The web app never touches raw tables directly.
-- Columns are typed explicitly and link is validated to http(s) only.

CREATE OR REPLACE VIEW api.imovel AS
SELECT
    i.id,
    i.preco::DOUBLE PRECISION                               AS preco,
    i.area::DOUBLE PRECISION                                AS area,
    i.quartos::INTEGER                                      AS quartos,
    i.vagas::INTEGER                                        AS vagas,
    i.banheiros::INTEGER                                    AS banheiros,
    -- mask links that are not plain http/https (defence against stored XSS)
    CASE
        WHEN i.link ~* '^https?://'  THEN i.link
        ELSE NULL
    END                                                     AS link,
    i.tipo,
    i.data_scrape,
    i.last_seen,
    b.bairrodesc                                            AS bairro,
    s.statusdesc                                            AS status,
    im.imobiliariadesc                                      AS imobiliaria,
    i.cidade, i.uf
FROM public.imovel      i
JOIN public.bairro      b  ON b.bairroid       = i.bairro
JOIN public.status      s  ON s.statusid       = i.status
JOIN public.imobiliaria im ON im.imobiliariaid = i.imobiliaria;

CREATE OR REPLACE VIEW api.bairro AS
SELECT bairroid, bairrodesc FROM public.bairro;

CREATE OR REPLACE VIEW api.stats AS
SELECT
    b.bairrodesc                                                AS bairro,
    ROUND(AVG(i.preco::NUMERIC / NULLIF(i.area::NUMERIC, 0)), 2) AS preco_m2,
    ROUND(AVG(i.area::NUMERIC), 2)                              AS area_media,
    COUNT(*)                                                    AS total
FROM public.imovel i
JOIN public.bairro b ON b.bairroid = i.bairro
WHERE i.area::NUMERIC > 0
  AND i.preco IS NOT NULL
GROUP BY b.bairrodesc;

-- Grant SELECT only on api schema views
GRANT SELECT ON ALL TABLES IN SCHEMA api TO re_web_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA api FOR ROLE postgres
    GRANT SELECT ON TABLES TO re_web_reader;

-- ── 4. Row-level security on the raw imovel table ─────────────────────────
-- Even if someone bypasses the view and hits the table directly,
-- re_web_reader cannot read it (no privilege). RLS is an extra layer
-- for roles that DO have table access (e.g. scraper role).

ALTER TABLE public.imovel ENABLE ROW LEVEL SECURITY;

-- Scraper role can see all rows; everyone else sees nothing
-- (The app role never touches the raw table so this is defence-in-depth)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_policies WHERE tablename = 'imovel' AND policyname = 'scraper_all'
    ) THEN
        CREATE POLICY scraper_all ON public.imovel
            FOR ALL TO postgres USING (true);
    END IF;
END $$;

-- ── 5. Revoke dangerous privileges from public ────────────────────────────
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE real_estate FROM PUBLIC;
GRANT CONNECT ON DATABASE real_estate TO re_web_app;
