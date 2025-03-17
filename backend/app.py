from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from graph_rag import GraphRAGPipeline
import os
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development; modify for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Initialize GraphRAG pipeline
graph_rag = GraphRAGPipeline()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Define the directory path
    print(f"Received file: {file.filename}")
    upload_dir = "data/uploaded_files"

    # Check if the directory exists, and create it if it doesn't
    os.makedirs(upload_dir, exist_ok=True)

    # Store the uploaded PDF/HTML file in the `data/uploaded_files/` folder
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Process the document and build the knowledge graph
    graph_rag.process_document(file_path)

    return {"message": "File uploaded and indexed!"}


@app.get("/search/")
async def search(query: str):
    return StreamingResponse(graph_rag.stream_search(query), media_type="text/event-stream")
