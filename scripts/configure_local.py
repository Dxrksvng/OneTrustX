import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    print("Existing .env preserved.")
else:
    template = (root / ".env.example").read_text()
    path.write_text(
        template.replace("replace-with-local-password", secrets.token_hex(18))
    )
    path.chmod(0o600)
    print("Created ignored .env with a generated local database password.")
