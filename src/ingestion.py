"""
Data Ingestion Pipeline for GitaBae
Parses Yatharth Gita text and structures it into verse-based chunks.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class VerseChunk:
    """Represents a single verse with its metadata."""
    chapter: int
    verse: str  # Can be "1" or "1-2" for combined verses
    sanskrit: str
    translation: str
    commentary: str
    tags: list[str]  # To be populated by LLM in Phase 2

    def to_dict(self) -> dict:
        return asdict(self)

    def word_count(self) -> int:
        """Returns word count of commentary."""
        return len(self.commentary.split())


class GitaParser:
    """Parser for Yatharth Gita text content."""

    # Devanagari numerals mapping
    DEVANAGARI_NUMS = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }

    # Regex patterns
    CHAPTER_PATTERN = r'CHAPTER\s*:\s*(\d+)'
    VERSE_NUM_PATTERN = r'॥\s*([०-९\d]+(?:\s*-\s*[०-९\d]+)?)\s*॥'
    TRANSLATION_PATTERN = r'\[\s*([^\]]+)\s*\]'
    SANSKRIT_PATTERN = r'[\u0900-\u097F]+'  # Devanagari Unicode range

    def __init__(self, max_chunk_words: int = 400):
        """
        Initialize parser with chunking threshold.

        Args:
            max_chunk_words: Maximum words before splitting commentary (hybrid chunking)
        """
        self.max_chunk_words = max_chunk_words

    def _devanagari_to_arabic(self, text: str) -> str:
        """Convert Devanagari numerals to Arabic numerals."""
        for dev, arab in self.DEVANAGARI_NUMS.items():
            text = text.replace(dev, arab)
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page artifacts
        text = re.sub(r'\s*\d+\s*$', '', text)  # Page numbers at end
        return text.strip()

    def _extract_chapter_info(self, text: str) -> tuple[int, str]:
        """Extract chapter number and title."""
        chapter_match = re.search(self.CHAPTER_PATTERN, text, re.IGNORECASE)
        chapter_num = int(chapter_match.group(1)) if chapter_match else 1

        # Try to extract chapter title (line after CHAPTER : X)
        title_match = re.search(r'CHAPTER\s*:\s*\d+\s*\n\s*([^\n]+)', text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""

        return chapter_num, title

    def _find_verse_boundaries(self, text: str) -> list[tuple[int, str]]:
        """Find all verse number positions and their numbers."""
        boundaries = []
        for match in re.finditer(self.VERSE_NUM_PATTERN, text):
            verse_num = self._devanagari_to_arabic(match.group(1))
            verse_num = verse_num.replace(' ', '')  # Clean spaces in ranges
            boundaries.append((match.end(), verse_num))
        return boundaries

    def _extract_sanskrit_block(self, text: str) -> str:
        """Extract Sanskrit text (Devanagari script) from a block."""
        # Find continuous Devanagari text blocks
        sanskrit_parts = re.findall(r'[\u0900-\u097F\s।॥०-९]+', text)
        if sanskrit_parts:
            # Join and clean
            sanskrit = ' '.join(sanskrit_parts)
            sanskrit = re.sub(r'\s+', ' ', sanskrit).strip()
            return sanskrit
        return ""

    def _extract_translation(self, text: str) -> str:
        """Extract English translation from brackets."""
        # Find the first bracketed translation
        match = re.search(r'\[\s*([^\]]+)\s*\]', text, re.DOTALL)
        if match:
            translation = match.group(1)
            # Clean up inline footnotes
            translation = re.sub(r'\*\s*\[[^\]]*\]', '', translation)
            return self._clean_text(translation)
        return ""

    def _extract_commentary(self, text: str) -> str:
        """Extract commentary (text after translation)."""
        # Remove Sanskrit text
        text = re.sub(r'[\u0900-\u097F।॥०-९]+', '', text)
        # Remove translation brackets
        text = re.sub(r'\[[^\]]*\]', '', text)
        # Clean up footnotes but keep their content readable
        text = re.sub(r'\*\s*\([^\)]*\)', '', text)
        text = re.sub(r'\*\s*\[[^\]]*\]', '', text)
        return self._clean_text(text)

    def _split_long_commentary(self, verse: VerseChunk) -> list[VerseChunk]:
        """
        Split verse with long commentary into multiple chunks (hybrid chunking).

        If commentary exceeds max_chunk_words, split into smaller chunks
        while preserving verse metadata.
        """
        if verse.word_count() <= self.max_chunk_words:
            return [verse]

        chunks = []
        words = verse.commentary.split()

        # Split into chunks with overlap
        chunk_size = self.max_chunk_words
        overlap = 50  # Word overlap between chunks

        i = 0
        part = 1
        while i < len(words):
            end = min(i + chunk_size, len(words))
            chunk_words = words[i:end]

            # Try to end at sentence boundary
            chunk_text = ' '.join(chunk_words)
            last_period = chunk_text.rfind('.')
            if last_period > len(chunk_text) * 0.7:  # If period is in last 30%
                chunk_text = chunk_text[:last_period + 1]
                actual_words = len(chunk_text.split())
                end = i + actual_words

            chunk = VerseChunk(
                chapter=verse.chapter,
                verse=f"{verse.verse}" if part == 1 else f"{verse.verse} (part {part})",
                sanskrit=verse.sanskrit if part == 1 else "",
                translation=verse.translation if part == 1 else "",
                commentary=chunk_text,
                tags=verse.tags.copy()
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            i = end - overlap if end < len(words) else end
            part += 1

        return chunks

    def parse_text(self, text: str) -> list[VerseChunk]:
        """
        Parse Gita text and extract structured verses.

        Args:
            text: Raw text content from Gita

        Returns:
            List of VerseChunk objects
        """
        verses = []

        # Get chapter info
        chapter_num, chapter_title = self._extract_chapter_info(text)

        # Find verse boundaries
        boundaries = self._find_verse_boundaries(text)

        if not boundaries:
            print(f"Warning: No verses found in text")
            return verses

        print(f"Found {len(boundaries)} verses in Chapter {chapter_num}")

        # Extract content for each verse
        for i, (pos, verse_num) in enumerate(boundaries):
            # Get text until next verse or end
            if i + 1 < len(boundaries):
                next_pos = boundaries[i + 1][0]
                # Find the start of Sanskrit for next verse (go back a bit)
                search_start = max(0, next_pos - 500)
                verse_text = text[pos:search_start + 500]

                # Find where next Sanskrit block starts
                next_sanskrit = re.search(r'[\u0900-\u097F]{10,}', text[search_start:next_pos])
                if next_sanskrit:
                    end_pos = search_start + next_sanskrit.start()
                else:
                    end_pos = next_pos - 100  # Rough estimate

                verse_text = text[pos:end_pos]
            else:
                verse_text = text[pos:]

            # Extract components
            translation = self._extract_translation(verse_text)
            commentary = self._extract_commentary(verse_text)

            # Get Sanskrit from before the verse number
            sanskrit_search_start = max(0, pos - 300)
            sanskrit_block = text[sanskrit_search_start:pos]
            sanskrit = self._extract_sanskrit_block(sanskrit_block)

            verse = VerseChunk(
                chapter=chapter_num,
                verse=verse_num,
                sanskrit=sanskrit,
                translation=translation,
                commentary=commentary,
                tags=[]  # Will be populated by LLM in Phase 2
            )

            verses.append(verse)

        print(f"Extracted {len(verses)} verses")
        return verses

    def apply_hybrid_chunking(self, verses: list[VerseChunk]) -> list[VerseChunk]:
        """
        Apply hybrid chunking strategy.

        - Short commentaries: Keep as-is
        - Long commentaries (>max_chunk_words): Split with overlap
        """
        chunked_verses = []
        split_count = 0

        for verse in verses:
            chunks = self._split_long_commentary(verse)
            if len(chunks) > 1:
                split_count += 1
            chunked_verses.extend(chunks)

        print(f"Applied hybrid chunking: {len(verses)} verses -> {len(chunked_verses)} chunks")
        print(f"  ({split_count} verses were split due to long commentary)")

        return chunked_verses

    def parse_file(self, file_path: str) -> list[VerseChunk]:
        """
        Parse Gita content from a file.

        Args:
            file_path: Path to text file

        Returns:
            List of VerseChunk objects with hybrid chunking applied
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Reading file: {file_path}")
        text = path.read_text(encoding='utf-8')

        verses = self.parse_text(text)
        chunked_verses = self.apply_hybrid_chunking(verses)

        return chunked_verses

    def save_to_json(self, verses: list[VerseChunk], output_path: str) -> None:
        """Save parsed verses to JSON file."""
        data = {
            "metadata": {
                "source": "Yatharth Gita (English)",
                "total_chunks": len(verses),
                "chapters": list(set(v.chapter for v in verses))
            },
            "verses": [v.to_dict() for v in verses]
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(verses)} chunks to {output_path}")


