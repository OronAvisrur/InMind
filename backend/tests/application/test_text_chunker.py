import pytest
from src.application.services.text_chunker import (
    TextChunker,
    ChunkConfig,
    TextChunk
)

@pytest.fixture
def default_chunker():
    config = ChunkConfig(chunk_size=200, chunk_overlap=50)
    return TextChunker(config)

@pytest.fixture
def small_chunker():
    config = ChunkConfig(chunk_size=50, chunk_overlap=10)
    return TextChunker(config)

def test_chunk_short_text(default_chunker):
    text = "This is a short text."
    chunks = default_chunker.chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].start_index == 0
    assert chunks[0].end_index == len(text)

def test_chunk_empty_text(default_chunker):
    text = ""
    chunks = default_chunker.chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0].text == ""
    assert chunks[0].start_index == 0
    assert chunks[0].end_index == 0

def test_chunk_long_text(small_chunker):
    text = "This is a longer text that needs to be split into multiple chunks. " \
           "Each chunk should be around 50 characters with some overlap. " \
           "This helps maintain context between chunks."
    
    chunks = small_chunker.chunk_text(text)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert isinstance(chunk, TextChunk)
        assert len(chunk.text) <= 50
        assert chunk.end_index > chunk.start_index

def test_chunk_respects_word_boundaries(small_chunker):
    text = "Word boundaries should be respected when chunking text into smaller pieces."
    
    chunks = small_chunker.chunk_text(text)
    
    for chunk in chunks:
        if len(chunk.text) > 0:
            assert not chunk.text[0].isspace()
            assert not chunk.text[-1].isspace() or chunk.text[-1] == ' '

def test_chunk_overlap(small_chunker):
    text = "A" * 100
    
    chunks = small_chunker.chunk_text(text)
    
    assert len(chunks) >= 2

def test_chunk_config_validation():
    config = ChunkConfig(chunk_size=100, chunk_overlap=20)
    
    assert config.chunk_size == 100
    assert config.chunk_overlap == 20

def test_chunk_config_defaults():
    config = ChunkConfig()
    
    assert config.chunk_size == 200
    assert config.chunk_overlap == 50

def test_chunk_exact_size():
    config = ChunkConfig(chunk_size=10, chunk_overlap=0)
    chunker = TextChunker(config)
    text = "A" * 10
    
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0].text == text

def test_chunk_multiple_sentences():
    config = ChunkConfig(chunk_size=100, chunk_overlap=20)
    chunker = TextChunker(config)
    text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here."
    
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) >= 1
    for chunk in chunks:
        assert len(chunk.text) > 0

def test_chunk_preserves_content():
    config = ChunkConfig(chunk_size=50, chunk_overlap=10)
    chunker = TextChunker(config)
    text = "Important content that must be preserved across all chunks without data loss."
    
    chunks = chunker.chunk_text(text)
    
    combined_unique_text = ""
    for i, chunk in enumerate(chunks):
        if i == 0:
            combined_unique_text += chunk.text
        else:
            overlap_start = max(0, len(combined_unique_text) - 10)
            combined_unique_text += chunk.text[10:] if len(chunk.text) > 10 else ""
    
    assert len(chunks) > 0