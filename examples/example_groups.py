# Example using Groups API helpers to list groups with membership (userIds)

import hyperproof

groups = hyperproof.get_groups(status="active", expand="userIds")
print(f"Groups: {len(groups) if isinstance(groups, list) else groups}")

# Optional: members for one group by id
# members = hyperproof.get_group_members(group_id="your-group-id")
# print(members)
