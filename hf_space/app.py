"""CPU NLP application using the repository's trained baseline and service."""

from __future__ import annotations
import json
from pathlib import Path
import gradio as gr
from clinroute.baseline import BaselineBundle
from clinroute.service import NLPService

ROOT = Path(__file__).resolve().parents[1]
SERVICE = NLPService(BaselineBundle.load(ROOT / "models/baseline"))


def analyze(text):
    if not text or not text.strip():
        raise gr.Error("Enter a synthetic referral or select an example.")
    if len(text) > 5000:
        raise gr.Error("Use at most 5,000 characters.")
    result = SERVICE.analyze(text)
    return result["route"].replace("_", " ").title(), result["urgency"].title(), result


def report():
    candidate = ROOT / "evaluation/candidate_metrics.json"
    return json.loads(
        (candidate if candidate.exists() else ROOT / "evaluation/baseline_metrics.json").read_text()
    )


with gr.Blocks(title="ClinRoute | Ankit Kumar Singh", delete_cache=(3600, 3600)) as demo:
    gr.Markdown(
        "# ClinRoute NLP\n### Referral routing · confidence review · reproducible evaluation\nBuilt by **Ankit Kumar Singh** · [GitHub source](https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps)"
    )
    gr.Markdown(
        "**Synthetic demonstration.** Use fictional text only. This baseline recognizes patterns in templated referrals; it is not clinically validated. Inputs are processed in memory and are not saved by application code."
    )
    with gr.Tab("Try a referral"):
        note = gr.Textbox(
            label="Synthetic referral",
            lines=5,
            placeholder="Select an example below or enter fictional referral text.",
        )
        gr.Examples(
            examples=[
                [
                    "ENT referral for ear pain for 1 week. Finding: inflamed tympanic membrane. urgent assessment is requested."
                ],
                [
                    "ENT referral for gradual hearing loss for 3 months. Finding: failed hearing screen. routine specialist review is requested."
                ],
                [
                    "ENT referral for nasal obstruction for 2 weeks. Finding: nasal polyp. earlier specialist review is requested."
                ],
            ],
            inputs=note,
        )
        button = gr.Button("Analyze referral", variant="primary")
        with gr.Row():
            route = gr.Textbox(label="Predicted service", interactive=False)
            urgency = gr.Textbox(label="Stated urgency classification", interactive=False)
        details = gr.JSON(label="Confidence, extracted entities and review decision")
        button.click(analyze, note, [route, urgency, details], api_name="analyze")
    with gr.Tab("Evaluation evidence"):
        gr.Markdown(
            "The seeded benchmark redacts identifiers and removes identical normalized notes **before** its 80/20 split. Saved predictions and a hashed split manifest make the reported metrics auditable. High synthetic accuracy is expected because templates share vocabulary and urgency is stated explicitly."
        )
        gr.JSON(report(), label="Measured benchmark")
        gr.Markdown(
            "[Inspect evaluation files](https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps/tree/main/evaluation)"
        )
    with gr.Tab("Engineering decisions"):
        gr.Markdown(
            "**Runtime:** TF-IDF + logistic regression on CPU. The dual-head Transformer remains an optional training path.\n\n**Release control:** train a candidate, compare F1 and calibration against the versioned baseline, publish the same validated model artifacts.\n\n**Limits:** no clinical generalization claim; confidence thresholds are engineering examples; identifier redaction is best-effort."
        )


if __name__ == "__main__":
    demo.queue(max_size=20, default_concurrency_limit=2).launch(
        server_name="0.0.0.0", server_port=7860, share=False, show_error=False, max_file_size="10mb"
    )
