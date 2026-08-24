# CI/CD Design

Pull requests run Python compatibility, generated synthetic data-contract validation, Ruff, mypy, pytest, NLP smoke tests, Bandit, CodeQL, and a reproducible baseline training smoke job. A separate model-regression gate compares macro-F1 and ECE against an approved baseline. Semantic version tags publish versioned and commit-SHA container tags to GHCR.
