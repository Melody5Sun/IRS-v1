CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    company TEXT NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    description TEXT NOT NULL,
    url TEXT NOT NULL,
    employment_type TEXT,
    collected_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    raw_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);

CREATE TABLE IF NOT EXISTS company_sources (
    name TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    provider TEXT NOT NULL,
    identifier TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 100,
    last_checked_at TEXT,
    last_status TEXT,
    last_message TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_company_sources_enabled_priority
ON company_sources(enabled, priority, company);

CREATE TABLE IF NOT EXISTS job_analysis (
    job_id INTEGER PRIMARY KEY,
    summary TEXT NOT NULL DEFAULT '',
    responsibilities_json TEXT NOT NULL DEFAULT '[]',
    required_skills_json TEXT NOT NULL DEFAULT '[]',
    preferred_skills_json TEXT NOT NULL DEFAULT '[]',
    employment_type TEXT NOT NULL DEFAULT 'not_stated',
    candidate_type TEXT NOT NULL DEFAULT 'not_stated',
    seniority_level TEXT NOT NULL DEFAULT 'not_stated',
    remote_policy TEXT NOT NULL DEFAULT 'not_stated',
    visa_sponsorship TEXT NOT NULL DEFAULT 'not_stated',
    work_authorization_notes TEXT,
    degree_required TEXT NOT NULL DEFAULT 'not_stated',
    major_required_json TEXT NOT NULL DEFAULT '[]',
    keywords_json TEXT NOT NULL DEFAULT '[]',
    source_evidence_json TEXT NOT NULL DEFAULT '[]',
    analysis_version TEXT NOT NULL DEFAULT '1.0',
    analysis_method TEXT NOT NULL DEFAULT 'not_stated',
    analyzed_at TEXT,
    analysis_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS job_match_features (
    job_id INTEGER PRIMARY KEY,
    normalized_skill_set_json TEXT NOT NULL DEFAULT '[]',
    constraint_flags_json TEXT NOT NULL DEFAULT '{}',
    kg_expanded_skills_json TEXT NOT NULL DEFAULT '[]',
    semantic_embedding_ref TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS job_discovery_preview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discovery_source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    snippet TEXT NOT NULL DEFAULT '',
    source_url TEXT NOT NULL,
    final_url TEXT,
    ats_type TEXT NOT NULL DEFAULT 'unknown',
    jd_quality TEXT NOT NULL DEFAULT 'partial',
    status TEXT NOT NULL DEFAULT 'preview',
    collected_at TEXT NOT NULL,
    raw_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(discovery_source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_job_discovery_preview_source
ON job_discovery_preview(discovery_source);

CREATE INDEX IF NOT EXISTS idx_job_discovery_preview_status
ON job_discovery_preview(status);

CREATE TABLE IF NOT EXISTS company_discovery_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    normalized_company TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_identifier TEXT,
    status TEXT NOT NULL,
    jobs_found_count INTEGER NOT NULL DEFAULT 0,
    message TEXT,
    checked_at TEXT NOT NULL,
    UNIQUE(normalized_company, provider)
);

CREATE INDEX IF NOT EXISTS idx_company_discovery_status_provider
ON company_discovery_status(provider, status);
