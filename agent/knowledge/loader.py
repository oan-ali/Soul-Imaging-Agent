"""
loader.py — Advanced knowledge loader.
Parses JSON, Markdown (.md), and Text (.txt) files from data/ and docs/.
"""
import os
import json
import logging
from typing import List, Dict
from agent.knowledge.store import knowledge_store

logger = logging.getLogger("knowledge-loader")

async def ingest_knowledge_base():
    """
    Scans both 'data' and 'docs' directories for knowledge sources.
    Parses JSON (question/answer format) and plain text / markdown files.
    """
    base_dir = os.path.dirname(__file__)
    data_sources = [
        os.path.join(base_dir, "data"),
        os.path.join(base_dir, "docs")
    ]
    
    # Ensure directories exist
    for source in data_sources:
        os.makedirs(source, exist_ok=True)
    
    chunks = []
    
    # Process files
    for source_dir in data_sources:
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            
            # 1. Process JSON
            if filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if "question" in item and "answer" in item:
                                    chunks.append(f"Q: {item['question']}\nA: {item['answer']}")
                                elif "content" in item:
                                    chunks.append(item["content"])
                except Exception as e:
                    logger.error(f"Error parsing JSON {filename}: {e}")
            
            # 2. Process MD / TXT
            elif filename.endswith((".md", ".txt")):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            # Split large documents into chunks of ~1000 characters
                            # (A simple character-based split for now)
                            text_chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                            chunks.extend(text_chunks)
                except Exception as e:
                    logger.error(f"Error parsing text file {filename}: {e}")
                    
    if not chunks:
        logger.warning("No knowledge chunks found in data/ or docs/.")
        return
        
    logger.info(f"Generating embeddings for {len(chunks)} chunks from {len(os.listdir(data_sources[0])) + len(os.listdir(data_sources[1]))} files...")
    
    # Prepare chunk objects for the store
    chunk_objs = [{"content": c} for c in chunks]
    embeddings_matrix = []
    
    for chunk_obj in chunk_objs:
        emb = await knowledge_store.get_embedding(chunk_obj["content"])
        if emb:
             embeddings_matrix.append(emb)
        else:
             # If embedding fails, push a zero vector
             embeddings_matrix.append([0.0]*1536)
             
    knowledge_store.set_data(chunk_objs, embeddings_matrix)
    logger.info("Knowledge base ingestion complete.")
