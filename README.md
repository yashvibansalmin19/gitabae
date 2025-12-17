# GitaBae

> Your wise friend for life's questions - A modern chatbot that provides life guidance using wisdom from the Bhagavad Gita.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gitabae.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-73%20passing-brightgreen.svg)](#running-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**[Try GitaBae Live](https://gitabae.streamlit.app/)**

---

## What is GitaBae?

GitaBae is an AI-powered chatbot that helps young professionals navigate life's challenges using timeless wisdom from the Bhagavad Gita. Whether you're dealing with career anxiety, relationship dilemmas, finding your purpose, or just need someone to talk to - GitaBae is here to help.

### Key Features

- **Conversational AI** - Chat naturally like you're talking to a wise friend
- **Multi-turn Memory** - Follows up on previous messages for flowing conversations
- **Semantic Search** - Finds the most relevant verses for your situation
- **Safety First** - Built-in content moderation and topic filtering
- **Source Transparency** - See the exact verses behind every response

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **LLM** | GPT-3.5-turbo via [OpenRouter](https://openrouter.ai/) |
| **Embeddings** | OpenAI text-embedding-ada-002 |
| **Vector Store** | [Pinecone](https://www.pinecone.io/) |
| **Deployment** | [Streamlit Cloud](https://streamlit.io/cloud) |

---

## How It Works

```
User Question → Embedding → Pinecone Search → Relevant Verses → LLM + Context → Response
```

1. **Embedding**: Your question is converted to a 1536-dimension vector
2. **Retrieval**: Pinecone finds the most semantically similar verses
3. **Generation**: GPT-3.5-turbo crafts a response using the retrieved wisdom
4. **Safety**: All inputs/outputs are checked for harmful content

---

## Project Structure

```
gitabae/
├── app.py                    # Streamlit application
├── src/
│   ├── config.py             # API configuration
│   ├── retriever.py          # Semantic search system
│   ├── generator.py          # LLM response generation
│   ├── safety.py             # Content moderation
│   ├── ingestion.py          # Data pipeline
│   ├── tagger.py             # Verse tagging
│   ├── embeddings.py         # Vector generation
│   └── vectorstore.py        # Pinecone operations
├── data/
│   └── chapter_1_tagged.json # 47 verses with metadata
├── tests/
│   ├── test_phase2.py        # 25 tests
│   ├── test_phase3.py        # 24 tests
│   └── test_phase4.py        # 24 tests
├── .streamlit/
│   ├── config.toml           # Theme configuration
│   └── secrets.toml.example  # Secrets template
├── requirements.txt
└── README.md
```

---

## Local Development

### Prerequisites

- Python 3.10+
- [OpenRouter API key](https://openrouter.ai/keys)
- [Pinecone API key](https://app.pinecone.io/)

### Installation

```bash
# Clone the repository
git clone https://github.com/yashvibansalmin19/gitabae.git
cd gitabae

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally

```bash
streamlit run app.py
```

Opens at: http://localhost:8501

### Running Tests

```bash
# All tests (73 total)
pytest tests/ -v

# Individual phases
pytest tests/test_phase2.py -v  # Embeddings & Vector Store
pytest tests/test_phase3.py -v  # Retrieval System
pytest tests/test_phase4.py -v  # Safety Layer
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM calls | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector search | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `gitabae`) | Yes |
| `LLM_MODEL` | Model to use (default: `openai/gpt-3.5-turbo`) | No |

### For Streamlit Cloud

Add secrets in your Streamlit Cloud dashboard:

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
PINECONE_API_KEY = "pcsk_..."
PINECONE_INDEX_NAME = "gitabae"
LLM_MODEL = "openai/gpt-3.5-turbo"
```

---

## Topics Covered

GitaBae can help with questions about:

- **Career & Purpose** - Finding direction, job anxiety, decision making
- **Stress & Anxiety** - Overthinking, fear, worry about the future
- **Relationships** - Dealing with difficult people, family conflicts
- **Self-improvement** - Motivation, discipline, letting go of the past
- **Life Philosophy** - Duty, dharma, detachment, inner peace

---

## Safety & Moderation

GitaBae includes built-in safety measures:

- **Topic Filtering** - Redirects medical, legal, financial, and political queries to appropriate resources
- **Crisis Support** - Provides helpline information for mental health concerns
- **Content Blocking** - Blocks harmful or inappropriate requests
- **Prompt Injection Protection** - Sanitizes inputs to prevent misuse

---

## Current Limitations

- **Chapter 1 Only** - Currently uses 47 verses from Chapter 1 of the Yatharth Gita
- **English Only** - Responses are in English
- **No Audio** - Text-only interface (Sanskrit pronunciation not available)

---

## Roadmap

- [ ] Add remaining 17 chapters (700 verses)
- [ ] User feedback system (thumbs up/down)
- [ ] Response streaming
- [ ] Dark mode
- [ ] Mobile optimization

---

## Acknowledgments

- **[Yatharth Gita](https://www.yatharthgeeta.com/)** - Primary source text (English edition)
- **Swami Adgadanand Ji Maharaj** - Author and spiritual guide
- Built with [Streamlit](https://streamlit.io/), [OpenRouter](https://openrouter.ai/), and [Pinecone](https://www.pinecone.io/)

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://gitabae.streamlit.app/">
    <strong>Try GitaBae Now</strong>
  </a>
</p>
