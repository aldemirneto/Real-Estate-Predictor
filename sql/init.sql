-- ── lookup tables ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS bairro (
    bairroid   SERIAL PRIMARY KEY,
    bairrodesc VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS status (
    statusid   SERIAL PRIMARY KEY,
    statusdesc VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS imobiliaria (
    imobiliariaid   SERIAL PRIMARY KEY,
    imobiliariadesc VARCHAR(120) NOT NULL UNIQUE
);

-- ── staging table (truncated + reloaded on every scrape run) ─────────────────

CREATE TABLE IF NOT EXISTS temp_imovel (
    id           SERIAL PRIMARY KEY,
    preco        NUMERIC(15, 2),
    area         NUMERIC(10, 2),
    quartos      VARCHAR(10),
    vagas        VARCHAR(10),
    banheiros    VARCHAR(10),
    bairro       INTEGER REFERENCES bairro(bairroid),
    "Status"     INTEGER REFERENCES status(statusid),
    "Data_scrape" DATE,
    last_seen    DATE,
    link         TEXT,
    tipo         VARCHAR(60),
    cidade       VARCHAR(120) NOT NULL DEFAULT 'Piracicaba',
    uf           CHAR(2) NOT NULL DEFAULT 'SP',
    "Imobiliaria" INTEGER REFERENCES imobiliaria(imobiliariaid)
);

-- ── main imovel table (deduplicated, historical) ──────────────────────────────

CREATE TABLE IF NOT EXISTS imovel (
    id           SERIAL PRIMARY KEY,
    preco        NUMERIC(15, 2),
    area         NUMERIC(10, 2),
    quartos      VARCHAR(10),
    vagas        VARCHAR(10),
    banheiros    VARCHAR(10),
    bairro       INTEGER REFERENCES bairro(bairroid),
    status       INTEGER REFERENCES status(statusid),
    data_scrape  DATE NOT NULL DEFAULT CURRENT_DATE,
    last_seen    DATE NOT NULL DEFAULT CURRENT_DATE,
    link         TEXT UNIQUE,
    tipo         VARCHAR(60),
    cidade       VARCHAR(120) NOT NULL DEFAULT 'Piracicaba',
    uf           CHAR(2) NOT NULL DEFAULT 'SP',
    imobiliaria  INTEGER REFERENCES imobiliaria(imobiliariaid)
);

-- ── seed lookup values ────────────────────────────────────────────────────────

INSERT INTO status (statusdesc) VALUES ('Compra'), ('Aluguel')
    ON CONFLICT (statusdesc) DO NOTHING;
