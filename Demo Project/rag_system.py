"""
RAG System for AI-Powered Test Automation
Implements Retrieval-Augmented Generation using FAISS and sentence-transformers
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

# Vector database and embeddings
import faiss
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class DocumentProcessor:
    """Processes documents for RAG system."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor.

        Args:
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at word boundaries
            if end < text_length and not text[end].isspace():
                last_space = chunk.rfind(' ')
                if last_space > 0:
                    chunk = chunk[:last_space]
                    end = start + last_space

            chunks.append(chunk.strip())
            start = end - self.chunk_overlap

        return [c for c in chunks if c]

    def process_document(self, doc_id: str, content: str, 
                        metadata: Dict[str, Any]) -> List[Document]:
        """
        Process a document into chunks.

        Args:
            doc_id: Document identifier
            content: Document content
            metadata: Document metadata

        Returns:
            List of document chunks
        """
        chunks = self.chunk_text(content)
        documents = []

        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_id'] = f"{doc_id}_chunk_{i}"
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)

            doc = Document(
                id=chunk_metadata['chunk_id'],
                content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)

        return documents


class RAGSystem:
    """RAG System for semantic search and retrieval."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2",
                 embedding_dim: int = 384):
        """
        Initialize RAG system.

        Args:
            model_name: Sentence transformer model name
            embedding_dim: Dimension of embeddings
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.embedding_model = None
        self.index = None
        self.documents: List[Document] = []
        self.document_processor = DocumentProcessor()
        self.is_initialized = False

    def initialize(self):
        """Initialize the RAG system."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)

            # Initialize FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dim)

            self.is_initialized = True
            logger.info("RAG system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            Numpy array of embeddings
        """
        if not self.embedding_model:
            raise RuntimeError("RAG system not initialized")

        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.astype('float32')

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the RAG system.

        Args:
            documents: List of documents to add
        """
        if not self.is_initialized:
            self.initialize()

        # Process documents into chunks if needed
        all_chunks = []
        for doc in documents:
            if doc.embedding is None:
                # This is a full document, need to chunk it
                chunks = self.document_processor.process_document(
                    doc.id, doc.content, doc.metadata
                )
                all_chunks.extend(chunks)
            else:
                # Already a chunk with embedding
                all_chunks.append(doc)

        # Create embeddings for chunks
        texts = [doc.content for doc in all_chunks]
        embeddings = self.create_embeddings(texts)

        # Store embeddings in documents
        for doc, embedding in zip(all_chunks, embeddings):
            doc.embedding = embedding

        # Add to FAISS index
        if len(embeddings) > 0:
            self.index.add(embeddings)
            self.documents.extend(all_chunks)

        logger.info(f"Added {len(all_chunks)} document chunks to RAG system")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of search results with scores
        """
        if not self.is_initialized:
            self.initialize()

        if self.index.ntotal == 0:
            logger.warning("No documents in RAG system")
            return []

        # Create query embedding
        query_embedding = self.create_embeddings([query])

        # Search
        distances, indices = self.index.search(query_embedding, k)

        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'score': float(dist),  # Lower is better for L2 distance
                    'document_id': doc.id
                })

        return results

    def get_context_for_test_generation(self, test_case: Dict[str, Any],
                                       k: int = 3) -> str:
        """
        Get relevant context for test generation.

        Args:
            test_case: Test case data
            k: Number of relevant documents to retrieve

        Returns:
            Formatted context string
        """
        # Create search query from test case
        query_parts = [
            test_case.get('name', ''),
            test_case.get('description', ''),
            ' '.join([step.get('description', '') for step in test_case.get('steps', [])])
        ]
        query = ' '.join(query_parts)

        # Search for relevant documents
        results = self.search(query, k)

        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Document {i} (Score: {result['score']:.4f}):")
            context_parts.append(result['content'])
            context_parts.append("")

        return "\n".join(context_parts)

    def save_index(self, filepath: str):
        """
        Save the FAISS index to disk.

        Args:
            filepath: Path to save the index
        """
        if self.index:
            faiss.write_index(self.index, filepath)
            logger.info(f"Index saved to {filepath}")

    def load_index(self, filepath: str):
        """
        Load the FAISS index from disk.

        Args:
            filepath: Path to load the index from
        """
        if os.path.exists(filepath):
            self.index = faiss.read_index(filepath)
            logger.info(f"Index loaded from {filepath}")
        else:
            logger.warning(f"Index file not found: {filepath}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.

        Returns:
            Dictionary with system statistics
        """
        return {
            'initialized': self.is_initialized,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'total_documents': len(self.documents),
            'total_chunks': self.index.ntotal if self.index else 0
        }


# Global RAG instance
_rag_instance: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """
    Get the global RAG system instance.

    Returns:
        RAG system instance
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance


def initialize_rag_with_sample_data():
    """
    Initialize RAG system with sample knowledge base data.
    """
    rag = get_rag_system()
    rag.initialize()

    # Create sample documents directory
    docs_dir = os.path.join(os.path.dirname(__file__), 'knowledge_base')
    os.makedirs(docs_dir, exist_ok=True)

    # Load documents from knowledge base
    documents = load_documents_from_directory(docs_dir)

    if documents:
        rag.add_documents(documents)
        logger.info(f"Initialized RAG with {len(documents)} documents")
    else:
        logger.warning("No documents found in knowledge base")

    return rag


def load_documents_from_directory(directory: str) -> List[Document]:
    """
    Load documents from a directory.

    Args:
        directory: Path to directory containing documents

    Returns:
        List of documents
    """
    documents = []

    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return documents

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            doc = Document(
                id=filename.replace('.txt', ''),
                content=content,
                metadata={
                    'source': filename,
                    'type': 'text'
                }
            )
            documents.append(doc)

        elif filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    if 'content' in item:
                        doc = Document(
                            id=item.get('id', filename),
                            content=item['content'],
                            metadata=item.get('metadata', {})
                        )
                        documents.append(doc)
            elif isinstance(data, dict) and 'content' in data:
                doc = Document(
                    id=data.get('id', filename),
                    content=data['content'],
                    metadata=data.get('metadata', {})
                )
                documents.append(doc)

    logger.info(f"Loaded {len(documents)} documents from {directory}")
    return documents
