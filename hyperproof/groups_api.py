# groups_api.py
#
# This module provides functionality for interacting with the Groups API of Hyperproof.
# Author: Ben Roose (extension of Virgil Vaduva wrapper)
# License: This project is licensed under the GNU General Public License (GPL).
#
# Description:
# The GroupsAPI class handles interactions with the Groups API, allowing for
# retrieving groups and membership, creating/updating groups, and adding/removing
# group members.
#
# Docs: https://developer.hyperproof.app/hyperproof-api/groups/groups.openapi

from .utils import logger


class GroupsAPI:
    """
    This class handles interactions with the Groups API of Hyperproof.
    Base: https://api.hyperproof.app/v1/groups
    """

    BASE_URL = "https://api.hyperproof.app/v1/groups"

    def __init__(self, api_client):
        # Use the shared API client
        self.client = api_client

    def get_groups(self, status=None, expand=None, raw=False):
        """
        Retrieves details of all groups within an organization.

        :param status: Comma-separated statuses (default active). Supported: active, archived.
        :param expand: Comma-separated fields to expand. Supported: userIds.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        """
        params = {
            "status": status,
            "expand": expand,
        }
        return self.client.get(self.BASE_URL, "/", params=params, raw=raw)

    def get_group_by_id(self, group_id, expand=None, raw=False):
        """
        Retrieves details of a specific group by its unique ID.

        :param group_id: Unique ID of the group.
        :param expand: Comma-separated fields to expand. Supported: userIds.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        """
        params = {"expand": expand}
        return self.client.get(self.BASE_URL, f"/{group_id}", params=params, raw=raw)

    def add_group(self, name, group_lead_id=None, user_ids=None, raw=False):
        """
        Creates a new group in Hyperproof.

        :param name: The name of the group (required).
        :param group_lead_id: Unique ID of the group lead (optional).
        :param user_ids: List of user IDs to add as initial members (optional).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        """
        data = {
            "name": name,
            "groupLeadId": group_lead_id,
            "userIds": user_ids or [],
        }
        return self.client.post(self.BASE_URL, "/", data=data, raw=raw)

    def update_group(
        self,
        group_id,
        name=None,
        group_lead_id=None,
        user_ids=None,
        raw=False,
    ):
        """
        Updates an existing group (name, lead, and/or membership configuration).

        :param group_id: Unique ID of the group.
        :param name: New group name (optional).
        :param group_lead_id: New group lead user ID (optional).
        :param user_ids: Replacement membership user ID list (optional; omit to leave unchanged).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        """
        data = {}
        if name is not None:
            data["name"] = name
        if group_lead_id is not None:
            data["groupLeadId"] = group_lead_id
        if user_ids is not None:
            data["userIds"] = user_ids
        return self.client.patch(self.BASE_URL, f"/{group_id}", data=data, raw=raw)

    def get_all_group_members(self, status=None, raw=False):
        """
        Retrieves membership for groups in the organization (GET /groups/users).

        :param status: Comma-separated statuses (default active). Supported: active, archived.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        """
        params = {"status": status}
        return self.client.get(self.BASE_URL, "/users", params=params, raw=raw)

    def get_group_members(self, group_id, raw=False):
        """
        Retrieves the members of a specific group (GET /groups/{groupId}/users).

        :param group_id: Unique ID of the group.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data (typically {groupId, userIds}) in the desired format.
        """
        return self.client.get(self.BASE_URL, f"/{group_id}/users", raw=raw)

    def add_group_members(self, group_id, user_ids, raw=False):
        """
        Adds one or more users to a group (POST /groups/{groupId}/users).

        :param group_id: Unique ID of the group.
        :param user_ids: List of canonical user IDs (Users API ``userId`` field —
            NOT the org-user ``id``). Passing org-user ids yields HTTP 500.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        :raises HyperproofAPIError: On HTTP / network failure from the shared client.
        """
        if isinstance(user_ids, str):
            user_ids = [user_ids]
        data = {"userIds": list(user_ids)}
        return self.client.post(self.BASE_URL, f"/{group_id}/users", data=data, raw=raw)

    def remove_group_members(self, group_id, user_ids, raw=False):
        """
        Removes one or more users from a group (PUT /groups/{groupId}/users/delete).

        :param group_id: Unique ID of the group.
        :param user_ids: List of canonical user IDs (Users API ``userId`` field —
            NOT the org-user ``id``).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data in the desired format (raw or parsed JSON).
        :raises HyperproofAPIError: On HTTP / network failure from the shared client.
        """
        if isinstance(user_ids, str):
            user_ids = [user_ids]
        data = {"userIds": list(user_ids)}
        return self.client.put(
            self.BASE_URL, f"/{group_id}/users/delete", data=data, raw=raw
        )
