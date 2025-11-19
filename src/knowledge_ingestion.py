"""
Knowledge Ingestion Pipeline
Handles extraction of text from various sources (files, URLs, notes)
"""

import logging
import os
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Base exception for ingestion errors"""
    pass


class FileIngestor:
    """Handles text extraction from files"""

    @staticmethod
    def ingest_text_file(file_path: str) -> str:
        """
        Extract text from plain text file

        Args:
            file_path: Path to text file

        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            logger.info(f"Extracted text from file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            raise IngestionError(f"Failed to read text file: {e}")

    @staticmethod
    def ingest_markdown_file(file_path: str) -> str:
        """
        Extract text from markdown file (strip markdown syntax)

        Args:
            file_path: Path to markdown file

        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Simple markdown stripping (keep text, remove formatting)
            # Remove code blocks
            content = re.sub(r'```[\s\S]*?```', '', content)
            # Remove inline code
            content = re.sub(r'`[^`]+`', '', content)
            # Remove headers (but keep the text)
            content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
            # Remove bold/italic markers
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
            content = re.sub(r'\*([^*]+)\*', r'\1', content)
            content = re.sub(r'__([^_]+)__', r'\1', content)
            content = re.sub(r'_([^_]+)_', r'\1', content)
            # Remove links but keep text
            content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
            # Remove images
            content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)

            logger.info(f"Extracted text from markdown: {file_path}")
            return content.strip()

        except Exception as e:
            logger.error(f"Failed to read markdown file {file_path}: {e}")
            raise IngestionError(f"Failed to read markdown file: {e}")

    @staticmethod
    def ingest_pdf_file(file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            # Try using PyPDF2 if available
            try:
                import PyPDF2

                text_parts = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)

                content = '\n\n'.join(text_parts)
                logger.info(f"Extracted text from PDF (PyPDF2): {file_path}")
                return content

            except ImportError:
                logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")

                # Try pdfplumber as fallback
                try:
                    import pdfplumber

                    text_parts = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                text_parts.append(text)

                    content = '\n\n'.join(text_parts)
                    logger.info(f"Extracted text from PDF (pdfplumber): {file_path}")
                    return content

                except ImportError:
                    logger.error("No PDF library available. Install PyPDF2 or pdfplumber")
                    raise IngestionError(
                        "PDF support not available. Install with: pip install PyPDF2"
                    )

        except IngestionError:
            raise
        except Exception as e:
            logger.error(f"Failed to read PDF file {file_path}: {e}")
            raise IngestionError(f"Failed to read PDF file: {e}")

    @staticmethod
    def ingest_file(file_path: str) -> str:
        """
        Auto-detect file type and extract text

        Args:
            file_path: Path to file

        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            raise IngestionError(f"File not found: {file_path}")

        # Detect file type by extension
        ext = Path(file_path).suffix.lower()

        if ext in ['.txt', '.log']:
            return FileIngestor.ingest_text_file(file_path)
        elif ext in ['.md', '.markdown']:
            return FileIngestor.ingest_markdown_file(file_path)
        elif ext == '.pdf':
            return FileIngestor.ingest_pdf_file(file_path)
        else:
            # Try as text file
            logger.warning(f"Unknown file type {ext}, attempting text extraction")
            return FileIngestor.ingest_text_file(file_path)


class URLIngestor:
    """Handles text extraction from web URLs"""

    DEFAULT_TIMEOUT = 15

    @staticmethod
    def ingest_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        """
        Fetch and extract main text from URL

        Args:
            url: Web URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Extracted text content
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("requests and beautifulsoup4 required for URL ingestion")
            raise IngestionError(
                "URL support requires: pip install requests beautifulsoup4"
            )

        try:
            # Fetch URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Gaming AI Assistant Knowledge Pack Ingestion)'
            }
            effective_timeout = timeout or URLIngestor.DEFAULT_TIMEOUT
            response = requests.get(
                url,
                timeout=(effective_timeout, effective_timeout),
                headers=headers,
            )
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text
            # Try to find main content area first
            main_content = None
            for tag in ['main', 'article', 'div[role="main"]']:
                main_content = soup.find(tag)
                if main_content:
                    break

            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body
                text = soup.get_text(separator='\n', strip=True)

            # Clean up extra whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines)

            logger.info(f"Extracted text from URL: {url} ({len(content)} chars)")
            return content

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise IngestionError(f"Failed to fetch URL: {e}")
        except Exception as e:
            logger.error(f"Failed to extract text from URL {url}: {e}")
            raise IngestionError(f"Failed to extract text: {e}")


class NoteIngestor:
    """Handles plain text notes (no processing needed)"""

    @staticmethod
    def ingest_note(content: str) -> str:
        """
        Process note content (just validation and cleanup)

        Args:
            content: Note text content

        Returns:
            Cleaned content
        """
        if not content:
            raise IngestionError("Note content is empty")

        return content.strip()


class IngestionPipeline:
    """
    Main ingestion pipeline that coordinates all ingestors
    """

    def __init__(self):
        self.file_ingestor = FileIngestor()
        self.url_ingestor = URLIngestor()
        self.note_ingestor = NoteIngestor()

    def ingest(self, source_type: str, **kwargs) -> str:
        """
        Ingest content based on source type

        Args:
            source_type: Type of source ('file', 'url', 'note')
            **kwargs: Type-specific parameters
                - file: file_path
                - url: url, timeout (optional)
                - note: content

        Returns:
            Extracted text content

        Raises:
            IngestionError: If ingestion fails
        """
        try:
            if source_type == 'file':
                file_path = kwargs.get('file_path')
                if not file_path:
                    raise IngestionError("file_path required for file source")
                return self.file_ingestor.ingest_file(file_path)

            elif source_type == 'url':
                url = kwargs.get('url')
                if not url:
                    raise IngestionError("url required for url source")
                timeout = kwargs.get('timeout', URLIngestor.DEFAULT_TIMEOUT)
                return self.url_ingestor.ingest_url(url, timeout=timeout)

            elif source_type == 'note':
                content = kwargs.get('content')
                if content is None:
                    raise IngestionError("content required for note source")
                return self.note_ingestor.ingest_note(content)

            else:
                raise IngestionError(f"Unknown source type: {source_type}")

        except IngestionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during ingestion: {e}", exc_info=True)
            raise IngestionError(f"Ingestion failed: {e}")

    def ingest_batch(self, sources: List[dict]) -> List[Optional[str]]:
        """
        Ingest multiple sources

        Args:
            sources: List of source dictionaries with 'type' and type-specific params

        Returns:
            List of extracted contents (None for failures)
        """
        results = []
        for source in sources:
            try:
                source_type = source.pop('type')
                content = self.ingest(source_type, **source)
                results.append(content)
            except Exception as e:
                logger.error(f"Failed to ingest source: {e}")
                results.append(None)

        return results


# Global ingestion pipeline instance
_ingestion_pipeline: Optional[IngestionPipeline] = None


def get_ingestion_pipeline() -> IngestionPipeline:
    """Get or create the global ingestion pipeline instance"""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = IngestionPipeline()
    return _ingestion_pipeline