def main():
    """Main function to run the ingestion pipeline."""
    import sys

    # Default paths
    input_file = "/Users/yashvi/Downloads/GitaChapter1_content.txt"
    output_file = "/Users/yashvi/Documents/Projects/gitabae/data/chapter_1.json"

    # Allow command line override
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print("=" * 60)
    print("GitaBae - Data Ingestion Pipeline")
    print("=" * 60)

    # Initialize parser with hybrid chunking threshold
    parser = GitaParser(max_chunk_words=400)

    # Parse the file
    verses = parser.parse_file(input_file)

    # Save to JSON
    parser.save_to_json(verses, output_file)

    # Print summary
    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"Total chunks created: {len(verses)}")

    # Show sample
    if verses:
        print("\nSample chunk (first verse):")
        print("-" * 40)
        sample = verses[0]
        print(f"Chapter: {sample.chapter}")
        print(f"Verse: {sample.verse}")
        print(f"Sanskrit: {sample.sanskrit[:100]}..." if len(sample.sanskrit) > 100 else f"Sanskrit: {sample.sanskrit}")
        print(f"Translation: {sample.translation[:150]}..." if len(sample.translation) > 150 else f"Translation: {sample.translation}")
        print(f"Commentary: {sample.commentary[:200]}..." if len(sample.commentary) > 200 else f"Commentary: {sample.commentary}")
        print(f"Word count: {sample.word_count()}")


if __name__ == "__main__":
    main()
