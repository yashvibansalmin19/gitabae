"""
Embeddings Generator for GitaBae.
Generates vector embeddings for verse content using OpenAI via OpenRouter.
"""

import json
import time
from pathlib import Path
from typing import Optional

from .config import get_openai_client, Config


class EmbeddingsGenerator:
    """Generates embeddings for verse content."""

    def __init__(self, model: str = None):
        """
        Initialize embeddings generator.

        Args:
            model: Embedding model to use (default from config)
        """
        Config.load()
        self.client = get_openai_client()
        self.model = model or Config.EMBEDDING_MODEL

    def _prepare_text(self, verse: dict) -> str:
        """
        Prepare verse content for embedding.
        Combines translation, commentary, and tags for rich semantic representation.

        Args:
            verse: Verse dictionary

        Returns:
            Combined text for embedding
        """
        parts = []

        # Add translation
        translation = verse.get("translation", "").strip()
        if translation:
            parts.append(f"Translation: {translation}")

        # Add commentary
        commentary = verse.get("commentary", "").strip()
        if commentary:
            parts.append(f"Commentary: {commentary}")

        # Add tags for semantic boost
        tags = verse.get("tags", [])
        if tags:
            parts.append(f"Themes: {', '.join(tags)}")

        return "\n\n".join(parts)

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector)
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )

        return response.data[0].embedding

    def generate_embeddings_batch(
        self,
        verses: list[dict],
        delay: float = 0.2,
        progress_callback: Optional[callable] = None
    ) -> list[dict]:
        """
        Generate embeddings for multiple verses.

        Args:
            verses: List of verse dictionaries
            delay: Delay between API calls (seconds)
            progress_callback: Optional callback(current, total)

        Returns:
            List of dicts with verse data and embeddings
        """
        total = len(verses)
        results = []

        for i, verse in enumerate(verses):
            # Prepare text
            text = self._prepare_text(verse)

            # Generate embedding
            try:
                embedding = self.generate_embedding(text)

                result = {
                    "id": f"ch{verse['chapter']}_v{verse['verse']}",
                    "values": embedding,
                    "metadata": {
                        "chapter": verse["chapter"],
                        "verse": verse["verse"],
                        "sanskrit": verse.get("sanskrit", "")[:500],
                        "translation": verse.get("translation", "")[:500],
                        "commentary": verse.get("commentary", "")[:1000],
                        "tags": verse.get("tags", []),
                        "text": text[:2000]  # Store searchable text
                    }
                }
                results.append(result)

            except Exception as e:
                print(f"  Error embedding verse {verse.get('verse', '?')}: {e}")
                continue

            # Progress update
            if progress_callback:
                progress_callback(i + 1, total)
            else:
                print(f"  [{i+1}/{total}] Verse {verse.get('verse', '?')}: {len(embedding)} dims")

            # Rate limiting
            if i < total - 1:
                time.sleep(delay)

        return results


def generate_embeddings_from_file(
    input_path: str,
    output_path: str = None,
    delay: float = 0.2
) -> str:
    """
    Generate embeddings for all verses in a JSON file.

    Args:
        input_path: Path to input JSON file (tagged verses)
        output_path: Path to output JSON file (default: adds _embeddings suffix)
        delay: Delay between API calls

    Returns:
        Path to output file
    """
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem.replace('_tagged', '')}_embeddings.json"
    else:
        output_path = Path(output_path)

    print(f"Loading verses from {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    verses = data.get("verses", [])
    print(f"Found {len(verses)} verses to embed")

    print(f"\nGenerating embeddings (delay={delay}s between calls)...")
    generator = EmbeddingsGenerator()
    embedded_verses = generator.generate_embeddings_batch(verses, delay=delay)

    # Save embeddings
    output_data = {
        "metadata": {
            "source": data.get("metadata", {}).get("source", ""),
            "chapter": data.get("metadata", {}).get("chapter", 1),
            "total_vectors": len(embedded_verses),
            "embedding_model": Config.EMBEDDING_MODEL,
            "dimensions": len(embedded_verses[0]["values"]) if embedded_verses else 0
        },
        "vectors": embedded_verses
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(embedded_verses)} embeddings to {output_path}")
    print(f"Embedding dimensions: {output_data['metadata']['dimensions']}")

    return str(output_path)


def main():
    """Main function to run embedding generation."""
    import sys

    input_file = "/Users/yashvi/Documents/Projects/gitabae/data/chapter_1_tagged.json"
    output_file = "/Users/yashvi/Documents/Projects/gitabae/data/chapter_1_embeddings.json"

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print("=" * 60)
    print("GitaBae - Embeddings Generator")
    print("=" * 60)

    generate_embeddings_from_file(input_file, output_file, delay=0.2)


if __name__ == "__main__":
    main()
