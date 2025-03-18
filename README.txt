Overview
-----------------------------------------------------------------------------------------------------------------------------------------
This project is a FastAPI-based document retrieval system that supports semantic and keyword search. 
The application processes uploaded PDF documents and allows users to query them efficiently. 
The system integrates various NLP techniques and APIs to enhance the relevance of retrieved results.
-----------------------------------------------------------------------------------------------------------------------------------------
Features
-----------------------------------------------------------------------------------------------------------------------------------------
1. PDF Processing: Parses uploaded PDFs and extracts text for indexing.

2. Semantic Search: Uses spaCy for embedding-based search.

3. Keyword Search: Implements traditional keyword-based retrieval using BM25.

4. Result Optimization: Leverages Cohere API for post-processing to refine search results.

5. Efficient Memory Usage: Optimized through model quantization and replacement of high-memory components.
-----------------------------------------------------------------------------------------------------------------------------------------
Deployment Attempts
-----------------------------------------------------------------------------------------------------------------------------------------
The application was tested for deployment on two platforms: Render and AWS. Below are the challenges encountered and solutions attempted.

Render Deployment Issues
1. Server Unhealthy (Memory Exhaustion): Render's free tier provides 512MB RAM and 0.1 CPU, which was insufficient.
	Memory Profiling Identified Sentence-Transformers as the Issue:
	Initial Memory Usage: ~244 MiB
	Performed quantization, reducing memory usage to ~98 MiB.
	Removed GraphRAG optimization and focused only on keyword and semantic search.
	Replaced Sentence Transformers with a lightweight spaCy model, reducing memory from ~244 MiB to ~9 MiB.

2. CORS Issue
	Initially blocked due to missing CORS headers.
	Fixed by adding mode: no-cors on the frontend to bypass restrictions.
-----------------------------------------------------------------------------------------------------------------------------------------
AWS Deployment Issues

1. IP Address Not Accessible (Permission Issues)
	Deployed backend on an AWS EC2 instance.
	Copied over files and started the FastAPI server.
	However, the frontend failed to connect due to network/permission restrictions.
	Investigated security group settings and port accessibility, but the issue persisted.
-----------------------------------------------------------------------------------------------------------------------------------------
Technical Experiments (Not Included in Final Codebase)
-----------------------------------------------------------------------------------------------------------------------------------------
1. GraphRAG Implementation
	Initially implemented GraphRAG to optimize search results by merging structured knowledge with traditional retrieval.
	Later removed due to high computational overhead.

2. Out-of-Context Query Handling
	Graph-Based Ranking: Instead of linking adjacent edges, experimented with PageRank to connect graph edges dynamically.
	CLIP Model for Chunk Filtering: Integrated CLIP model to filter irrelevant document chunks based on query relevance.
	While effective, this was removed to reduce complexity and compute cost.
-----------------------------------------------------------------------------------------------------------------------------------------
How It Works
-----------------------------------------------------------------------------------------------------------------------------------------
1. User Uploads a PDF via the frontend.
2. Processing Begins:
	The document is parsed and indexed.
	Both semantic and keyword search techniques are applied.
3. Search Execution:
	User submits a query.
	The system performs a hybrid retrieval using both methods.
4. Post-Processing with Cohere API:
	The results are refined and displayed based on semantic relevance.
-----------------------------------------------------------------------------------------------------------------------------------------
Future Improvements
-----------------------------------------------------------------------------------------------------------------------------------------
1. Optimize Deployment on cloud platforms to ensure scalability.
2. Enhance Out-of-Context Detection for improved query relevance.
3. Refine Ranking Mechanisms by integrating newer NLP models with lower memory consumption.
-----------------------------------------------------------------------------------------------------------------------------------------
Conclusion
-----------------------------------------------------------------------------------------------------------------------------------------
This project demonstrates the development of an optimized document retrieval system using FAISS indexing, BM25, and Cohere API. 
While deployment challenges were encountered, significant improvements were made in terms of memory optimization, retrieval accuracy, and 
query handling. Future iterations will focus on resolving deployment issues and enhancing model efficiency.
-----------------------------------------------------------------------------------------------------------------------------------------