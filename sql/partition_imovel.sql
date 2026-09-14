-- ═══════════════════════════════════════════════════════════════════════════
-- PARTITION imovel BY YEAR (data_scrape)
-- ⚠  Run in a maintenance window — rewrites the table.
-- ═══════════════════════════════════════════════════════════════════════════

BEGIN;

-- 1. Rename old table
ALTER TABLE public.imovel RENAME TO imovel_old;

-- 2. Create partitioned table with the same structure
CREATE TABLE public.imovel (
    id           SERIAL,
    preco        NUMERIC(15, 2),
    area         NUMERIC(10, 2),
    quartos      VARCHAR(10),
    vagas        VARCHAR(10),
    banheiros    VARCHAR(10),
    bairro       INTEGER REFERENCES public.bairro(bairroid),
    status       INTEGER REFERENCES public.status(statusid),
    data_scrape  DATE NOT NULL DEFAULT CURRENT_DATE,
    last_seen    DATE NOT NULL DEFAULT CURRENT_DATE,
    link         TEXT,
    tipo         VARCHAR(60),
    imobiliaria  INTEGER REFERENCES public.imobiliaria(imobiliariaid),
    PRIMARY KEY (id, data_scrape)
) PARTITION BY RANGE (data_scrape);

-- Unique constraint must include partition key
CREATE UNIQUE INDEX imovel_link_date_uidx ON public.imovel (link, data_scrape);

-- 3. Create yearly partitions (add more as needed)
CREATE TABLE public.imovel_2023
    PARTITION OF public.imovel
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE public.imovel_2024
    PARTITION OF public.imovel
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE public.imovel_2025
    PARTITION OF public.imovel
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE public.imovel_2026
    PARTITION OF public.imovel
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Catch-all for future dates
CREATE TABLE public.imovel_future
    PARTITION OF public.imovel
    FOR VALUES FROM ('2027-01-01') TO ('2099-01-01');

-- 4. Migrate data
INSERT INTO public.imovel
    SELECT * FROM public.imovel_old;

-- 5. Indexes on each partition (Postgres propagates to partitions automatically)
CREATE INDEX ON public.imovel (bairro);
CREATE INDEX ON public.imovel (data_scrape);
CREATE INDEX ON public.imovel (status);

-- 6. Re-enable RLS on the new partitioned table
ALTER TABLE public.imovel ENABLE ROW LEVEL SECURITY;

CREATE POLICY scraper_all ON public.imovel
    FOR ALL TO postgres USING (true);

-- 7. Drop old table (only after verifying counts match!)
-- Uncomment when confident:
-- DROP TABLE public.imovel_old;

COMMIT;
