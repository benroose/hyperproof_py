# Hyperproof Python API Wrapper

A robust, production-ready Python wrapper for the Hyperproof API. This library provides a clean, Pythonic interface over Hyperproof’s Governance, Risk, and Compliance (GRC) APIs and includes convenience helpers, resiliency, and best-practice defaults.

- Project homepage: `https://developer.hyperproof.app/apis`
- License: GNU General Public License (GPL)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Command Line Interface (CLI)](#command-line-interface-cli)
- [Usage Examples](#usage-examples)
  - [Controls](#controls)
  - [Tasks](#tasks)
  - [Proof](#proof)
  - [Labels](#labels)
  - [Programs](#programs)
  - [Risks](#risks)
  - [Users and Roles](#users-and-roles)
  - [Groups](#groups)
  - [Role Assignments](#role-assignments)
- [Advanced Usage](#advanced-usage)
  - [Auto-paginating list_proof generator](#auto-paginating-list_proof-generator)
- [API Coverage](#api-coverage)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Project origin and maintenance](#project-origin-and-maintenance)

## Features

- **OAuth2 authentication with automatic refresh**: The client transparently refreshes the token on 401 responses and replays the request.
- **Resiliency by default**: Network requests include sensible default timeouts and automatic retries with exponential backoff for 429 and 5xx responses.
- **Explicit API errors**: Failed requests raise `HyperproofAPIError` (with `status_code`, response body, method, and URL) instead of returning `None`.
- **Correct, reliable pagination**: All collection methods use Hyperproof’s `offset`/`offsetToken` model. A high-level generator abstracts pagination for proofs.
- **Fixed multipart uploads**: File uploads now use the correct multipart field name `proof` and support additional metadata when required.
- **Lazy, shared client**: A single `APIClient` instance is shared across all API classes for efficiency.
- **Pythonic convenience functions**: Import top-level helpers like `get_controls`, `add_task_proof`, `get_proof_by_label`, etc., or use the specific APIs directly.

## Installation

This fork is currently distributed from GitHub (not PyPI).

From source:

```bash
git clone https://github.com/benroose/hyperproof_PyWrapper-forked.git
cd hyperproof_PyWrapper-forked
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Notes:
- Use the library from within the repository (or add the repository root to `PYTHONPATH`).
- To run examples directly, prefix commands with `PYTHONPATH=.` from the repo root.

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

## Command Line Interface (CLI)

A new command-line tool `hp-cli` is available for interacting with the Hyperproof API from the terminal.

**The CLI tool is available as a separate repository.** See the [hp-cli repository](https://github.com/your-org/hp-cli) for installation and usage instructions.

### Quick CLI Examples

```bash
# Get current user
hp-cli users me

# List all controls
hp-cli controls list

# Upload a proof file
hp-cli proof upload /path/to/file.pdf

# List proofs by label (shows uploaded date and owner)
hp-cli proof by-label "Security"
```

For complete CLI documentation and installation instructions, see the [hp-cli repository](https://github.com/your-org/hp-cli).

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

# Upload a proof with ownership specified
created = hyperproof.add_proof(file_path="/path/to/proof.pdf", proof_owned_by="user-id")

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

### Groups

```python
import hyperproof
from hyperproof import HyperproofAPIError

# List active groups including membership user IDs
groups = hyperproof.get_groups(status="active", expand="userIds")

# Members of one group
# members = hyperproof.get_group_members(group_id="…")

# Add / remove members (mutates Hyperproof — use deliberately).
# Pass Users API ``userId`` values (not org-user ``id``).
try:
    hyperproof.add_group_members(group_id="…", user_ids=["…userId…"])
except HyperproofAPIError as err:
    print(err.status_code, err.response_text)
```

### Role Assignments

Object-level access (manager / contributor / auditor / viewer) for users or groups:

```python
import hyperproof
from hyperproof import HyperproofAPIError

# Find assignments for a user (read-only filter)
assignments = hyperproof.filter_role_assignments(
    user_ids=["…userId…"],
    direct_assignments_only=True,
)

# Grant / update / revoke (mutates Hyperproof — use deliberately)
# hyperproof.add_role_assignment(
#     role_kind="auditor",
#     principal_id="…userId…",
#     principal_type="user",
#     target_object_id="…program-or-object-id…",
#     target_object_type="program",
# )
# hyperproof.update_role_assignment(role_assignment_id="…", role_kind="viewer")
# hyperproof.delete_role_assignment(role_assignment_id="…")
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
- Groups API: `get_groups`, `get_group_by_id`, `add_group`, `update_group`, `get_all_group_members`, `get_group_members`, `add_group_members`, `remove_group_members`
- Role Assignments API: `add_role_assignment`, `filter_role_assignments`, `update_role_assignment`, `delete_role_assignment`

## Security

- Credentials: Use a secret manager or environment variables; `.env` is for local dev only. Rotate secrets regularly and grant least privilege.
- Logging: This library avoids logging auth secrets; do not enable debug logging in production. Configure your app logger (the library uses a NullHandler by default).
- Transport: All requests use HTTPS with TLS verification (via `requests`).
- Resiliency: Built-in timeouts and limited retries with jitter. Monitor and alert on repeated 429/5xx.

See `SECURITY.md` for detailed guidance.

## Contributing

Contributions are welcome! Please open an issue or submit a PR with clear descriptions and tests where applicable.

- Issues: https://github.com/benroose/hyperproof_PyWrapper-forked/issues
- Pull Requests: https://github.com/benroose/hyperproof_PyWrapper-forked/pulls

## License

GPL - GNU General Public License.

This project is licensed under the GNU General Public License (GPL). Any modifications or derivative works must also be licensed under the GPL and include the source code.

## Project origin and maintenance

**This repository is the active source of truth** for ongoing Hyperproof Python wrapper work
([benroose/hyperproof_PyWrapper-forked](https://github.com/benroose/hyperproof_PyWrapper-forked)).
Development happens on this fork’s `master` branch. We are **not syncing from or contributing
back to** [booyasatoshi/hyperproof](https://github.com/booyasatoshi/hyperproof) as an upstream
project — that repository appears inactive, and this fork is maintained independently.

**Credit:** The original foundation was created by **Virgil Vaduva**
([booyasatoshi/hyperproof](https://github.com/booyasatoshi/hyperproof)). Thank you for the
initial wrapper that made this work possible. This fork extends that foundation with Groups,
Role Assignments, explicit `HyperproofAPIError` handling, and other production-focused
improvements.

For local git history reference only, the original repo may be configured as a read-only
`upstream` remote (fetch allowed; do not push):

```bash
git remote add upstream https://github.com/booyasatoshi/hyperproof.git
git remote set-url --push upstream no_push
```
