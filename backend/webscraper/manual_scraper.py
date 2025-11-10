"""
fetch_gutenberg_book.py
Fetch a single Project Gutenberg book and store:
- Full text in ./documents/{id}.txt
- Metadata in ./documents_meta.json
"""

import requests
import re
import json
from pathlib import Path
import string

# -------------------------------
# Utilities
# -------------------------------

def extract_id_from_url(url: str) -> str:
    """Extract numeric eBook ID from a Gutenberg URL."""
    match = re.search(r"/(\d+)", url)
    if not match:
        raise ValueError(f"Could not extract ID from {url}")
    return match.group(1)


def clean_gutenberg_text(raw: str) -> str:
    """Strip Project Gutenberg header/footer boilerplate."""
    start_re = re.compile(r"\*\*\* START OF.*?\*\*\*", re.IGNORECASE)
    end_re = re.compile(r"\*\*\* END OF.*?\*\*\*", re.IGNORECASE)
    start = start_re.search(raw)
    end = end_re.search(raw)
    if start and end:
        return raw[start.end():end.start()].strip()
    return raw.strip()

def looks_like_postscript(text: str) -> bool:
    head = text[:2000]
    # Core PostScript markers
    if "%!PS" in head or "%%Creator" in head or "%%BoundingBox" in head:
        return True
    # Too many PostScript command words
    ps_tokens = sum(word in text[:50000] for word in [
        "moveto", "lineto", "stroke", "setfont", "findfont", "/Courier", "/Helvetica", "/Times"
    ])
    return ps_tokens > 5  # threshold for "definitely PS"

def is_valid_plaintext(text: str) -> bool:
    printable_ratio = sum(c in string.printable for c in text) / max(len(text), 1)
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    return printable_ratio > 0.9 and alpha_ratio > 0.2


def fetch_gutenberg_book(url: str) -> dict:
    """Download one book’s text and metadata from a Gutenberg URL."""
    book_id = extract_id_from_url(url)
    base = f"https://www.gutenberg.org/files/{book_id}/{book_id}"
    alt_base = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}"

    variants = [
        f"{base}-0.txt", f"{base}.txt", f"{base}.txt.utf-8",
        f"{alt_base}.txt", f"{alt_base}.txt.utf8"
    ]

    text = None
    for link in variants:
        try:
            resp = requests.get(link, timeout=10)
            if resp.ok and len(resp.text) > 2000:
                text = resp.text
                print(f"✅ Found text at {link}")
                break
        except Exception:
            continue

    if not text:
        raise RuntimeError(f"Could not fetch text for book {book_id}")
    
    if looks_like_postscript(text):
        raise RuntimeError(f"Book {book_id} appears to be PostScript — skipping.")

    if not is_valid_plaintext(text):
        raise RuntimeError(f"Book {book_id} seems non-text or binary — skipping.")

    # Fetch metadata page for title
    meta_url = f"https://www.gutenberg.org/ebooks/{book_id}"
    meta_resp = requests.get(meta_url, timeout=10)
    title_match = re.search(r"<title>(.*?)</title>", meta_resp.text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else f"Book {book_id}"

    cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
    clean_text = clean_gutenberg_text(text)

    return {
        "id": book_id,
        "title": title,
        "cover": cover_url,
        "text": clean_text,
    }



def append_metadata(book_data: dict, meta_path: Path):
    """Append metadata to documents_meta.json, creating if missing."""
    data = []
    if meta_path.exists():
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    # avoid duplicates
    if any(b["id"] == book_data["id"] for b in data):
        print(f"⚠️ Book {book_data['id']} already exists in {meta_path.name}")
        return

    data.append({
        "id": book_data["id"],
        "title": book_data["title"],
        "cover": book_data["cover"],
        "text_path": f"documents/{book_data['id']}.txt"
    })

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📝 Updated metadata file: {meta_path.name}")


def save_text(book_data: dict, docs_dir: Path):
    """Write full text to ./documents/{id}.txt."""
    docs_dir.mkdir(parents=True, exist_ok=True)
    text_path = docs_dir / f"{book_data['id']}.txt"
    with text_path.open("w", encoding="utf-8") as f:
        f.write(book_data["text"])
    print(f"📖 Saved text to {text_path}")


# -------------------------------
# Main script
# -------------------------------
if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    docs_dir = current_dir / "documents"
    meta_path = current_dir / "documents_meta.json"
    failed_path = current_dir / "failed_ids.txt"


    # Load existing IDs
    existing_ids = set()
    if meta_path.exists():
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                existing_ids = {int(b["id"]) for b in data}
            print(f"📂 Loaded {len(existing_ids)} existing IDs from metadata.")
        except Exception:
            print("⚠️ Could not read metadata; starting fresh.")

    for book_id in range(1, 2001):  # change range for your next batch
        if book_id in existing_ids:
            print(f"⏭️ Skipping already collected book {book_id}")
            continue

        url = f"https://www.gutenberg.org/ebooks/{book_id}"
        try:
            book = fetch_gutenberg_book(url)
            save_text(book, docs_dir)
            append_metadata(book, meta_path)
            print(f"✨ Done {book_id}.")
        except Exception as e:
            with failed_path.open("a", encoding="utf-8") as f:
                f.write(f"{book_id}\n")
            print(f"❌ Skipping {book_id}: {e}")

