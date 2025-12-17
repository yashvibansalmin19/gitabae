"""
LLM-based Verse Tagger for GitaBae.
Generates 2-3 thematic tags for each verse using OpenRouter/GPT.
"""

import json
import time
from pathlib import Path
from typing import Optional

from .config import get_openai_client, Config


# Predefined theme categories for consistency
THEME_CATEGORIES = [
    "duty", "dharma", "karma", "action", "work",
    "detachment", "renunciation", "surrender",
    "devotion", "bhakti", "faith", "worship",
    "knowledge", "wisdom", "self-realization", "enlightenment",
    "mind", "meditation", "focus", "concentration",
    "fear", "anxiety", "grief", "sorrow", "despair",
    "courage", "strength", "resilience",
    "ego", "pride", "humility",
    "anger", "desire", "attachment", "lust",
    "peace", "equanimity", "balance", "calm",
    "love", "compassion", "kindness",
    "truth", "righteousness", "ethics",
    "death", "immortality", "soul", "atman",
    "god", "divine", "brahman", "krishna",
    "yoga", "discipline", "practice",
    "nature", "prakriti", "gunas",
    "war", "conflict", "battle", "struggle",
    "friendship", "relationships", "family",
    "leadership", "guidance", "teaching",
    "success", "failure", "results",
    "happiness", "suffering", "pleasure", "pain"
]


TAGGING_PROMPT = """You are an expert on the Bhagavad Gita. Given a verse's translation and commentary, identify 2-3 key themes that best describe what this verse teaches.

Choose themes from this list (or use very similar terms):
{categories}

Verse Translation:
{translation}

Commentary:
{commentary}

Return ONLY a JSON array of 2-3 theme tags, nothing else. Example: ["duty", "action", "detachment"]

Tags:"""


class VerseTagger:
    """Tags verses with themes using LLM."""

    def __init__(self, model: str = None):
        """
        Initialize tagger.

        Args:
            model: LLM model to use (default from config)
        """
        Config.load()
        self.client = get_openai_client()
        self.model = model or Config.LLM_MODEL

    def tag_verse(self, translation: str, commentary: str) -> list[str]:
        """
        Generate tags for a single verse.

        Args:
            translation: English translation of the verse
            commentary: Commentary/explanation of the verse

        Returns:
            List of 2-3 theme tags
        """
        prompt = TAGGING_PROMPT.format(
            categories=", ".join(THEME_CATEGORIES[:30]),  # Use top categories
            translation=translation[:500],  # Limit length
            commentary=commentary[:800]
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3  # Lower temperature for consistency
            )

            result = response.choices[0].message.content.strip()

            # Parse JSON array
            tags = json.loads(result)

            # Validate and clean tags
            if isinstance(tags, list):
                tags = [t.lower().strip() for t in tags if isinstance(t, str)]
                return tags[:3]  # Max 3 tags

        except json.JSONDecodeError:
            # Try to extract tags from non-JSON response
            result = response.choices[0].message.content.strip()
            # Look for quoted words
            import re
            tags = re.findall(r'"([^"]+)"', result)
            if tags:
                return [t.lower().strip() for t in tags[:3]]

        except Exception as e:
            print(f"  Warning: Tagging failed - {e}")

        return []

    def tag_verses_batch(
        self,
        verses: list[dict],
        delay: float = 0.5,
        progress_callback: Optional[callable] = None
    ) -> list[dict]:
        """
        Tag multiple verses with rate limiting.

        Args:
            verses: List of verse dictionaries
            delay: Delay between API calls (seconds)
            progress_callback: Optional callback(current, total)

        Returns:
            List of verses with tags added
        """
        total = len(verses)
        tagged_verses = []

        for i, verse in enumerate(verses):
            # Get tags
            tags = self.tag_verse(
                verse.get("translation", ""),
                verse.get("commentary", "")
            )

            # Update verse with tags
            verse_copy = verse.copy()
            verse_copy["tags"] = tags
            tagged_verses.append(verse_copy)

            # Progress update
            if progress_callback:
                progress_callback(i + 1, total)
            else:
                print(f"  [{i+1}/{total}] Verse {verse.get('verse', '?')}: {tags}")

            # Rate limiting
            if i < total - 1:
                time.sleep(delay)

        return tagged_verses


def tag_chapter_file(
    input_path: str,
    output_path: str = None,
    delay: float = 0.5
) -> str:
    """
    Tag all verses in a chapter JSON file.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file (default: adds _tagged suffix)
        delay: Delay between API calls

    Returns:
        Path to output file
    """
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_tagged.json"
    else:
        output_path = Path(output_path)

    print(f"Loading verses from {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    verses = data.get("verses", [])
    print(f"Found {len(verses)} verses to tag")

    print(f"\nTagging verses (delay={delay}s between calls)...")
    tagger = VerseTagger()
    tagged_verses = tagger.tag_verses_batch(verses, delay=delay)

    # Update data
    data["verses"] = tagged_verses
    data["metadata"]["tagged"] = True

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved tagged verses to {output_path}")

    # Summary
    tag_counts = {}
    for v in tagged_verses:
        for tag in v.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\nTop tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {tag}: {count}")

    return str(output_path)


def main():
    """Main function to run tagging pipeline."""
    import sys

    input_file = "/Users/yashvi/Documents/Projects/gitabae/data/chapter_1.json"
    output_file = "/Users/yashvi/Documents/Projects/gitabae/data/chapter_1_tagged.json"

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print("=" * 60)
    print("GitaBae - Verse Tagging Pipeline")
    print("=" * 60)

    tag_chapter_file(input_file, output_file, delay=0.5)


if __name__ == "__main__":
    main()
