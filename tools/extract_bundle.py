#!/usr/bin/env python3
"""Eski index.html bundle'indan gorselleri ve fontlari dosyaya cikarir.

Site eskiden bir Claude Design Canvas artifact bundle'iydi: 24 webp
`window.__IMG` icinde base64, 8 woff2 de `__bundler/manifest` icinde gomuluydu.
Bu script onlari bir kez `assets/` altina yazar. Sonrasinda ise yaramaz ama
varliklarin nereden geldigini belgelemesi icin repoda duruyor.

Kullanim (eski index.html'in yolunu ver):

    python tools/extract_bundle.py path/to/eski-index.html

Eski surum git gecmisinde: git show f0c4bac:index.html > eski-index.html
"""

import base64
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# Turkce icin latin + latin-ext yetiyor; cyrillic/vietnamese subsetleri atiyoruz.
FONTS = {
    "35277208-472d-4549-888c-5f674ebcc274": "nunito-latin.woff2",
    "fc9afa2f-1607-40eb-8741-f2cb0fae8518": "nunito-latin-ext.woff2",
    "cbd74c33-9c35-436e-9c0a-d511a26c3a6a": "pixelify-latin.woff2",
    "099a72f1-ead9-4a69-aad4-4138342c6095": "pixelify-latin-ext.woff2",
}

EXT = {"image/webp": ".webp", "image/png": ".png", "image/jpeg": ".jpg"}


def section(src, kind):
    m = re.search(r'<script type="__bundler/%s">(.*?)</script>' % kind, src, re.S)
    if not m:
        sys.exit("bundle icinde __bundler/%s bulunamadi" % kind)
    return m.group(1)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = open(sys.argv[1], encoding="utf-8").read()

    template = json.loads(section(src, "template"))
    manifest = json.loads(section(src, "manifest"))

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(FONT_DIR, exist_ok=True)

    start = template.find("window.__IMG=")
    end = template.find("</script>", start)
    images = json.loads(template[start + len("window.__IMG=") : end].rstrip().rstrip(";"))

    total = 0
    for name, uri in sorted(images.items()):
        header, payload = uri.split(",", 1)
        mime = header[5:].split(";")[0]
        raw = base64.b64decode(payload)
        path = os.path.join(IMG_DIR, name + EXT.get(mime, ".bin"))
        with open(path, "wb") as fh:
            fh.write(raw)
        total += len(raw)
        print("img  %-18s %7.1f KB" % (name, len(raw) / 1024))

    for uuid, filename in FONTS.items():
        entry = manifest.get(uuid)
        if not entry:
            print("font ATLANDI (manifestte yok): %s" % filename)
            continue
        raw = base64.b64decode(entry["data"])
        with open(os.path.join(FONT_DIR, filename), "wb") as fh:
            fh.write(raw)
        total += len(raw)
        print("font %-18s %7.1f KB" % (filename, len(raw) / 1024))

    print("\ntoplam %.2f MB -> assets/" % (total / 1024 / 1024))


if __name__ == "__main__":
    main()
