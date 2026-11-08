#!/usr/bin/env python3
"""Site checks run by `mise run check` (besides `zola check`).

1. Drift against avenir. Several templates here are world copies of avenir templates (same
   markup, world URLs/texts). templates/avenir-sync.toml records, per copy, the avenir blob the
   copy was last brought in line with. When the avenir submodule moves and one of those avenir
   files changed, this fails and prints the avenir diff to port. After porting:
       python scripts/check_site.py --accept templates/page.html   (or --accept all)
   A world template that shadows an avenir template without an entry also fails, so a new copy
   cannot slip in unrecorded.

2. security.txt expiry. Fails 60 days before `Expires:` so it is renewed in time.
"""
import subprocess
import sys
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AVENIR = ROOT / "themes/avenir"
SYNC = ROOT / "templates/avenir-sync.toml"
SECURITY = ROOT / "static/.well-known/security.txt"
WARN_DAYS = 60


def git(*args):
    return subprocess.run(["git", "-C", str(AVENIR), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def blob(path):
    return git("rev-parse", f"HEAD:templates/{path}")


def load():
    return tomllib.loads(SYNC.read_text()) if SYNC.exists() else {"copies": {}}


def save(data):
    lines = [
        "# World copies of avenir templates and the avenir blob each was last synced with.",
        "# Maintained by scripts/check_site.py --accept <file|all>; see the docstring there.",
        f"# avenir HEAD at last accept: {git('rev-parse', '--short', 'HEAD')}",
        "",
        "[copies]",
    ]
    lines += [f'"{k}" = "{v}"' for k, v in sorted(data["copies"].items())]
    SYNC.write_text("\n".join(lines) + "\n")


def shadowing():
    for f in sorted((ROOT / "templates").rglob("*.html")):
        rel = f.relative_to(ROOT / "templates").as_posix()
        if (AVENIR / "templates" / rel).exists():
            yield rel


def check_drift():
    data, problems = load(), []
    for rel in shadowing():
        synced = data["copies"].get(rel)
        if synced is None:
            problems.append(f"templates/{rel} shadows avenir templates/{rel} but has no entry in "
                            f"templates/avenir-sync.toml (port it, then --accept templates/{rel})")
        elif synced != blob(rel):
            diff = subprocess.run(["git", "-C", str(AVENIR), "diff", "--shortstat", synced, blob(rel)],
                                  capture_output=True, text=True).stdout.strip()
            problems.append(f"avenir templates/{rel} changed since the world copy was synced:\n"
                            f"    {diff}\n"
                            f"    see: git -C themes/avenir diff {synced[:12]} HEAD:templates/{rel}\n"
                            f"    port to templates/{rel}, then: python scripts/check_site.py --accept templates/{rel}")
    for rel in data["copies"]:
        if not (ROOT / "templates" / rel).exists():
            problems.append(f"templates/avenir-sync.toml lists {rel}, which no longer exists here")
    return problems


def check_security_txt():
    for line in SECURITY.read_text().splitlines():
        if line.startswith("Expires:"):
            expires = datetime.fromisoformat(line.split(":", 1)[1].strip().replace("Z", "+00:00"))
            if expires - datetime.now(timezone.utc) < timedelta(days=WARN_DAYS):
                return [f"{SECURITY.relative_to(ROOT)} expires {expires.date()}: set a new Expires "
                        f"(at most a year ahead)"]
            return []
    return [f"{SECURITY.relative_to(ROOT)} has no Expires line"]


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--accept":
        data = load()
        targets = list(shadowing()) if sys.argv[2] == "all" else [sys.argv[2].removeprefix("templates/")]
        for rel in targets:
            data["copies"][rel] = blob(rel)
            print(f"accepted templates/{rel} at avenir {blob(rel)[:12]}")
        save(data)
        return 0
    problems = check_drift() + check_security_txt()
    for p in problems:
        print("✗", p)
    if not problems:
        print(f"✓ {len(load()['copies'])} avenir copies in sync, security.txt valid")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
