import json
import base64
import requests
import os
import time

bearer: None | str = None

session = requests.Session()


def load_auth_details() -> dict | None:
    try:
        with open("auth.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def atob(x: str) -> str:
    """Python implementation of Javascript atob() function"""
    return base64.b64decode(x)


def btoa(x: str) -> str:
    """Python implementation of Javascript btoa() function"""
    return base64.b64encode(bytes(x, "utf-8")).decode("utf-8")


def generate_basic_token(username: str, password: str) -> str:
    return "Basic " + btoa(username + ":" + password)


def request_bearer_token(username: str, password: str) -> str:
    global bearer, session

    if bearer is not None:
        return bearer

    basic_token = generate_basic_token(username, password)

    response = session.get(
        "https://secure.objectiveconnect.co.uk/rest/me",
        params={"emailAddress": username, "noContentReplacesSeeOther": "true"},
        headers={"Authorization": basic_token},
    )

    # get response auth header
    bearer = response.headers["Authorization"]

    return bearer


def fetch_all_workspaces():
    global bearer, session

    response = session.get(
        "https://secure.objectiveconnect.co.uk/publicapi/1/myworkspaces",
        params={
            "page": "",
            "size": "50",
            "sort": "createdDate,desc",
            "includeActions": "true",
            "excludeInvited": "true",
            "noContentReplacesSeeOther": "true",
        },
        headers={"Authorization": bearer},
    )

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    return json.loads(response.text)


def get_workspace(uuid: str):
    global bearer, session

    response = session.get(
        f"https://secure.objectiveconnect.co.uk/publicapi/1/workspaces/{uuid}",
        params={"noContentReplacesSeeOther": "true"},
        headers={"Authorization": bearer},
    )

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    return json.loads(response.text)


def send_access_code(workspace_uuid: str) -> str:
    global bearer, session

    # https://secure.objectiveconnect.co.uk/rest/shares/e0d0-c85b-44f5-400c-bb4b-cb4f-005a-52cb/accesscode?noContentReplacesSeeOther=true
    response = session.put(
        f"https://secure.objectiveconnect.co.uk/rest/shares/{workspace_uuid}/accesscode",
        params={"noContentReplacesSeeOther": "true"},
        headers={"Authorization": bearer, "Content-Type": "application/hal+json"},
        data={"shareUuid": workspace_uuid},
    )

    # print(response.text)
    # print(response.headers)
    # print(response.status_code)

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    return json.loads(response.text)["sendBy"]


def submit_access_code(workspace_uuid: str, access_code: str) -> bool:
    global bearer, session

    # https://secure.objectiveconnect.co.uk/rest/shares/e0d0-c85b-44f5-400c-bb4b-cb4f-005a-52cb/accesscode?noContentReplacesSeeOther=true
    response = session.post(
        f"https://secure.objectiveconnect.co.uk/rest/shares/{workspace_uuid}/accesscode",
        params={"noContentReplacesSeeOther": "true"},
        headers={
            "Authorization": bearer,
            "Content-Type": "application/hal+json",
            "format": "json",
        },
        json={"code": access_code},
    )

    # print(response.text)
    # print(response.headers)
    # print(response.status_code)

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    return response.status_code == 204


def list_assets(workspace_uuid: str, page: int) -> list:
    global bearer, session

    # https://secure.objectiveconnect.co.uk/publicapi/1/assets?page=&size=50&sort=createdDate,desc&includeActions=true&excludeInvited=true&workspaceUuid=e0d0-c85b-44f5-400c-bb4b-cb4f-005a-52cb&parentUuid=e0d0-c85b-44f5-400c-bb4b-cb4f-005a-52cb&noContentReplacesSeeOther=true
    response = session.get(
        f"https://secure.objectiveconnect.co.uk/publicapi/1/assets",
        params={
            "page": page,
            "size": "50",
            "sort": "createdDate,desc",
            "includeActions": "true",
            "excludeInvited": "true",
            "workspaceUuid": workspace_uuid,
            "parentUuid": workspace_uuid,
            "noContentReplacesSeeOther": "true",
        },
        headers={"Authorization": bearer},
    )

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    return json.loads(response.text)


def download_asset(asset: dict) -> bool:
    global bearer, session

    # create the `downloads` dir if doesnt exist
    if not os.path.exists("./downloads"):
        os.mkdir("./downloads")

    # https://secure.objectiveconnect.co.uk/rest/shares/e0d0-c85b-44f5-400c-bb4b-cb4f-005a-52cb/assets/6c41-87f7-ca3d-4552-b18f-364e-764f-e4df/contents/latest?request.preventCache=1676500745385
    response = session.get(
        f"https://secure.objectiveconnect.co.uk/rest/shares/{asset['workspaceUuid']}/assets/{asset['uuid']}/contents/latest",
        params={"request.preventCache": int(time.time() * 1000)},
        # headers={"Authorization": bearer},
    )

    if response.headers["Authorization"] is not None:
        bearer = response.headers["Authorization"]

    out_file = f"{asset['name']}_{asset['uuid']}_v{asset['contentVersion']}.{asset['extension']}"

    out_path = os.path.join("./downloads", out_file)

    with open(out_path, "wb") as f:
        f.write(response.content)
        return True


def main():
    auth = load_auth_details()

    if auth is not None:
        username = auth["username"]
        password = auth["password"]
    else:
        username = input("Email: ")
        password = input("Password: ")
        print("")

    request_bearer_token(username, password)

    workspace_uuid = choose_workspace()
    workspace = get_workspace(workspace_uuid)
    enabled_2fa = workspace["hasTwoStepEnabled"]

    if enabled_2fa:
        valid = False

        while not valid:
            send_access_code(workspace_uuid)
            print("\nA one-time access code has been sent to your email address.")
            access_code = input("Access code: ")
            valid = submit_access_code(workspace_uuid, access_code)

            if not valid:
                print("\nThat access code didn't work. Please try again.\n")

    asset_metadata = list_assets(workspace_uuid, 0)["metadata"]
    pages = asset_metadata["totalPages"]
    totalAssets = asset_metadata["totalElements"]

    currentAsset = 0

    for i in range(0, pages):
        print(f"PAGE {i + 1} of {pages}")
        page_assets = list_assets(workspace_uuid, i)["content"]

        for asset in page_assets:
            currentAsset += 1
            name = asset["name"] + "." + asset["extension"]
            print(f"Downloading asset '{name}'... ({currentAsset}/{totalAssets})")

            download_asset(asset)


def choose_workspace() -> str:
    valid = False

    while not valid:
        try:
            workspaces = fetch_all_workspaces()["content"]

            print("All workspaces:")

            for i, workspace in enumerate(workspaces):
                print(f"{i + 1}: {workspace['name']}")

            choice = int(input("Choose workspace: "))

            if choice < 1 or choice > len(workspaces):
                print("Invalid choice")
                print("Please try again\n")
            else:
                valid = True
        except ValueError:
            print("Invalid choice")
            print("Please try again\n")
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again\n")

    return workspaces[choice - 1]["uuid"]


if __name__ == "__main__":
    main()
