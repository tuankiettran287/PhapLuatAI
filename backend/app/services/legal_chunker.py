"""
Legal Chunker Module
Splits legal documents by Article (Điều) and Clause (Khoản) to preserve legal context
"""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LegalChunk:
    """A chunk of legal text with context"""
    content: str
    chunk_type: str  # "article", "clause", "section", "chapter"
    article_number: Optional[str] = None
    clause_number: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def reference(self) -> str:
        """Generate citation reference"""
        parts = []
        if self.article_number:
            parts.append(f"Điều {self.article_number}")
        if self.clause_number:
            parts.append(f"Khoản {self.clause_number}")
        if self.chapter:
            parts.append(f"Chương {self.chapter}")
        return ", ".join(parts) if parts else "Phần mở đầu"


class LegalChunker:
    """
    Chunks legal documents according to Vietnamese legal structure:
    - Phần (Part)
    - Chương (Chapter)  
    - Mục (Section)
    - Điều (Article) - Primary chunking unit
    - Khoản (Clause)
    - Điểm (Point)
    """
    
    # Regex patterns for Vietnamese legal structure
    PATTERNS = {
        'part': r'^PHẦN\s+(THỨ\s+)?([IVXLCDM]+|\d+)[.:\s]*(.*?)$',
        'chapter': r'^CHƯƠNG\s+([IVXLCDM]+|\d+)[.:\s]*(.*?)$',
        'section': r'^MỤC\s+(\d+)[.:\s]*(.*?)$',
        'article': r'^Điều\s+(\d+)[.:\s]*(.*?)$',
        'clause': r'^(\d+)\.\s+',
        'point': r'^([a-zđ])\)\s+',
    }
    
    def __init__(
        self,
        chunk_by_article: bool = True,
        include_context: bool = True,
        max_chunk_size: int = 2000,
        min_chunk_size: int = 100
    ):
        self.chunk_by_article = chunk_by_article
        self.include_context = include_context
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        
        # Compile patterns
        self.compiled_patterns = {
            name: re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def _find_articles(self, text: str) -> List[Dict[str, Any]]:
        """Find all articles in the document"""
        articles = []
        pattern = self.compiled_patterns['article']
        
        for match in pattern.finditer(text):
            articles.append({
                'number': match.group(1),
                'title': match.group(2).strip() if match.group(2) else "",
                'start': match.start(),
                'header_end': match.end()
            })
        
        # Set end positions
        for i, article in enumerate(articles):
            if i + 1 < len(articles):
                article['end'] = articles[i + 1]['start']
            else:
                article['end'] = len(text)
        
        return articles
    
    def _find_chapter_for_position(self, text: str, position: int) -> Optional[str]:
        """Find the chapter that contains a given position"""
        pattern = self.compiled_patterns['chapter']
        current_chapter = None
        
        for match in pattern.finditer(text):
            if match.start() > position:
                break
            current_chapter = match.group(1)
        
        return current_chapter
    
    def _find_section_for_position(self, text: str, position: int) -> Optional[str]:
        """Find the section that contains a given position"""
        pattern = self.compiled_patterns['section']
        current_section = None
        
        for match in pattern.finditer(text):
            if match.start() > position:
                break
            current_section = match.group(1)
        
        return current_section
    
    def _split_article_into_clauses(self, article_text: str, article_number: str) -> List[LegalChunk]:
        """Split an article into clauses if it's too long"""
        chunks = []
        lines = article_text.split('\n')
        
        current_clause = []
        current_clause_number = None
        
        for line in lines:
            clause_match = self.compiled_patterns['clause'].match(line.strip())
            
            if clause_match:
                # Save previous clause
                if current_clause:
                    chunk_text = '\n'.join(current_clause)
                    if len(chunk_text) >= self.min_chunk_size:
                        chunks.append(LegalChunk(
                            content=chunk_text,
                            chunk_type='clause',
                            article_number=article_number,
                            clause_number=current_clause_number
                        ))
                
                current_clause_number = clause_match.group(1)
                current_clause = [line]
            else:
                current_clause.append(line)
        
        # Don't forget the last clause
        if current_clause:
            chunk_text = '\n'.join(current_clause)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(LegalChunk(
                    content=chunk_text,
                    chunk_type='clause',
                    article_number=article_number,
                    clause_number=current_clause_number
                ))
        
        return chunks
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[LegalChunk]:
        """
        Chunk a legal document into meaningful pieces
        
        Primary strategy: Split by Article (Điều)
        Secondary: Split long articles by Clause (Khoản)
        """
        if metadata is None:
            metadata = {}
        
        chunks = []
        articles = self._find_articles(text)
        
        if not articles:
            # No articles found, return as single chunk or split by size
            if len(text) <= self.max_chunk_size:
                chunks.append(LegalChunk(
                    content=text,
                    chunk_type='document',
                    metadata=metadata
                ))
            else:
                # Split by paragraphs
                chunks.extend(self._fallback_chunking(text, metadata))
            return chunks
        
        # Process preamble (text before first article)
        if articles[0]['start'] > self.min_chunk_size:
            preamble = text[:articles[0]['start']].strip()
            if preamble:
                chunks.append(LegalChunk(
                    content=preamble,
                    chunk_type='preamble',
                    metadata=metadata
                ))
        
        # Process each article
        for article in articles:
            article_text = text[article['start']:article['end']].strip()
            article_number = article['number']
            
            # Find chapter and section context
            chapter = self._find_chapter_for_position(text, article['start'])
            section = self._find_section_for_position(text, article['start'])
            
            if len(article_text) <= self.max_chunk_size:
                # Article fits in one chunk
                chunks.append(LegalChunk(
                    content=article_text,
                    chunk_type='article',
                    article_number=article_number,
                    chapter=chapter,
                    section=section,
                    metadata=metadata
                ))
            else:
                # Article is too long, split by clauses
                clause_chunks = self._split_article_into_clauses(article_text, article_number)
                for chunk in clause_chunks:
                    chunk.chapter = chapter
                    chunk.section = section
                    chunk.metadata = metadata
                chunks.extend(clause_chunks)
        
        return chunks
    
    def _fallback_chunking(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[LegalChunk]:
        """Fallback chunking when no legal structure is found"""
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if current_length + len(para) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(LegalChunk(
                        content='\n\n'.join(current_chunk),
                        chunk_type='paragraph',
                        metadata=metadata
                    ))
                current_chunk = [para]
                current_length = len(para)
            else:
                current_chunk.append(para)
                current_length += len(para)
        
        if current_chunk:
            chunks.append(LegalChunk(
                content='\n\n'.join(current_chunk),
                chunk_type='paragraph',
                metadata=metadata
            ))
        
        return chunks


if __name__ == "__main__":
    # Test the chunker
    sample_text = """
CHƯƠNG I
NHỮNG QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Luật này quy định về quyền sở hữu và các quyền khác đối với tài sản.

1. Quyền chiếm hữu, quyền sử dụng, quyền định đoạt tài sản của chủ sở hữu.
2. Quyền khác đối với tài sản của người không phải là chủ sở hữu.

Điều 2. Đối tượng áp dụng
Luật này áp dụng đối với cơ quan, tổ chức, cá nhân Việt Nam; cơ quan, tổ chức, cá nhân nước ngoài có liên quan.

CHƯƠNG II
TÀI SẢN

Điều 3. Tài sản
1. Tài sản bao gồm vật, tiền, giấy tờ có giá và các quyền tài sản.
2. Tài sản bao gồm bất động sản và động sản.

a) Bất động sản là đất đai và các tài sản gắn liền với đất.
b) Động sản là các tài sản không phải bất động sản.
    """
    
    chunker = LegalChunker()
    chunks = chunker.chunk_document(sample_text, {"source": "test"})
    
    print(f"Found {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ({chunk.chunk_type}) ---")
        print(f"Reference: {chunk.reference}")
        print(f"Chapter: {chunk.chapter}")
        print(f"Content preview: {chunk.content[:100]}...")
        print()
