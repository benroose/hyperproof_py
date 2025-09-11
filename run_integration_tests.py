import os
import sys
import json
from dotenv import load_dotenv, find_dotenv

# Import from refactored wrapper modules (avoid side-effects in hyperproof.__init__)
from hyperproof.utils import APIClient
from hyperproof.controls_api import ControlsAPI


def print_result(test_name: str, passed: bool, details: str = "") -> None:
    prefix = "PASS" if passed else "FAIL"
    if details:
        print(f"{prefix} - {test_name}: {details}")
    else:
        print(f"{prefix} - {test_name}")


def load_credentials():
    load_dotenv(find_dotenv())
    # Prefer HYPERPROOF_* names, fallback to CLIENT_ID/CLIENT_SECRET if provided
    client_id = os.getenv("HYPERPROOF_CLIENT_ID") or os.getenv("CLIENT_ID")
    client_secret = os.getenv("HYPERPROOF_CLIENT_SECRET") or os.getenv("CLIENT_SECRET")
    if not client_id or not client_secret:
        print_result(
            "Setup",
            False,
            "Missing credentials. Set HYPERPROOF_CLIENT_ID and HYPERPROOF_CLIENT_SECRET in .env",
        )
        sys.exit(1)
    return client_id, client_secret


def test_authentication(client: APIClient) -> None:
    test_name = "Authentication"
    try:
        # Force re-authentication to validate
        client.access_token = None
        client._authenticate()
        if client.access_token:
            print_result(test_name, True, "Retrieved access token")
        else:
            print_result(test_name, False, "No access token returned")
    except Exception as e:
        print_result(test_name, False, f"Exception: {e}")


def test_file_upload(client: APIClient, control_id: str) -> None:
    test_name = "File Upload (proof field)"
    if not control_id or control_id.strip() in ("", "REPLACE_ME"):
        print_result(test_name, False, "Missing TEST_CONTROL_ID. Set HYPERPROOF_TEST_CONTROL_ID in .env")
        return

    try:
        # Create a small dummy file
        filename = "test_proof.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("This is a test proof file for integration testing.\n")

        controls_api = ControlsAPI(client)
        response_json = controls_api.add_control_proof(control_id=control_id, file_path=filename, raw=False)

        # Clean up local file
        try:
            os.remove(filename)
        except Exception:
            pass

        if isinstance(response_json, dict) and response_json.get("id"):
            print_result(test_name, True, f"Uploaded proof id={response_json.get('id')}")
        elif response_json:
            print_result(test_name, True, "Upload returned a response")
        else:
            print_result(test_name, False, "Upload returned no data (None)")
    except Exception as e:
        print_result(test_name, False, f"Exception: {e}")


def test_pagination(client: APIClient) -> None:
    test_name = "Pagination (offset/offsetToken)"
    try:
        base_url = "https://api.hyperproof.app/v1/proof"

        # Page 1 with a very small limit
        page1 = client.get(base_url, "/", params={"limit": 2}, raw=False)
        if not page1 or not isinstance(page1, dict):
            print_result(test_name, False, "First page request failed or returned no data")
            return

        data1 = page1.get("data", [])
        offset_token = page1.get("offsetToken")

        if len(data1) >= 2:
            # Expect another page if there are at least 'limit' items
            if not offset_token:
                print_result(test_name, False, "Expected offsetToken but none was returned")
                return

            page2 = client.get(base_url, "/", params={"limit": 2, "offset": offset_token}, raw=False)
            if not page2 or not isinstance(page2, dict):
                print_result(test_name, False, "Second page request failed or returned no data")
                return

            print_result(test_name, True, "Successfully retrieved second page using offsetToken")
        else:
            # Only one page exists; treat as pass
            print_result(test_name, True, "Only one page of results (no offsetToken expected)")
    except Exception as e:
        print_result(test_name, False, f"Exception: {e}")


def main():
    client_id, client_secret = load_credentials()
    client = APIClient(client_id, client_secret)

    # Test 1: Authentication
    test_authentication(client)

    # Test 2: File upload (control proof)
    test_control_id = os.getenv("HYPERPROOF_TEST_CONTROL_ID", "REPLACE_ME")
    test_file_upload(client, test_control_id)

    # Test 3: Pagination using Proof API (GET /v1/proof)
    test_pagination(client)


if __name__ == "__main__":
    main()

