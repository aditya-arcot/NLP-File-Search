-- connect
\c :DB_NAME

-- load extensions
CREATE EXTENSION pg_trgm;
CREATE EXTENSION vector;

CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    file_path VARCHAR(255)
);

CREATE TABLE tokens (
	token_id SERIAL PRIMARY KEY,
	token_name VARCHAR(255),
	embedding vector(300)
);

CREATE TABLE mapping (
	id SERIAL PRIMARY KEY,
	file_id INTEGER REFERENCES files(file_id),
	token_id INTEGER REFERENCES tokens(token_id)
);

-- trigram-based GIN index on file path
CREATE INDEX path_tgrm_idx ON files USING gin (file_path gin_trgm_ops);
CREATE INDEX token_name_idx ON tokens (token_name);
-- HNSW index for vector similarity
CREATE INDEX ON tokens USING hnsw (embedding vector_cosine_ops);
