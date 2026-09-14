-- Apply to existing databases BEFORE running the updated scraper/API.
BEGIN;
ALTER TABLE public.temp_imovel ADD COLUMN IF NOT EXISTS cidade VARCHAR(120) NOT NULL DEFAULT 'Piracicaba';
ALTER TABLE public.temp_imovel ADD COLUMN IF NOT EXISTS uf CHAR(2) NOT NULL DEFAULT 'SP';
ALTER TABLE public.imovel ADD COLUMN IF NOT EXISTS cidade VARCHAR(120) NOT NULL DEFAULT 'Piracicaba';
ALTER TABLE public.imovel ADD COLUMN IF NOT EXISTS uf CHAR(2) NOT NULL DEFAULT 'SP';
CREATE INDEX IF NOT EXISTS imovel_cidade_idx ON public.imovel(cidade);
COMMIT;
-- Reapply security.sql after this migration to update API views.
