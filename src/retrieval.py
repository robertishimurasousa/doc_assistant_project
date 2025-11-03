"""Document retrieval module for the assistant."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from src.schemas import Document, Query


class DocumentRetriever:
    """Handles document retrieval and search."""

    def __init__(self, document_path: Optional[str] = None):
        """Initialize the document retriever.

        Args:
            document_path: Path to the documents directory or file
        """
        self.document_path = document_path
        self.documents: List[Document] = []

    def load_documents(self, path: Optional[str] = None) -> None:
        """Load documents from a specified path.

        Args:
            path: Path to load documents from
        """
        target_path = path or self.document_path
        if not target_path:
            return

        path_obj = Path(target_path)
        if path_obj.is_file():
            self._load_single_file(path_obj)
        elif path_obj.is_dir():
            self._load_directory(path_obj)

    def _load_single_file(self, file_path: Path) -> None:
        """Load a single document file.

        Args:
            file_path: Path to the file
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            doc = Document(
                content=content,
                source=str(file_path),
                metadata={"filename": file_path.name, "extension": file_path.suffix}
            )
            self.documents.append(doc)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")

    def _load_directory(self, dir_path: Path) -> None:
        """Load all documents from a directory.

        Args:
            dir_path: Path to the directory
        """
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.json', '.csv']:
                self._load_single_file(file_path)

    def retrieve(self, query: Query, top_k: int = 5) -> List[Document]:
        """Retrieve relevant documents for a query.

        Args:
            query: Query object containing search text
            top_k: Number of top documents to retrieve

        Returns:
            List of relevant documents
        """
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_terms = query.text.lower().split()
        scored_docs = []

        for doc in self.documents:
            score = self._calculate_score(doc.content.lower(), query_terms)
            if score > 0:
                doc_copy = doc.model_copy()
                doc_copy.score = score
                scored_docs.append(doc_copy)

        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x.score or 0, reverse=True)
        return scored_docs[:top_k]

    def _calculate_score(self, content: str, query_terms: List[str]) -> float:
        """Calculate relevance score for a document.

        Args:
            content: Document content
            query_terms: List of query terms

        Returns:
            Relevance score
        """
        score = 0.0
        for term in query_terms:
            score += content.count(term)
        return score

    def add_document(self, document: Document) -> None:
        """Add a document to the retriever.

        Args:
            document: Document to add
        """
        self.documents.append(document)

    def clear_documents(self) -> None:
        """Clear all loaded documents."""
        self.documents.clear()

    def get_document_count(self) -> int:
        """Get the number of loaded documents.

        Returns:
            Number of documents
        """
        return len(self.documents)
