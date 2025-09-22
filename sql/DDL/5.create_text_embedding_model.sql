/* Create text embedding model for generating embeddings from missing person summaries */

CREATE OR REPLACE MODEL `<DATASET>.text_embedding_model`
REMOTE WITH CONNECTION `<PROJECT_ID>.<REGION>.<CONNECTION_NAME>`
OPTIONS (
  endpoint = 'text-embedding-004'
);