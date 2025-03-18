# from langchain_community.embeddings import SentenceTransformerEmbeddings
import spacy
import faiss
# from langchain_community.vectorstores import FAISS
# from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import networkx as nx
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from pdf_html_extractor import extract_text_from_pdf, extract_text_from_html
from dotenv import load_dotenv
import cohere, os
# from memory_profiler import profile
import psutil


def get_cohere_api_key():
    """
    Retrieves the Cohere API key from an environment variable.
    """
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY environment variable not set.")
    return api_key


def get_memory_usage():
    process = psutil.Process(os.getpid())  # Get current process
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)

class GraphRAGPipeline:
    def __init__(self):
        self.graph = nx.Graph()
        self.faiss_index = None
        self.bm25_index = None
        self.chunks = []
        load_dotenv()
        api_key = get_cohere_api_key()
        self.cohere_client = cohere.Client(api_key)

        self.nlp = spacy.load("en_core_web_sm")
    
    # @profile
    # def load_embeddings(self):
    #     embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    #     return embeddings



    def process_document(self, file_path):
        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_html(file_path)

        self.chunks = [text[i:i + 500] for i in range(0, len(text), 500)]
        

        before_mem = get_memory_usage()
        chunk_embeddings = np.array([self.nlp(text).vector for text in self.chunks])
        # chunk_embeddings = self.faiss_index.index.reconstruct_n(0, len(self.chunks))  # Get embeddings
        after_mem = get_memory_usage()
        print(f"<><><> MEMORY USAGE: {after_mem - before_mem:.2f} MB")
        # self.faiss_index = FAISS.from_texts(self.chunks, embeddings)
        # self.faiss_index.save_local("faiss_index")
        embedding_dim = chunk_embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(embedding_dim)  # L2 distance FAISS index
        self.faiss_index.add(chunk_embeddings)  # Add embeddings to FAISS
        # similarity_matrix = cosine_similarity(chunk_embeddings)
        
        # for i, chunk in enumerate(self.chunks):
        #     self.graph.add_node(i, text=chunk) 
        self.graph.add_nodes_from(range(len(self.chunks)))

        # for i in range(len(self.chunks)):
        #     for j in range(i + 1, len(self.chunks)):
        #         if similarity_matrix[i][j] > 0.7:  
        #             self.graph.add_edge(i, j, weight=similarity_matrix[i][j])
        for i in range(len(self.chunks)):
            distances, indices = self.faiss_index.search(chunk_embeddings[i].reshape(1, -1), k=10)
            for j, dist in zip(indices[0], distances[0]):
                if i != j and dist < 0.7:  # ✅ Lower threshold = higher similarity
                    self.graph.add_edge(i, j, weight=1 - dist)  # Store similarity score

        after_mem = get_memory_usage()
        print(f"<><><> MEMORY USAGE AFTER FAISS: {after_mem - before_mem:.2f} MB")
       
        tokenized_chunks = [word_tokenize(chunk.lower()) for chunk in self.chunks]
        self.bm25_index = BM25Okapi(tokenized_chunks, k1=1.5, b=0.75)

    def semantic_search(self, query):
        # if self.faiss_index is None:
        #     self.faiss_index = FAISS.load_local("faiss_index", self.embeddings)
        # return self.faiss_index.similarity_search_with_score(query, k=5)
        if self.faiss_index is None:
            self.faiss_index = faiss.read_index("faiss_index")

        query_embedding = np.array([self.nlp(query).vector], dtype=np.float32)
        if not self.faiss_index.is_trained:
            print("FAISS index is not trained.")
            return []

        distances, indices = self.faiss_index.search(np.array(query_embedding, dtype=np.float32), 5)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue  
            
            text_chunk = self.chunks[idx]  # Retrieve original text chunk
            similarity_score = 1 / (1 + distances[0][i])  # Convert L2 distance to similarity

            results.append((text_chunk, similarity_score))

        return results

    def keyword_search(self, query):
        tokenized_query = word_tokenize(query.lower())
        scores = self.bm25_index.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
        return [(self.chunks[i], scores[i]) for i in top_indices]

    # def graph_rag_search(self, query):
    #     faiss_results = self.semantic_search(query)
        
    #     # seed_nodes = [self.chunks.index(doc.page_content) for doc, _ in faiss_results]
    #     # personalization = {node: 1 if node in seed_nodes else 0 for node in self.graph.nodes}
    #     # pagerank_scores = nx.pagerank(self.graph, personalization=personalization, alpha=0.85)

    #     # ranked_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
    #     # results_with_context = []
    #     # for node, score in ranked_nodes[:5]:  
    #     #     context_chunks = [self.graph.nodes[neighbor]['text'] for neighbor in self.graph.neighbors(node)]
    #     #     results_with_context.append((self.graph.nodes[node]['text'], context_chunks, score))

    #     # return results_with_context

    #     seed_nodes = [idx for idx, _ in faiss_results]
    #     if len(self.graph.edges) == 0:
    #         return [(self.graph.nodes[node]['text'], [], 1.0) for node in seed_nodes]
    #     personalization = {node: (1 if node in seed_nodes else 0) for node in self.graph.nodes}
    #     pagerank_scores = nx.pagerank(self.graph, personalization=personalization, alpha=0.85)
    #     ranked_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
    #     results_with_context = [
    #         (
    #             self.graph.nodes[node]['text'],  # Main retrieved chunk
    #             [self.graph.nodes[neighbor]['text'] for neighbor in self.graph.neighbors(node)],  # Context chunks
    #             score  # PageRank score
    #         )
    #         for node, score in ranked_nodes[:5]  # Top 5 results
    #     ]

    #     return results_with_context

    def stream_search(self, query):
        faiss_results = self.semantic_search(query)
        keyword_results = self.keyword_search(query)
        # graph_rag_results = self.graph_rag_search(query)

        merged_results = []

        for doc, score in faiss_results:
            merged_results.append({"text": doc, "source": "semantic", "score": score})


        for chunk, score in keyword_results:
            merged_results.append({"text": chunk, "source": "keyword", "score": score})

        # for doc, context, score in graph_rag_results:
        #     merged_results.append({"text": doc, "context": context, "source": "graph_rag", "score": score})

        unique_results = {}
        for result in merged_results:
            unique_results[result["text"]] = result

        final_results = sorted(unique_results.values(), key=lambda x: x["score"], reverse=True)
        response = self.extract_info(final_results)

        return response
    def extract_info(self, results):
        """
        Extracts tasks, task percentages, descriptions, and deadlines from the provided document text.
        """
        prompt = "Please provide a summary of the following information:\n\n"
        for result in results:
            prompt += f"Source: {result['source']} | Text: {result['text']} | Score: {result['score']}\n\n"

        response = self.cohere_client.chat(
            model="command-xlarge-nightly",
            message=prompt,
            max_tokens=1500,
            temperature=0.7
        )

        return response.text
