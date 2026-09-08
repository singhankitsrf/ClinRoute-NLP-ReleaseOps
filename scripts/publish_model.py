"""Publish only the locally evaluated synthetic baseline to the requested HF account."""

from pathlib import Path
import json
import hashlib
import os
import shutil
import tempfile
from huggingface_hub import HfApi
from scripts.model_regression_gate import gate


def main():
    root = Path(__file__).resolve().parents[1]
    candidate = json.loads((root / "evaluation/candidate_metrics.json").read_text())
    baseline = json.loads((root / "evaluation/baseline_metrics.json").read_text())
    failures = gate(candidate, baseline)
    if failures:
        raise RuntimeError(failures)
    for name, expected in candidate["model_sha256"].items():
        if name not in {"route.joblib", "urgency.joblib", "VERSION"}:
            raise ValueError("Unexpected model artifact")
        actual = hashlib.sha256((root / "models/baseline" / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Weights changed since evaluation")
    api = HfApi(token=os.getenv("HF_TOKEN"))
    if api.whoami()["name"] != "singhankit491":
        raise ValueError("Wrong Hugging Face account")
    repo_id = "singhankit491/clinroute-synthetic-baseline"
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for name in ("route.joblib", "urgency.joblib", "VERSION"):
            shutil.copyfile(root / "models/baseline" / name, folder / name)
        shutil.copyfile(root / "docs/MODEL_CARD.md", folder / "README.md")
        shutil.copyfile(root / "evaluation/candidate_metrics.json", folder / "evaluation.json")
        shutil.copyfile(root / "hf_space/requirements.txt", folder / "requirements.txt")
        api.create_repo(repo_id, exist_ok=True, private=False)
        print(
            api.upload_folder(
                repo_id=repo_id,
                folder_path=tmp,
                commit_message="Publish evaluated synthetic baseline",
            ).commit_url
        )


if __name__ == "__main__":
    main()
