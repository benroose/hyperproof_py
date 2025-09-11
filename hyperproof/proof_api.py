# proof_api.py
# 
# This module provides functionality for interacting with the Proof API of Hyperproof.
# Author: Virgil Vaduva
# Timestamp: 2024-09-25
# License: This project is licensed under the GNU General Public License (GPL).
#
# Description:
# The ProofAPI class is responsible for handling interactions with the Proof API,
# allowing for operations related to proof, such as retrieving and managing proof data.

import re
from typing import Iterator, Optional
from .utils import logger
from .users_api import UsersAPI
from .labels_api import LabelsAPI

class ProofAPI:
    """
    This class handles interactions with the Proof API of Hyperproof.
    """
    BASE_URL = "https://api.hyperproof.app/v1/proof"

    def __init__(self, api_client):
        # Use the shared API client
        self.client = api_client
        self.users_api = UsersAPI(api_client)
        self.labels_api = LabelsAPI(api_client)

    def get_proof_metadata_collection(self, limit=500, sort_by="uploadedOn", sort_direction="desc", object_type=None, object_id=None, owned_by_me=None, search=None, raw=False):
        """
        Retrieve all proof metadata for an organization, control, label, or task, with pagination support.

        :param limit: Maximum number of results to retrieve in a single call (default 500).
        :param sort_by: Field to sort results by (default is uploadedOn).
        :param sort_direction: Sort direction (asc or desc, default is desc).
        :param object_type: Filter by object type (control or label).
        :param object_id: Filter by object ID.
        :param next_token: Token for paginated results (optional, handled internally).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: List of all available proof metadata.
        """
        all_proofs = []
        offset_token = None

        while True:
            # Prepare the parameters for the API call
            params = {
                'limit': limit,
                'sortBy': sort_by,
                'sortDirection': sort_direction,
                'objectType': object_type,
                'objectId': object_id,
                'ownedByMe': owned_by_me,
                'search': search,
                'offset': offset_token
            }

            # Make the API call
            response = self.client.get(self.BASE_URL, "/", params=params, raw=False)

            # Check if the response has data and append to the result
            if not response or 'data' not in response:
                raise ValueError("No data returned from get_proof_metadata_collection.")

            all_proofs.extend(response.get('data', []))

            # Check for the offset token to determine if more data needs to be fetched
            offset_token = response.get('offsetToken', None)

            # If no nextToken is returned, we have retrieved all data
            if not offset_token:
                break

        # Return all accumulated proofs
        if raw:
            return all_proofs

        return all_proofs


    def get_proof_metadata(self, proof_id, raw=False):
        """
        Retrieve specific proof metadata by proof ID.

        :param proof_id: The unique ID of the proof.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data of the proof metadata.
        """
        return self.client.get(self.BASE_URL, f"/{proof_id}", raw=raw)

    def add_proof(self, file_path, raw=False):
        """
        Upload a new proof file to the organization.

        :param file_path: Path to the proof file to upload.
        :param object_id: The object ID the proof is related to (optional).
        :param object_type: The object type (control or label, optional).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data of the newly added proof.
        """
        with open(file_path, 'rb') as file:
            files = {'proof': file}
            return self.client.post(self.BASE_URL, "/", files=files, data=None, raw=raw)

    def add_proof_version(self, proof_id, file_path, raw=False):
        """
        Add a new version of an existing proof by proof ID.

        :param proof_id: The ID of the proof to update.
        :param file_path: Path to the new version of the proof file.
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: Response data of the updated proof.
        """
        with open(file_path, 'rb') as file:
            files = {'proof': file}
            return self.client.post(self.BASE_URL, f"/{proof_id}/versions", files=files, raw=raw)

    def get_proof_contents(self, proof_id, version=None, raw=False):
        """
        Retrieve the contents of a proof as a file.

        :param proof_id: The ID of the proof to retrieve.
        :param version: The version of the proof to retrieve (optional).
        :param raw: If True, return raw response.
        :return: The contents of the proof file.
        """
        params = {}
        if version:
            params['version'] = version
        return self.client.get(self.BASE_URL, f"/{proof_id}/contents", params=params, raw=raw)

    def get_proof_by_user(self, userid=None, givenName=None, surname=None, object_type=None, object_id=None, raw=False):
        """
        Retrieve proofs associated with a user based on userid, givenName, surname, object_type, and object_id.
        Handles large data sets by using pagination.

        :param userid: The unique identifier of the user (optional).
        :param givenName: The given name of the user (optional).
        :param surname: The surname of the user (optional).
        :param object_type: The object type to filter by (e.g., 'control' or 'label', optional).
        :param object_id: The object ID to filter by (optional).
        :param raw: If True, return raw response; otherwise return parsed JSON.
        :return: List of proofs associated with the specified user(s) and object_type or object_id.
        """
        # Get all organization users
        org_users = self.users_api.get_organization_users(raw=False)

        if raw:
            return org_users

        # Filter users based on userid, givenName, and surname
        filtered_users = []
        for user in org_users:
            if userid and (user.get('id') == userid or user.get('userId') == userid):
                filtered_users.append(user)
            elif givenName and surname:
                if user.get('givenName') == givenName and user.get('surname') == surname:
                    filtered_users.append(user)
            elif givenName and user.get('givenName') == givenName:
                filtered_users.append(user)
            elif surname and user.get('surname') == surname:
                filtered_users.append(user)

        if not filtered_users:
            return []

        # Fetch proofs with optional object_type and object_id filtering
        limit = 500
        offset_token = None
        all_proofs = []

        while True:
            # Prepare the parameters for fetching proofs
            params = {
                'limit': limit,
                'sortBy': 'createdBy',
                'sortDirection': 'desc',
                'objectType': object_type,
                'objectId': object_id,
                'offset': offset_token
            }

            all_proofs_response = self.client.get(self.BASE_URL, '/', params=params, raw=False)

            if not all_proofs_response or 'data' not in all_proofs_response:
                raise ValueError("No data returned from get_proof_metadata_collection.")

            # Extend the list with data from the current response
            all_proofs.extend(all_proofs_response.get('data', []))

            # Check for offsetToken to determine if more results exist
            offset_token = all_proofs_response.get('offsetToken', None)

            # If no continuationToken is returned, all results have been fetched
            if not offset_token:
                break

        # Filter the returned proofs based on the createdBy field matching the filtered users
        user_proofs = []
        for proof in all_proofs:
            if isinstance(proof, dict):
                created_by = proof.get('createdBy', None)

                # Match the 'createdBy' field with the filtered users
                for user in filtered_users:
                    if created_by == user.get('id') or created_by == user.get('userId'):
                        user_proofs.append(proof)
            else:
                print(f"Unexpected type for proof: {type(proof)}")

        return user_proofs

    def get_proof_by_label(self, label_name, limit=500, sort_by="uploadedOn", sort_direction="desc", raw=False):
        """
        Retrieve proofs associated with a specific label by label name (partial, case-insensitive match).
        
        :param label_name: The name of the label to search for (partial, case-insensitive match).
        :param limit: Maximum number of results to retrieve in a single call (default 500).
        :param sort_by: Field to sort results by (default is uploadedOn).
        :param sort_direction: Sort direction (asc or desc, default is desc).
        :param raw: If True, return raw response text; otherwise return parsed JSON.
        :return: List of proofs associated with the specified label.
        """
        # Get label summaries and perform a case-insensitive partial match on the given name
        label_summaries = self.labels_api.get_label_summaries(raw=False)

        # Perform case-insensitive partial match on label name
        matching_label = next((label for label in label_summaries if re.search(label_name, label.get('name', ''), re.IGNORECASE)), None)

        if not matching_label:
            raise ValueError(f"No label found with the name: {label_name}")

        label_id = matching_label.get('id')

        # Fetch proofs associated with the label using its ID
        all_proofs = []
        offset_token = None

        while True:
            # Prepare parameters for fetching proofs
            params = {
                'limit': limit,
                'sortBy': sort_by,
                'sortDirection': sort_direction,
                'objectType': 'label',
                'objectId': label_id,
                'offset': offset_token
            }

            # Make the API request and handle errors via the core _handle_response method
            response = self.client.get(self.BASE_URL, "/", params=params, raw=False)
            
            if response is None:
                # Handle the case where the user doesn't have permission (403)
                raise PermissionError(f"Access to the label '{label_name}' is forbidden. Please ensure you have joined the label.")
            
            if 'data' not in response:
                raise ValueError("No data returned from get_proof_metadata_collection.")

            all_proofs.extend(response.get('data', []))

            # Check for offsetToken to fetch more data if available
            offset_token = response.get('offsetToken', None)
            if not offset_token:
                break

        return all_proofs if not raw else response

    def list_proof(
        self,
        limit: int = 50,
        owned_by_me: bool = False,
        search: Optional[str] = None,
        sort_by: str = 'createdOn',
        sort_direction: str = 'desc',
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> Iterator[dict]:
        """
        Stream (yield) proof items across all pages using the Hyperproof proof listing API.

        This high-level method abstracts pagination, sorting, and filtering to provide
        an easy-to-use generator over all available proof that match the provided criteria.

        Parameters
        ----------
        limit : int, optional
            Maximum number of items per API page (default 50). Must be >= 1.
        owned_by_me : bool, optional
            If True, only return proof owned by the authenticated user (default False).
        search : str, optional
            Case-insensitive substring filter applied to the proof filename.
        sort_by : str, optional
            Field used to sort results; one of: 'createdBy', 'createdOn', 'filename', 'uploadedOn'.
            Defaults to 'createdOn'.
        sort_direction : str, optional
            Sort order direction; either 'asc' or 'desc'. Defaults to 'desc'.
        object_type : str, optional
            If provided, filters proof linked to the given object type ('control', 'label', or 'task').
        object_id : str, optional
            If provided with object_type, filters proof linked to the specified object id.

        Yields
        ------
        dict
            A single proof item (JSON object) per iteration.

        Notes
        -----
        - This method automatically follows pagination using the 'offsetToken' pattern from Hyperproof.
        - It issues repeated GET requests to `/v1/proof` until no further `offsetToken` is returned.
        - Invalid `sort_by` and `sort_direction` values are not coerced here and should follow
          Hyperproof API constraints; provide valid values to avoid API errors.
        """
        # Defensive clamp for per-page size
        page_size = max(1, int(limit))

        # Pagination state
        offset_token: Optional[str] = None

        while True:
            params = {
                'limit': page_size,
                'sortBy': sort_by,
                'sortDirection': sort_direction,
                'ownedByMe': owned_by_me or None,  # omit if False
                'search': search,
                'objectType': object_type,
                'objectId': object_id,
                'offset': offset_token
            }

            response = self.client.get(self.BASE_URL, '/', params=params, raw=False)

            if not response:
                break

            data = response.get('data') if isinstance(response, dict) else None
            if not isinstance(data, list):
                break

            for item in data:
                # Each item is expected to be a dict representing a proof record
                yield item

            offset_token = response.get('offsetToken') if isinstance(response, dict) else None
            if not offset_token:
                break
