# GitaBae

A modern chatbot that provides life guidance to young professionals using wisdom from the Bhagavad Gita.

## Overview

GitaBae is an interactive Streamlit application that empowers young professionals to seek life guidance via natural language queries, leveraging the Yatharth Gita (English) as its primary source. The chatbot interprets user questions, semantically searches the text of the Gita, and generates thoughtful, context-sensitive responses rooted in the scripture.

## Features (Planned)

- Natural language queries for life guidance
- Semantic search across Bhagavad Gita verses
- Context-aware responses with verse citations
- LLM-generated thematic tags for better retrieval
- Safety layer for content moderation
- Modern, responsive chat interface

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM Provider | OpenRouter (GPT-3.5-turbo) |
| Embeddings | OpenAI text-embedding-ada-002 |
| Vector Store | Pinecone |
| Framework | LangChain |

## Project Structure

```
gitabae/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
├── .streamlit/             # Streamlit configuration
├── data/
│   ├── chapter_1.json           # Parsed Gita verses
│   ├── chapter_1_tagged.json    # Verses with LLM-generated tags
│   └── chapter_1_embeddings.json # Vector embeddings
├── src/
│   ├── __init__.py
│   ├── config.py           # API configuration (OpenRouter, Pinecone)
│   ├── ingestion.py        # Data ingestion pipeline
│   ├── tagger.py           # LLM-based verse tagging
│   ├── embeddings.py       # Embedding generation
│   └── vectorstore.py      # Pinecone operations
├── tests/                  # Unit tests
├── .env.example            # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Development Phases

### Phase 1: Data Ingestion Pipeline

**Status: Complete**

- [x] PDF/TXT parsing for Yatharth Gita
- [x] Verse extraction with metadata (chapter, verse, sanskrit, translation, commentary)
- [x] Hybrid chunking strategy (preserves short commentaries, splits long ones at ~400 words)
- [x] JSON output for downstream processing

### Phase 2: Embeddings & Vector Store

**Status: Complete**

- [x] LLM-based verse tagging (2-3 themes per verse using GPT-3.5-turbo)
- [x] Generate embeddings using OpenAI text-embedding-ada-002 via OpenRouter
- [x] Store vectors in Pinecone (47 vectors, 1536 dimensions)
- [x] Semantic search retrieval working

**Tagged Data Schema:**
```json
{
  "chapter": 1,
  "verse": "1",
  "sanskrit": "धृतराष्र उवाच...",
  "translation": "Dhritrashtr said...",
  "commentary": "Dhritrashtr is the very image of ignorance...",
  "tags": ["dharma", "knowledge", "ego"]
}
```

**Top Tags in Chapter 1:**
- duty (32 verses)
- surrender (16 verses)
- faith (11 verses)
- knowledge (10 verses)
- dharma (8 verses)

### Phase 3: Retrieval System (Upcoming)

- [ ] Query embedding
- [ ] Semantic similarity search
- [ ] Context assembly

### Phase 4: Safety Layer (Upcoming)

- [ ] OpenAI Moderation API integration
- [ ] Custom topic filters (politics, medical, legal)
- [ ] Graceful redirect responses

### Phase 5: Response Generation (Upcoming)

- [ ] Prompt engineering
- [ ] Context injection
- [ ] Response formatting (verse + translation + explanation)

### Phase 6: Streamlit UI (Upcoming)

- [ ] Chat interface
- [ ] Message history
- [ ] Responsive design

### Phase 7: Deployment (Upcoming)

- [ ] Streamlit Cloud deployment
- [ ] GitHub Actions CI pipeline
- [ ] Secrets management

## Setup

### Prerequisites

- Python 3.10+
- OpenRouter API key
- Pinecone API key (with index `gitabae`, 1536 dimensions, cosine metric)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yashvibansalmin19/gitabae.git
cd gitabae
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Pipelines

**Phase 1 - Ingestion:**
```bash
python -m src.ingestion
```

**Phase 2 - Tagging:**
```bash
python -m src.tagger
```

**Phase 2 - Embeddings & Upload:**
```bash
python -m src.embeddings
python -m src.vectorstore
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `PINECONE_API_KEY` | Your Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `gitabae`) |
| `LLM_MODEL` | LLM model to use (default: `openai/gpt-3.5-turbo`) |
| `EMBEDDING_MODEL` | Embedding model (default: `openai/text-embedding-ada-002`) |

## Sample Retrieval Results

Query: *"How do I deal with anxiety and fear?"*

| Rank | Verse | Score | Tags |
|------|-------|-------|------|
| 1 | Ch1, V30 | 0.77 | fear, anxiety, courage |
| 2 | Ch1, V21 | 0.77 | duty, faith, surrender |
| 3 | Ch1, V26 | 0.76 | duty, surrender, faith |

## Contributing

This is a portfolio project. Contributions, issues, and feature requests are welcome!

## License

MIT

## Acknowledgments

- Yatharth Gita (English) - Primary source text
- Swami Adgadanand Ji Maharaj - Author of Yatharth Geeta
