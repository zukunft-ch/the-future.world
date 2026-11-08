#!/usr/bin/env python3
"""Encode the site's AI-generated visuals and write the catalogue the avenir macros read.

Source of truth: visuals/slots.toml (slot, page, prompt scene, alt text).
A slot is published only when visuals/incoming/<slot>.png exists. For those slots this writes
static/visuals/<slot>-{600,960,1536}.{avif,webp,jpg} (ImageMagick), visuals/catalog.json and
visuals/provenance.json. Unchanged originals (same SHA-256 as in provenance) are not re-encoded.

Run via `mise run visuals`; commit the outputs (Cloudflare Pages only runs `zola build`).
"""
import hashlib
import json
import subprocess
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = (600, 960, 1536)
FORMATS = {"avif": 50, "webp": 78, "jpg": 80}
INCOMING = ROOT / "visuals/incoming"
OUT = ROOT / "static/visuals"
PROVENANCE = ROOT / "visuals/provenance.json"


def image_size(path):
    w, h = subprocess.run(["magick", "identify", "-format", "%w %h", str(path)],
                          check=True, capture_output=True, text=True).stdout.split()
    return int(w), int(h)


def main():
    slots = tomllib.loads((ROOT / "visuals/slots.toml").read_text())
    old = {}
    if PROVENANCE.exists():
        data = json.loads(PROVENANCE.read_text())
        for rec in data.get("images", [data] if "slot" in data else []):
            old[rec["slot"]] = rec

    OUT.mkdir(parents=True, exist_ok=True)
    catalog = {
        "captions": {"en": slots["caption"]},
        "notes": {"en": slots["note"]},
        "images": [],
    }
    records, missing = [], []
    for item in slots["images"]:
        slot = item["slot"]
        source = INCOMING / f"{slot}.png"
        if not source.exists():
            missing.append(slot)
            continue
        prompt_file = source.with_suffix(".txt")
        prompt = (prompt_file.read_text().strip() if prompt_file.exists()
                  else f"{slots['style']}\n\n{item['scene']}")
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        prev = old.get(slot)
        outputs_exist = all((OUT / f"{slot}-{w}.{e}").exists() for w in WIDTHS for e in FORMATS)
        if prev and prev.get("source_sha256") == sha and outputs_exist:
            record = prev
        else:
            record = {
                "slot": slot,
                "generated_on": prev["generated_on"] if prev and prev.get("source_sha256") == sha
                else date.today().isoformat(),
                "tool": item.get("tool", "OpenAI built-in image_gen"),
                "source": str(source.relative_to(ROOT)),
                "source_sha256": sha,
                "prompt_file": str(prompt_file.relative_to(ROOT)) if prompt_file.exists() else None,
                "prompt": prompt,
                "outputs": [],
            }
            for width in WIDTHS:
                for ext, quality in FORMATS.items():
                    out = OUT / f"{slot}-{width}.{ext}"
                    subprocess.run(["magick", str(source), "-auto-orient", "-colorspace", "sRGB",
                                    "-resize", f"{width}x>", "-strip", "-quality", str(quality),
                                    str(out)], check=True)
                    record["outputs"].append({"path": str(out.relative_to(ROOT)), "width": width,
                                              "format": ext, "quality": quality,
                                              "bytes": out.stat().st_size})
            print(f"encoded {slot}")
        records.append(record)
        width, height = image_size(source)
        catalog["images"].append({"slot": slot, "page": item["page"], "width": width,
                                  "height": height, "alt": {"en": item["alt"]}})

    (ROOT / "visuals/catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    PROVENANCE.write_text(json.dumps({"images": records}, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(records)} visuals published" + (f"; waiting for originals: {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
