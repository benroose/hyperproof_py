# Contributing to Hyperproof Python API Wrapper (Fork)

Thanks for your interest in contributing! This repository is a maintained fork that focuses on resiliency, correctness, and developer ergonomics.

## Code of Conduct

Be respectful and constructive. Harassment and discrimination are not tolerated.

## Getting Started (Local Development)

1. Clone and create a virtual environment:
```bash
git clone https://github.com/booyasatoshi/hyperproof.git
cd hyperproof
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure credentials for integration tests/examples (local only):
```bash
echo 'CLIENT_ID="your_client_id"' >> .env
echo 'CLIENT_SECRET="your_client_secret"' >> .env
```

3. Run examples (from repo root):
```bash
PYTHONPATH=. python examples/example_users.py
```

## Development Workflow

- Branch naming: use short, descriptive names (e.g., `fix-proof-pagination`, `feat-retry-timeouts`).
- Commits: write clear messages in imperative mood. Example: "Fix retry logic for 429 responses".
- Style: prefer clear, readable, high-verbosity Python. Avoid deep nesting and inline comments.
- Tests: when modifying behavior, include runnable example updates or small test scripts where applicable.

## Pull Requests

1. Fork and create a feature branch from `main`.
2. Make focused changes with clear commit messages.
3. Update documentation if behavior or usage changes.
4. Open a PR with:
   - Problem statement and rationale
   - Summary of changes
   - Testing notes (manual steps or scripts)

PRs are reviewed for correctness, clarity, and maintainability.

## Issues

- File issues at: https://github.com/booyasatoshi/hyperproof/issues
- Include steps to reproduce, expected vs actual behavior, and environment details.

## Release and Versioning

This fork is currently source-distributed. Pin commits/SHAs as needed for production.

## Acknowledgements

This project builds upon prior community work. Thanks to the original authors for the initial foundation.
