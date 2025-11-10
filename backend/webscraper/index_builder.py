""""
index_builder.py
Build an inverted index from Gutenberg text corpus.

Requires:
- documents_meta.json (technically not needed as id can be fetched using the id.txt path name of the books in documents folder)
- ./documents/{id}.txt
Outputs:
- search_index.json
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

class FastIndexBuilder:
    def __init__(self, docs_dir: Path, output_path: Path):
        self.docs_dir = docs_dir
        self.output_path = output_path
        self.inverted_index = defaultdict(dict)

    def tokenize(self, text: str):
        """Extract lowercase alphabetic tokens."""
        return re.findall(r"[a-zA-Z]+", text.lower())

    def build_index(self):
        """Iterate over all .txt files and build the inverted index."""
        text_files = list(self.docs_dir.glob("*.txt"))
        print(f"📚 Found {len(text_files)} text files")

        for file_path in text_files:
            doc_id = file_path.stem  # e.g., "1" from "1.txt"
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                counts = Counter(self.tokenize(text))
                for word, freq in counts.items():
                    self.inverted_index[word][doc_id] = freq
                print(f"✅ Indexed {doc_id} ({len(counts)} unique terms)")
            except Exception as e:
                print(f"⚠️ Skipped {doc_id}: {e}")

        print(f"✅ Built inverted index with {len(self.inverted_index)} unique words.")

    def save_index(self):
        """Write index to JSON."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.inverted_index, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved inverted index to {self.output_path}")


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    docs_dir = current_dir / "documents"
    output_path = current_dir / "search_index.json"

    builder = FastIndexBuilder(docs_dir, output_path)
    builder.build_index()
    builder.save_index()
    print("✨ Done.")
