# GitaBae

A modern chatbot that provides life guidance to young professionals using wisdom from the Bhagavad Gita.

## Overview

GitaBae is an interactive Streamlit application that empowers young professionals to seek life guidance via natural language queries, leveraging the Yatharth Gita (English) as its primary source. The chatbot interprets user questions, semantically searches the text of the Gita, and generates thoughtful, context-sensitive responses rooted in the scripture.

## Features

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

## Project Structure

```
gitabae/
├── data/
│   ├── chapter_1_tagged.json       # Verses with tags
│   └── chapter_1_embeddings.json   # Vector embeddings
├── src/
│   ├── config.py                   # API configuration
│   ├── ingestion.py                # Data ingestion
│   ├── tagger.py                   # LLM tagging
│   ├── embeddings.py               # Embedding generation
│   ├── vectorstore.py              # Pinecone operations
│   └── retriever.py                # Semantic retrieval
├── tests/
│   ├── test_phase2.py
│   └── test_phase3.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- OpenRouter API key
- Pinecone API key

### Installation

```bash
git clone https://github.com/yashvibansalmin19/gitabae.git
cd gitabae
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Running Tests

```bash
pytest tests/ -v
```

## Configuration

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Index name (default: `gitabae`) |

## License

MIT

## Acknowledgments

- Yatharth Gita (English) - Primary source text
- Swami Adgadanand Ji Maharaj - Author
