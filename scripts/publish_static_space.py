"""Publish a validated static Hugging Face Space from an already exported folder."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from huggingface_hub import HfApi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()

    if not args.repo_id.startswith("singhankit491/"):
        raise ValueError("Destination must be in the requested singhankit491 account")
    required = {"README.md", "index.html", "styles.css", "runtime.js", "app.js", "model.json", "evaluation.json"}
    missing = sorted(name for name in required if not (args.folder / name).is_file())
    if missing:
        raise FileNotFoundError(f"Static Space bundle is incomplete: {missing}")

    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN is required for publication")
    api = HfApi(token=token)
    identity = api.whoami()
    if identity["name"] != "singhankit491":
        raise ValueError("Authenticated Hugging Face account does not match requested owner")

    api.create_repo(
        repo_id=args.repo_id,
        repo_type="space",
        space_sdk="static",
        exist_ok=True,
        private=False,
    )
    commit = api.upload_folder(
        repo_id=args.repo_id,
        repo_type="space",
        folder_path=args.folder,
        commit_message="Deploy validated client-side ClinRoute ML demonstration",
    )
    info = api.space_info(args.repo_id, files_metadata=False)
    print("Published commit:", commit.commit_url)
    print("Space:", f"https://huggingface.co/spaces/{args.repo_id}")
    print("Revision:", info.sha)


if __name__ == "__main__":
    main()
