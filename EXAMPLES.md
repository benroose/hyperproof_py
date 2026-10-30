# Hyperproof Python API Wrapper — Examples

This guide shows practical, runnable snippets for common Hyperproof API tasks using this wrapper.

## Prerequisites

1) Install the library from this repository (create a virtualenv recommended):
```bash
git clone https://github.com/benroose/hyperproof_PyWrapper-forked.git
cd hyperproof_PyWrapper-forked
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Configure credentials (recommended via .env):
```bash
# .env in your project root
CLIENT_ID="your_client_id"
CLIENT_SECRET="your_client_secret"
```

3) Basic usage pattern (from repo root):
```python
import hyperproof

me = hyperproof.get_current_user()
print(me)
```

## Controls

```python
import hyperproof

# Fetch all controls
controls = hyperproof.get_controls()
print(f"Controls: {len(controls)}")

# Get a control by ID
control = hyperproof.get_control_by_id(control_id="your-control-id")
print(control)
```

## Tasks

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
print(task)

# Add proof to a task
added = hyperproof.add_task_proof(
    task_id="your-task-id",
    file_path="/path/to/evidence.pdf",
    proof_owned_by="owner-id",
    proof_source="manual",
)
print(added)
```

## Proof — Core operations

```python
import hyperproof

proofs = hyperproof.get_proof_metadata_collection(limit=200, sort_by="uploadedOn", sort_direction="desc")
print(f"Fetched {len(proofs)} proofs")

# Upload a new proof
created = hyperproof.add_proof(file_path="/path/to/proof.pdf")
print(created)

# Upload a proof with ownership specified
created = hyperproof.add_proof(file_path="/path/to/proof.pdf", proof_owned_by="user-id")
print(created)

# Add a new version of an existing proof
updated = hyperproof.add_proof_version(proof_id="existing-proof-id", file_path="/path/to/new-version.pdf")
print(updated)

# Download proof contents (raw bytes/text depends on server)
contents = hyperproof.get_proof_contents(proof_id="existing-proof-id", version=2)
print(type(contents), len(contents) if contents else 0)

# Find proofs by label (partial, case-insensitive)
malware_proofs = hyperproof.get_proof_by_label(label_name="Malware")
print(f"Malware proofs: {len(malware_proofs)}")
```

## Advanced — Auto-paginating list_proof generator

```python
from hyperproof import APIClient
from hyperproof.proof_api import ProofAPI
import os

# Uses environment vars (from .env or direct env)
client = APIClient(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
proof_api = ProofAPI(client)

count = 0
for item in proof_api.list_proof(limit=100, sort_by="uploadedOn", sort_direction="desc"):
    # Process each proof item
    count += 1
print(f"Streamed {count} proof items")
```

## Labels

```python
import hyperproof

labels = hyperproof.get_labels()
print(f"Labels: {len(labels)}")

label = hyperproof.get_label_by_id(label_id="your-label-id")
print(label)
```

## Programs

```python
import hyperproof

programs = hyperproof.get_programs(status="defining")
print(f"Programs: {len(programs)}")

program = hyperproof.get_program_by_id(program_id="your-program-id")
print(program)
```

## Risks

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
print(risk)
```

## Users and Roles

```python
import hyperproof

me = hyperproof.get_current_user()
print(me)

users = hyperproof.get_organization_users(include_deactivated=False)
print(f"Users: {len(users)}")

roles = hyperproof.get_roles()
print(f"Roles: {len(roles)}")
```

## Groups

```python
import hyperproof

groups = hyperproof.get_groups(status="active", expand="userIds")
print(f"Groups: {len(groups)}")

# members = hyperproof.get_group_members(group_id="your-group-id")
# print(members)
```
## Role Assignments

```python
import hyperproof

# Filter (read-only) — find object-level assignments for a user
assignments = hyperproof.filter_role_assignments(
    user_ids=["your-userId"],
    direct_assignments_only=True,
)
print(f"Assignments: {len(assignments) if isinstance(assignments, list) else assignments}")

# Mutating examples (commented — use deliberately):
# created = hyperproof.add_role_assignment(
#     role_kind="auditor",
#     principal_id="your-userId",
#     principal_type="user",
#     target_object_id="your-program-id",
#     target_object_type="program",
# )
# hyperproof.update_role_assignment(role_assignment_id=created["id"], role_kind="viewer")
# hyperproof.delete_role_assignment(role_assignment_id=created["id"])
```
