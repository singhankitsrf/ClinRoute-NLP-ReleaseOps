# ClinRoute NLP on Hugging Face

Target Space: `singhankit491/clinroute-nlp` (a deployment target, not a claim that it is live).

## Run locally

From the repository root:

```bash
pip install -r hf_space/requirements.txt
PYTHONPATH=.:src python hf_space/app.py
```


First run the synthetic generator and training/train_baseline.py. Docker performs this automatically and checks the regression gate.


## Build the exact deployment

```bash
pip install huggingface_hub==1.30.0
python scripts/publish_space.py --repo-id singhankit491/clinroute-nlp --stage-only /tmp/clinroute-nlp-space
docker build -t clinroute-nlp /tmp/clinroute-nlp-space
docker run --rm -p 7860:7860 clinroute-nlp
```

The staging command copies only tracked allowlisted source files. Commit intended changes first.
Patient data, local credentials and trained checkpoints are excluded.

## Publish

Authenticate securely with `hf auth login`, then run:

```bash
python scripts/publish_space.py --repo-id singhankit491/clinroute-nlp
```

Alternatively, configure a narrowly scoped Hugging Face write token as the GitHub Actions secret
`HF_TOKEN` and run the **Hugging Face Space** workflow. It builds and checks application startup before uploading.
No token belongs in source code, a README, a Docker build argument, or a chat message.
The workflow uses default CPU Space hardware and does not request paid GPU resources.

After publishing, wait for the Hugging Face build to finish, open the application, execute its example,
and verify the displayed output. Record the Space commit and the GitHub source revision.
The upload script reports current runtime state but does not mistake BUILDING for RUNNING.

## Scope

Synthetic referral routing with reproducible model evaluation. The AWS/Azure infrastructure remains in GitHub and requires its own account deployment.
This CPU demonstration is not evidence of clinical validation or a measured production cloud deployment.
