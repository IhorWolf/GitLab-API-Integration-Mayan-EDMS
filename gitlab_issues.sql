CREATE TABLE IF NOT EXISTS gitlab_issues (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER UNIQUE,
    title TEXT,
    state TEXT,
    created_at TIMESTAMP,
    closed_at TIMESTAMP,
    run_date DATE DEFAULT CURRENT_DATE
);