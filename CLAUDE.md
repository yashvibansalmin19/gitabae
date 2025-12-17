# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitaBae is a Bhagavad Gita guidance chatbot that processes the Yatharth Gita text and provides spiritual guidance. The project is being built in phases:
- Phase 1: Data ingestion (current) - parsing Gita text into structured verse chunks
- Phase 2: Embeddings & vector store with Pinecone
- Phase 6: Streamlit UI

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run data ingestion pipeline
python src/ingestion.py [input_file] [output_file]

# Run tests
pytest
```

## Architecture

### Data Pipeline (`src/ingestion.py`)

The ingestion module parses Yatharth Gita text and structures it into verse-based chunks:

- **VerseChunk dataclass**: Core data structure containing chapter number, verse number (supports ranges like "1-2"), Sanskrit text, English translation, commentary, and tags (for future LLM tagging)
- **GitaParser class**: Handles parsing with Devanagari numeral conversion, verse boundary detection via `॥` markers, Sanskrit/translation/commentary extraction
- **Hybrid chunking**: Long commentaries (>400 words) are split with 50-word overlap, preserving sentence boundaries

### Environment Configuration

Uses OpenRouter API for LLM access and Pinecone for vector storage. Copy `.env.example` to `.env` and configure:
- `OPENROUTER_API_KEY` - for LLM calls
- `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` - for vector storage
