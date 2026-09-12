"""Check local Markdown document links without fetching external websites."""

import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
missing = []
for path in [root / "README.md", *sorted((root / "docs").glob("*.md"))]:
    for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        if "://" in link or link.startswith("#"):
            continue
        target = (path.parent / link.split("#")[0]).resolve()
        if not target.exists():
            missing.append(f"{path.relative_to(root)} → {link}")
if missing:
    raise SystemExit("\n".join(missing))
print("All local Markdown links resolve.")
