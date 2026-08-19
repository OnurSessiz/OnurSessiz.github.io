#!/usr/bin/env python3
"""notlar/ klasorundeki .txt notlarini notlar.json'a derler, 30 gunden eskileri siler.

Not bir dosyadir: notlar/ icine notepad ile yazip attigin her .txt bir kart olur.
- Baslik: dosya adi (tarih oneki ve tire/alt tire temizlenir)
- Tarih: dosya adindaki YYYY-MM-DD oneki, yoksa dosyanin repoya eklendigi commit tarihi
- Metin: 512 karaktere kirpilir
"""

import json
import os
import re
import subprocess
import unicodedata
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTES_DIR = os.path.join(ROOT, "notlar")
OUT = os.path.join(NOTES_DIR, "notlar.json")

MAX_CHARS = 512
MAX_AGE = timedelta(days=30)
DATE_PREFIX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[ ._-]*")

# Notepad "ANSI" olarak da kaydedebiliyor; Turkce karakterler bozulmasin diye sirayla dene.
ENCODINGS = ("utf-8-sig", "utf-8", "cp1254", "cp1252")


def read_text(path):
    with open(path, "rb") as fh:
        data = fh.read()
    for enc in ENCODINGS:
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", "replace")


def clean(text):
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) > MAX_CHARS:
        text = text[: MAX_CHARS - 1].rstrip() + "…"
    return text


def added_at(rel):
    """Dosyanin repoya eklendigi commit tarihi (ISO)."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%aI", "-1", "--", rel],
            cwd=ROOT, capture_output=True, text=True, check=False,
        ).stdout.strip()
    except OSError:
        out = ""
    if not out:
        return None
    try:
        return datetime.fromisoformat(out.splitlines()[0])
    except ValueError:
        return None


def title_of(stem):
    stem = DATE_PREFIX.sub("", stem)
    stem = re.sub(r"[-_]+", " ", stem).strip()
    return stem or "not"


def main():
    now = datetime.now(timezone.utc)
    os.makedirs(NOTES_DIR, exist_ok=True)

    notes, removed = [], []
    for name in sorted(os.listdir(NOTES_DIR)):
        if not name.lower().endswith(".txt"):
            continue
        path = os.path.join(NOTES_DIR, name)
        if not os.path.isfile(path):
            continue

        stem = name[:-4]
        m = DATE_PREFIX.match(stem)
        when = None
        if m:
            try:
                when = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
            except ValueError:
                when = None
        if when is None:
            when = added_at("notlar/" + name) or now

        if now - when > MAX_AGE:
            os.remove(path)
            removed.append(name)
            continue

        text = clean(read_text(path))
        if not text:
            continue
        notes.append({
            "id": stem,
            "title": title_of(stem),
            "date": when.astimezone(timezone.utc).isoformat(),
            "text": text,
        })

    notes.sort(key=lambda n: n["date"], reverse=True)
    payload = {"generated": now.isoformat(), "notes": notes}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("{} not derlendi, {} eski not silindi".format(len(notes), len(removed)))
    for name in removed:
        print("  silindi: " + name)


if __name__ == "__main__":
    main()
