# roleassignments_api.py
#
# Role Assignments API — grant/filter/update/revoke object-level access for users
# and groups in Hyperproof.
# Author: Ben Roose (extension of Virgil Vaduva wrapper)
# License: GNU General Public License (GPL)
#
# Docs: https://developer.hyperproof.app/hyperproof-api/roleassignments/roleassignments.openapi

from .utils import logger


class RoleAssignmentsAPI:
    """
    Interactions with the Role Assignments API.

    Base: https://api.hyperproof.app/v1/roleassignments

    Role kinds: manager | contributor | auditor | viewer
    """

    BASE_URL = "https://api.hyperproof.app/v1/roleassignments"

    def __init__(self, api_client):
        self.client = api_client

    def add_role_assignment(
        self,
        role_kind,
        principal_id,
        principal_type,
        target_object_id,
        target_object_type,
        message=None,
        raw=False,
    ):
        """
        Adds a role assignment for a user or group on a target object
        (POST /roleassignments).

        :param role_kind: One of manager, contributor, auditor, viewer.
        :param principal_id: User or group id matching principal_type.
        :param principal_type: Principal object type (commonly ``user`` or group-related).
        :param target_object_id: Target object unique id.
        :param target_object_type: Target object type (program, control, audit, …).
        :param message: Optional notification message.
        :param raw: If True, return raw response body; otherwise parsed JSON.
        :return: Created role assignment (HTTP 201).
        :raises HyperproofAPIError: On HTTP / network failure.
        """
        data = {
            "roleKind": role_kind,
            "principalId": principal_id,
            "principalType": principal_type,
            "targetObjectId": target_object_id,
            "targetObjectType": target_object_type,
        }
        if message is not None:
            data["message"] = message
        return self.client.post(self.BASE_URL, "/", data=data, raw=raw)

    def filter_role_assignments(
        self,
        object_ids=None,
        object_type=None,
        user_ids=None,
        role_assignment_ids=None,
        direct_assignments_only=None,
        group_ids=None,
        raw=False,
    ):
        """
        Returns role assignments matching a filter (POST /roleassignments/filter).

        :param object_ids: Target object ids to filter by.
        :param object_type: Target object type filter.
        :param user_ids: Principal user ids to filter by.
        :param role_assignment_ids: Specific assignment ids to return.
        :param direct_assignments_only: If True, exclude inherited assignments.
        :param group_ids: Group ids to filter by.
        :param raw: If True, return raw response body; otherwise parsed JSON.
        :return: Matching role assignments.
        :raises HyperproofAPIError: On HTTP / network failure.
        """
        data = {}
        if object_ids is not None:
            data["objectIds"] = list(object_ids)
        if object_type is not None:
            data["objectType"] = object_type
        if user_ids is not None:
            data["userIds"] = list(user_ids)
        if role_assignment_ids is not None:
            data["roleAssignmentIds"] = list(role_assignment_ids)
        if direct_assignments_only is not None:
            data["directAssignmentsOnly"] = direct_assignments_only
        if group_ids is not None:
            data["groupIds"] = list(group_ids)
        return self.client.post(self.BASE_URL, "/filter", data=data, raw=raw)

    def update_role_assignment(self, role_assignment_id, role_kind, raw=False):
        """
        Updates an existing role assignment's role kind
        (PATCH /roleassignments/{id}).

        :param role_assignment_id: Role assignment unique id.
        :param role_kind: New role kind (manager, contributor, auditor, viewer).
        :param raw: If True, return raw response body; otherwise parsed JSON.
        :return: Updated role assignment.
        :raises HyperproofAPIError: On HTTP / network failure.
        """
        data = {"roleKind": role_kind}
        return self.client.patch(
            self.BASE_URL, f"/{role_assignment_id}", data=data, raw=raw
        )

    def delete_role_assignment(self, role_assignment_id, raw=False):
        """
        Deletes a role assignment (DELETE /roleassignments/{id}).

        :param role_assignment_id: Role assignment unique id.
        :param raw: If True, return raw response body; otherwise parsed JSON
            (empty success bodies become ``{}``).
        :return: Empty mapping on HTTP 204 success when raw=False.
        :raises HyperproofAPIError: On HTTP / network failure.
        """
        return self.client.delete(
            self.BASE_URL, f"/{role_assignment_id}", raw=raw
        )
