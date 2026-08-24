# API Contract

`GET /health` reports service readiness. `POST /analyze` accepts `{ "text": "..." }` and returns route, route confidence, urgency, urgency confidence, review-required status, redacted text, entities, model version, and a disclaimer. It does not return treatment recommendations or autonomous clinical instructions.
