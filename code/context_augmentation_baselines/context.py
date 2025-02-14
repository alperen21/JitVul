from retriever import Chunker
import os
from jaccard import retrieve_chunks

def get_context(query):
    chunker = Chunker()
    chunks = chunker.read_and_parse_documents(repo_path=os.path.join("projects","repo"))
    context = retrieve_chunks(query, chunks, top_k=5)
    
    return context