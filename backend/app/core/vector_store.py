"""
Vector Store Module
ChromaDB integration for storing and retrieving legal document embeddings
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from dataclasses import dataclass

from app.services.legal_chunker import LegalChunk


@dataclass
class SearchResult:
    """A single search result"""
    content: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str
    
    @property
    def reference(self) -> str:
        """Generate citation reference"""
        parts = []
        if self.metadata.get('article_number'):
            parts.append(f"Điều {self.metadata['article_number']}")
        if self.metadata.get('clause_number'):
            parts.append(f"Khoản {self.metadata['clause_number']}")
        if self.metadata.get('document_number'):
            parts.append(f"({self.metadata['document_number']})")
        if self.metadata.get('filename'):
            parts.append(f"- {self.metadata['filename']}")
        return " ".join(parts) if parts else "Không rõ nguồn"


class VectorStore:
    """
    Vector store using ChromaDB for legal documents
    Supports metadata filtering for document type, year, etc.
    """
    
    def __init__(
        self,
        persist_directory: str = "./vectordb",
        collection_name: str = "legal_documents"
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self._collection = None
    
    @property
    def collection(self):
        """Get or create the collection"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
        return self._collection
    
    def add_chunks(
        self,
        chunks: List[LegalChunk],
        embeddings: List[List[float]],
        document_metadata: Dict[str, Any] = None
    ) -> List[str]:
        """
        Add legal chunks to the vector store
        
        Args:
            chunks: List of LegalChunk objects
            embeddings: Corresponding embeddings
            document_metadata: Additional metadata from the document
        
        Returns:
            List of chunk IDs
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        if not chunks:
            return []
        
        ids = []
        documents = []
        metadatas = []
        
        doc_meta = document_metadata or {}
        
        for i, chunk in enumerate(chunks):
            # Generate unique ID
            chunk_id = f"{doc_meta.get('filename', 'doc')}_{chunk.chunk_type}_{chunk.article_number or 'na'}_{i}"
            chunk_id = chunk_id.replace(' ', '_').replace('/', '_')
            
            ids.append(chunk_id)
            documents.append(chunk.content)
            
            # Combine chunk metadata with document metadata
            metadata = {
                "chunk_type": chunk.chunk_type,
                "article_number": chunk.article_number or "",
                "clause_number": chunk.clause_number or "",
                "chapter": chunk.chapter or "",
                "section": chunk.section or "",
                "reference": chunk.reference,
                **doc_meta
            }
            # ChromaDB only supports str, int, float, bool
            metadata = {k: str(v) if v is not None else "" for k, v in metadata.items()}
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"document_type": "Luật"})
        
        Returns:
            List of SearchResult objects
        """
        # Build where clause for filtering
        where = None
        if filter_metadata:
            where = {k: str(v) for k, v in filter_metadata.items() if v}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        if results and results['ids'] and results['ids'][0]:
            for i, chunk_id in enumerate(results['ids'][0]):
                # Convert distance to similarity score (ChromaDB uses L2 by default, we use cosine)
                distance = results['distances'][0][i]
                score = 1 - distance  # For cosine, similarity = 1 - distance
                
                search_results.append(SearchResult(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    score=score,
                    chunk_id=chunk_id
                ))
        
        return search_results
    
    def delete_document(self, filename: str) -> int:
        """Delete all chunks from a specific document"""
        # Get all IDs for this document
        results = self.collection.get(
            where={"filename": filename},
            include=[]
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        return 0
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Get list of all documents in the store"""
        results = self.collection.get(
            include=["metadatas"]
        )
        
        # Group by filename
        documents = {}
        for metadata in results['metadatas']:
            filename = metadata.get('filename', 'Unknown')
            if filename not in documents:
                documents[filename] = {
                    'filename': filename,
                    'document_number': metadata.get('document_number', ''),
                    'document_type': metadata.get('document_type', ''),
                    'year': metadata.get('year', ''),
                    'chunk_count': 0
                }
            documents[filename]['chunk_count'] += 1
        
        return list(documents.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        count = self.collection.count()
        documents = self.get_document_list()
        
        return {
            'total_chunks': count,
            'total_documents': len(documents),
            'collection_name': self.collection_name,
            'persist_directory': str(self.persist_directory)
        }
    
    def reset(self) -> None:
        """Reset the collection (delete all data)"""
        self.client.delete_collection(self.collection_name)
        self._collection = None
        print(f"Collection '{self.collection_name}' has been reset")


# Singleton
_vector_store: Optional[VectorStore] = None


def get_vector_store(
    persist_directory: str = "./vectordb",
    collection_name: str = "legal_documents"
) -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_directory, collection_name)
    return _vector_store


if __name__ == "__main__":
    # Test the vector store
    store = VectorStore("./test_vectordb", "test_collection")
    
    print("Vector Store Stats:")
    print(store.get_stats())
