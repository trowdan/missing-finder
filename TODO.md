- Add logging (right now exceptions are logged as notifications)
- after the modification, the ml summary and embeddings should be resetted-
- Insert in the documentation Video intelligence buzzwords
- The video object external table in big query contains a repeted field called "metadata" with field "name" and "value". the most interesting field
  are named "timestamp", "latitude" and "longitude". I want to leverage these field to modify the video intelligent search. In the UI in the case
  detail page I  have a "radius" from the case last seeing position, and I want to filter the scanned videos before running the Gemini analysis. Same
  for start date and end date and Time range field. Let's start with the date filtering as it simpler 