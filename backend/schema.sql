-- SQLite schema (also compatible with SQLAlchemy models)

CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rss_url TEXT UNIQUE NOT NULL,
    base_credibility_score REAL NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    published_at DATETIME,
    raw_text TEXT NOT NULL,
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE user_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    goal_text TEXT NOT NULL,
    embedding_vector BLOB -- Will store numpy array bytes or JSON depending on implementation
);

CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL UNIQUE,
    credibility_score REAL NOT NULL,
    credibility_reasons TEXT, -- JSON
    relevance_score REAL NOT NULL,
    summary TEXT,
    matched_goal_id INTEGER,
    FOREIGN KEY(article_id) REFERENCES articles(id),
    FOREIGN KEY(matched_goal_id) REFERENCES user_goals(id)
);

CREATE TABLE briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL,
    article_ids TEXT NOT NULL, -- JSON ordered list of IDs
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
