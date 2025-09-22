MERGE `<DATASET>.missing_persons` AS target
USING (
  SELECT 
    id,
    ml_generate_embedding_result as new_embedding
  FROM ML.GENERATE_EMBEDDING(
    MODEL `<DATASET>.text_embedding_model`,
    (SELECT id, ml_summary as content FROM `<DATASET>.missing_persons` WHERE ml_summary IS NOT NULL AND (ml_summary_embedding IS NULL OR ARRAY_LENGTH(ml_summary_embedding) = 0)),
    STRUCT('SEMANTIC_SIMILARITY' as task_type)
  )
) AS source
ON target.id = source.id
WHEN MATCHED THEN
  UPDATE SET 
    ml_summary_embedding = source.new_embedding,
    updated_date = CURRENT_TIMESTAMP();