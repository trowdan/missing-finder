/* Create text embedding model for generating embeddings from missing person summaries */

CREATE OR REPLACE MODEL `homeward.text_embedding_model`
REMOTE WITH CONNECTION `bq-ai-hackaton.us-central1.homeward_gcp_connection`
OPTIONS (
  endpoint = 'text-embedding-004'
);