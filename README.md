# Hyperproof Python API Wrapper

A robust, production-ready Python wrapper for the Hyperproof API. This library provides a clean, Pythonic interface over Hyperproof’s Governance, Risk, and Compliance (GRC) APIs and includes convenience helpers, resiliency, and best-practice defaults.

- Project homepage: `https://developer.hyperproof.app/apis`
- License: GNU General Public License (GPL)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Controls](#controls)
  - [Tasks](#tasks)
  - [Proof](#proof)
  - [Labels](#labels)
  - [Programs](#programs)
  - [Risks](#risks)
  - [Users and Roles](#users-and-roles)
- [Advanced Usage](#advanced-usage)
  - [Auto-paginating list_proof generator](#auto-paginating-list_proof-generator)
- [API Coverage](#api-coverage)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Features

- **OAuth2 authentication with automatic refresh**: The client transparently refreshes the token on 401 responses and replays the request.
- **Resiliency by default**: Network requests include sensible default timeouts and automatic retries with exponential backoff for 429 and 5xx responses.
- **Correct, reliable pagination**: All collection methods use Hyperproof’s `offset`/`offsetToken` model. A high-level generator abstracts pagination for proofs.
- **Fixed multipart uploads**: File uploads now use the correct multipart field name `proof` and support additional metadata when required.
- **Lazy, shared client**: A single `APIClient` instance is shared across all API classes for efficiency.
- **Pythonic convenience functions**: Import top-level helpers like `get_controls`, `add_task_proof`, `get_proof_by_label`, etc., or use the specific APIs directly.

## Installation

Install from PyPI:

```bash
pip install hyperproof
```

From source:

```bash
git clone https://github.com/booyasatoshi/hyperproof.git
cd hyperproof
pip install -r requirements.txt
```

## Configuration

Use a `.env` file for credentials (recommended). Create a `.env` in your project root with:

```bash
CLIENT_ID="your_client_id"
CLIENT_SECRET="your_client_secret"
```

The package loads these automatically via `python-dotenv` in `hyperproof/__init__.py`. For production, consider a secure secret store; environment variables are also supported.

## Quick Start

Import the top-level functions and call any supported API directly:

```python
import hyperproof

# Fetch current user
me = hyperproof.get_current_user()

# List controls
controls = hyperproof.get_controls()

# Upload a proof file (organization-level)
result = hyperproof.add_proof(file_path="/path/to/proof.pdf")
```

You can also import specific helpers:

```python
from hyperproof import get_proof_by_label

proofs = get_proof_by_label(label_name="Malware")
```

## Usage Examples

### Controls

```python
import hyperproof

# Fetch all controls
controls = hyperproof.get_controls()

# Fetch a control by ID
control = hyperproof.get_control_by_id(control_id="your-control-id")
```

### Tasks

```python
import hyperproof

# Create a task
task = hyperproof.add_task(
    title="Collect quarterly evidence",
    target_object={"objectId": "target-id", "objectType": "domain"},
    description="Gather Q3 evidence for the SOC2 program",
    assignee_id="user-id",
    priority="high",
    due_date="2025-10-01T00:00:00Z"
)

# Add proof to a task
added = hyperproof.add_task_proof(
    task_id="your-task-id",
    file_path="/path/to/evidence.pdf",
    proof_owned_by="owner-id",
    proof_source="manual",
)
```

### Proof

```python
import hyperproof

# Get proof metadata collection (handles pagination using offset/offsetToken)
proofs = hyperproof.get_proof_metadata_collection(limit=200, sort_by="uploadedOn", sort_direction="desc")

# Upload a new proof (multipart uses the correct field name `proof`)
created = hyperproof.add_proof(file_path="/path/to/proof.pdf")

# Upload a new version of an existing proof
updated = hyperproof.add_proof_version(proof_id="existing-proof-id", file_path="/path/to/new-version.pdf")

# Download proof contents
contents = hyperproof.get_proof_contents(proof_id="existing-proof-id", version=2)

# Find proofs attached to a label by partial, case-insensitive name match
malware_proofs = hyperproof.get_proof_by_label(label_name="Malware")
```

### Labels

```python
import hyperproof

labels = hyperproof.get_labels()
label = hyperproof.get_label_by_id(label_id="your-label-id")
```

### Programs

```python
import hyperproof

programs = hyperproof.get_programs(status="defining")
program = hyperproof.get_program_by_id(program_id="your-program-id")
```

### Risks

```python
import hyperproof

risk = hyperproof.add_risk(
    risk_register_id="register-id",
    risk_identifier="RISK-001",
    name="Data Breach Risk",
    description="Potential for a data breach to occur",
    category="Security",
    response="mitigate",
    likelihood_level=5,
    likelihood_rationale="Historical incidents suggest elevated likelihood",
    impact_level=4,
    impact_rationale="Severe impact on data and reputation",
    tolerance_level=3,
    owner_id="owner-id"
)
```

### Users and Roles

```python
import hyperproof

me = hyperproof.get_current_user()
users = hyperproof.get_organization_users(include_deactivated=False)
roles = hyperproof.get_roles()
```

## Advanced Usage

### Auto-paginating list_proof generator

For efficient iteration over all proofs without manual pagination, use the high-level generator on `ProofAPI`. When using top-level imports, first access the underlying API instance via `hyperproof._proof_api.instance` or instantiate your own `ProofAPI` with the shared client if you need direct API access.

Recommended best practice:

```python
# Best: instantiate ProofAPI with the shared client from the package
from hyperproof import APIClient
from hyperproof.proof_api import ProofAPI
import os

client = APIClient(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
proof_api = ProofAPI(client)

# Stream proof records across all pages
for item in proof_api.list_proof(limit=100, sort_by="uploadedOn", sort_direction="desc"):
    # process each proof item
    pass
```

Notes:
- The generator follows Hyperproof’s `offset`/`offsetToken` pagination automatically until exhaustion.
- Supports optional filters: `owned_by_me`, `search`, `object_type` and `object_id`.
- Use this over manual pagination when processing large result sets.

## API Coverage

This wrapper provides a 1:1 mapping for the following APIs plus convenience methods:

- Controls API: `get_controls`, `get_control_by_id`, `add_control`, `update_control`, `get_control_summaries`, `add_control_proof`, `get_controls_by_user`
- Proof API: `get_proof_metadata_collection`, `get_proof_metadata`, `get_proof_contents`, `add_proof`, `add_proof_version`, `get_proof_by_user`, `get_proof_by_label`, and the `ProofAPI.list_proof` generator
- Labels API: `get_labels`, `get_label_by_id`, `get_label_summaries`, `add_label`, `update_label`, `get_labels_by_user`
- Programs API: `get_programs`, `get_program_by_id`, `add_program`, `update_program`
- Risks API: `get_risks`, `get_risk_by_id`, `add_risk`, `update_risk`, `filter_risks`, `get_risks_by_user`
- Tasks API: `add_task`, `get_task_by_id`, `update_task`, `filter_tasks`, `add_task_comment`, `update_task_comment`, `delete_task_comment`, `add_task_proof`, `get_task_proof_metadata`, plus helpers `get_all_tasks`, `get_all_tasks_by_status`, `get_tasks_by_user`
- Roles API: `get_roles`
- Users API: `get_current_user`, `get_organization_users`

## Security

- Credentials: Use a secret manager or environment variables; `.env` is for local dev only. Rotate secrets regularly and grant least privilege.
- Logging: This library avoids logging auth secrets; do not enable debug logging in production. Configure your app logger (the library uses a NullHandler by default).
- Transport: All requests use HTTPS with TLS verification (via `requests`).
- Resiliency: Built-in timeouts and limited retries with jitter. Monitor and alert on repeated 429/5xx.

See `SECURITY.md` for detailed guidance.

## Contributing

Contributions are welcome! Please open an issue or submit a PR with clear descriptions and tests where applicable.

## License

GPL - GNU General Public License.

This project is licensed under the GNU General Public License (GPL). Any modifications or derivative works must also be licensed under the GPL and include the source code.