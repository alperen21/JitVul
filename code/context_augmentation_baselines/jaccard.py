import re
from typing import List, Tuple
from langchain.docstore.document import Document

def tokenize(text: str) -> set:
    """
    Tokenize the input text into a set of lowercase words.
    You can adjust this function to use different tokenization or even n-grams.
    """
    return set(re.findall(r'\w+', text.lower()))

def jaccard_similarity(text1: str, text2: str) -> float:
    """
    Compute the Jaccard similarity between two texts.
    """
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))

def retrieve_chunks(query: str, chunks: List[Document], top_k: int = 5) -> List[Tuple[Document, float]]:
    """
    Given a query string and a list of Document objects (chunks), compute the Jaccard similarity
    for each chunk and return the top_k results as tuples of (Document, similarity_score).
    """
    scored_chunks = []
    for doc in chunks:
        score = jaccard_similarity(query, doc.page_content)
        scored_chunks.append((doc, score))
    
    # Sort by similarity score in descending order and return the top_k results
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]

# Example usage:
if __name__ == "__main__":
    # Suppose you already have a list of Document objects from your Chunker:
    # from your_chunker_module import Chunker
    # chunker = Chunker()
    # chunks = chunker.read_and_parse_documents(repo_path="path/to/your/repo")
    
    # For demonstration, let's assume:
    chunks = [
        Document(page_content="def add(a, b): return a + b", metadata={"source": "file1.py"}),
        Document(page_content="def multiply(a, b): return a * b", metadata={"source": "file2.py"}),
        Document(page_content="def subtract(a, b): return a - b", metadata={"source": "file3.py"}),
    ]
    
    query = "function to add numbers"
    top_results = retrieve_chunks(query, chunks, top_k=2)
    for doc, score in top_results:
        print(f"Score: {score:.2f} | Source: {doc.metadata['source']}")
        print(doc.page_content)
        print("-" * 50)