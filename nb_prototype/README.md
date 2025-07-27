## Notebook prototype of the app

Currently finds the first relevant source and just uses that as additional context

Improvements todo:
- use search APIs rather than google html scraping [DONE]
- improve search response time [DONE]
- add conversation memory [DONE]
- allow system to gather more external context if needed
- (lower priority) improve system prompt
- (lower priority) use site-specific APIs for popular sites like reddit - requests doesn't read
    comments seemingly
- (lower priority) better system pipeline, i.e. multiple search queries, context sufficiency priority scores, etc.