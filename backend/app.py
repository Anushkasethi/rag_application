from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from graph_rag import GraphRAGPipeline
import os
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import shutil
import spacy

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development; modify for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

model_name = "en_core_web_sm"
subprocess.run(["python", "-m", "spacy", "download", model_name])
graph_rag = GraphRAGPipeline(model_name)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    upload_dir = "data/uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    graph_rag.process_document(file_path)

    return {"message": "File uploaded and indexed!"}


@app.get("/search/")
async def search(query: str):
    return StreamingResponse(graph_rag.stream_search(query), media_type="text/event-stream")
