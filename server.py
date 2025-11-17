#!/usr/bin/env python3
"""
MCP Knowledge Base Assistant Server
A server that provides tools for interacting with a local knowledge base.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader, 
    Docx2txtLoader
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Knowledge Base Server")

class KnowledgeBase:
    def __init__(self, storage_path: str = "./knowledge_base"):
        """Initialize the knowledge base."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector store
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=str(self.storage_path / "chroma_db"),
            embedding_function=self.embeddings
        )
        
        # Text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

# Initialize knowledge base
kb = KnowledgeBase()
        
@app.post("/search")
async def search_documents(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search the knowledge base for relevant documents.
    """
    try:
        results = kb.vector_store.similarity_search_with_relevance_scores(
            query,
            k=limit
        )
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_document(content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Add a new document to the knowledge base.
    """
    try:
        if metadata is None:
            metadata = {}
        
        # Add timestamp to metadata
        metadata["added_at"] = datetime.now().isoformat()
        
        # Split text into chunks
        texts = kb.text_splitter.split_text(content)
        
        # Add to vector store
        kb.vector_store.add_texts(
            texts,
            metadatas=[metadata for _ in texts]
        )
        
        return {
            "status": "success",
            "document_size": len(content),
            "chunks_created": len(texts),
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{document_id}")
async def get_document_summary(document_id: str) -> Dict[str, Any]:
    """
    Get a summary of a document's metadata and contents.
    """
    try:
        results = kb.vector_store.similarity_search(
            document_id,
            k=1,
            filter={"document_id": document_id}
        )
        
        if not results:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = results[0]
        return {
            "document_id": document_id,
            "metadata": doc.metadata,
            "content_preview": doc.page_content[:500] + "..."
        }
    except Exception as e:
        logger.error(f"Error getting document summary: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)