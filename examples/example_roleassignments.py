# Example: filter role assignments (read-only). Mutating calls are commented out.

import hyperproof

# Replace with a real Users API userId (canonical userId field, not org-user id)
USER_ID = "your-userId"

assignments = hyperproof.filter_role_assignments(
    user_ids=[USER_ID],
    direct_assignments_only=True,
)
print(
    f"Assignments: {len(assignments) if isinstance(assignments, list) else assignments}"
)

# Mutating examples — uncomment only when intentional:
# created = hyperproof.add_role_assignment(
#     role_kind="auditor",
#     principal_id=USER_ID,
#     principal_type="user",
#     target_object_id="your-program-id",
#     target_object_type="program",
# )
# print(created)
# hyperproof.update_role_assignment(role_assignment_id=created["id"], role_kind="viewer")
# hyperproof.delete_role_assignment(role_assignment_id=created["id"])
