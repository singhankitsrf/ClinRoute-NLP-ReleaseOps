from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--output", default="artifacts/release_manifest.json")
    a = ap.parse_args()
    md = Path(a.model_dir)
    files = [
        {
            "path": p.relative_to(md).as_posix(),
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
        }
        for p in sorted(md.rglob("*"))
        if p.is_file()
    ]
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": os.getenv("GITHUB_SHA", "local"),
        "git_ref": os.getenv("GITHUB_REF_NAME", "local"),
        "model_dir": str(md),
        "model_files": files,
        "metrics": json.loads(Path(a.metrics).read_text()),
    }
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    print(out)


if __name__ == "__main__":
    main()
