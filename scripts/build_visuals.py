#!/usr/bin/env python3
"""Encode the original editorial scene with ImageMagick; preserve provenance."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'visuals/incoming/world-tomorrow.png'
    prompt = source.with_suffix('.txt')
    record = {'slot': 'world-tomorrow', 'generated_on': '2026-11-08',
              'tool': 'OpenAI built-in image_gen', 'source': str(source.relative_to(ROOT)),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'prompt_file': str(prompt.relative_to(ROOT)), 'prompt': prompt.read_text().strip(), 'outputs': []}
    for width in (600, 960, 1536):
        for ext, quality in [('avif', 50), ('webp', 78), ('jpg', 80)]:
            out = ROOT / f'static/visuals/world-tomorrow-{width}.{ext}'
            out.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['magick', str(source), '-auto-orient', '-colorspace', 'sRGB',
                            '-resize', f'{width}x>', '-strip', '-quality', str(quality), str(out)], check=True)
            record['outputs'].append({'path': str(out.relative_to(ROOT)), 'width': width,
                                      'format': ext, 'quality': quality, 'bytes': out.stat().st_size})
    (ROOT / 'visuals/provenance.json').write_text(json.dumps(record, indent=2) + '\n')

if __name__ == '__main__':
    main()
