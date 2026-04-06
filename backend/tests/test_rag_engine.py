"""
Tests for RAG Engine
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.prompts import (
    LEGAL_ASSISTANT_PROMPT,
    format_context,
    build_rag_prompt,
    NO_CONTEXT_PROMPT
)


class TestPrompts:
    """Tests for prompt generation"""
    
    def test_legal_prompt_exists(self):
        """Test that legal assistant prompt is defined"""
        assert LEGAL_ASSISTANT_PROMPT is not None
        assert len(LEGAL_ASSISTANT_PROMPT) > 100
        assert "V-Legal Bot" in LEGAL_ASSISTANT_PROMPT
    
    def test_legal_prompt_has_key_elements(self):
        """Test that prompt contains key instructions"""
        prompt = LEGAL_ASSISTANT_PROMPT
        
        # Should instruct to cite sources
        assert "trích dẫn" in prompt.lower() or "nguồn" in prompt.lower()
        
        # Should mention staying within context
        assert "tài liệu" in prompt.lower() or "dữ liệu" in prompt.lower()
    
    def test_no_context_prompt(self):
        """Test fallback prompt when no context found"""
        assert NO_CONTEXT_PROMPT is not None
        assert "không tìm thấy" in NO_CONTEXT_PROMPT.lower()
    
    def test_build_rag_prompt_with_results(self):
        """Test building RAG prompt with search results"""
        # Create mock search result
        class MockResult:
            content = "Điều 1. Nội dung điều 1."
            reference = "Điều 1, Luật Test"
            score = 0.95
            metadata = {"filename": "test.docx"}
        
        results = [MockResult()]
        prompt = build_rag_prompt("Câu hỏi test?", results)
        
        assert "Câu hỏi test?" in prompt
        assert "Điều 1" in prompt
        assert "0.95" in prompt or "95" in prompt  # Score format
    
    def test_build_rag_prompt_no_results(self):
        """Test building RAG prompt with no results"""
        prompt = build_rag_prompt("Câu hỏi test?", [])
        
        assert prompt == NO_CONTEXT_PROMPT


class TestFormatContext:
    """Tests for context formatting"""
    
    def test_format_empty_results(self):
        """Test formatting empty results"""
        result = format_context([])
        assert "không tìm thấy" in result.lower()
    
    def test_format_multiple_results(self):
        """Test formatting multiple results"""
        class MockResult:
            def __init__(self, num):
                self.content = f"Nội dung {num}"
                self.reference = f"Điều {num}"
                self.score = 0.9 - (num * 0.1)
        
        results = [MockResult(1), MockResult(2)]
        formatted = format_context(results)
        
        assert "[Nguồn 1]" in formatted
        assert "[Nguồn 2]" in formatted
        assert "Điều 1" in formatted
        assert "Điều 2" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
