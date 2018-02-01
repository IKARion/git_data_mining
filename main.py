import requests
import git
import os
import pathlib
import json

import mining
import xapi
from config import *

headers = {
    "Content-Type": "application/json",
    "X-Experience-API-Version": XPERIENCE_API_VERSION,
}


# SERVER_URL = "http://descartes.inf.uni-due.de:9001/data/xAPI/statements"
#
# REPO_DIR = "C:/Users/Yassin/Downloads/smalltestgit"
#
# KEY = "9ea36f66cff47fcb01d14ae5d69e16814745b41f"
# SECRET = "d47f994dc198684706f42619974be3a05a06c68f"


# def main():
#     headers = {
#         "Content-Type": "application/json",
#         "X-Experience-API-Version": "1.0.3",
#     }
#     repo = git.Repo(REPO_DIR)
#     commit_set = set()
#     action_lists, file_line_changes = mining.get_repo_actions(repo, commit_set)
#     for k, v in action_lists.items():
#         for item in v:
#             statement = xapi.xapi_statement(item["action"], item["commit"], "smalltestgit", k, file_line_changes)
#             response = requests.post(SERVER_URL, json=statement, auth=(KEY, SECRET), headers=headers)
#             print(response.content)
#             print(response)


def send_xapi_statements(action_lists, file_line_changes, repo_name):
    for k, v in action_lists.items():
        for item in v:
            statement = xapi.xapi_statement(item["action"], item["commit"], repo_name, k, file_line_changes)
            response = requests.post(SERVER_URL, json=statement, auth=(KEY, SECRET), headers=headers)

            print("Sent statement:")
            print(statement)


def main():
    # Collect all repo_data remote and local in a list
    repo_list = []
    for repo_url in REMOTE_REPO_LIST:
        repo_name = repo_url.split("/")[-1].split(".")[0]
        repo_dir = os.path.join(LOCAL_REPO_PATH, repo_name)
        path = pathlib.Path(repo_dir)
        if path.exists():
            repo = git.Repo(repo_dir)
            repo.remotes[0].pull()
        else:
            repo = git.Repo.clone_from(repo_url, repo_dir)

        repo_url = repo_url[:-4] + "/"
        repo_data = {
            "repo": repo,
            "name": repo_name,
            "path": repo_dir,
            "url": repo_url
        }
        repo_list.append(repo_data)

    for repo_dir in LOCAL_REPO_LIST:
        path = pathlib.Path(repo_dir)
        repo = git.Repo(repo_dir)
        repo.remotes[0].pull()
        repo_url = LOCAL_URL_PREFIX + repo_dir + "/"

        repo_data = {
            "repo": repo,
            "name": repo_name,
            "path": path,
            "url": repo_url
        }
        repo_list.append(repo_data)

    commit_set_path = pathlib.Path("commitset.json")
    if commit_set_path.exists():
            commit_set_string = commit_set_path.read_text()
            if commit_set_string == "":
                commit_sets = {item["name"]: set() for item in repo_list}
            else:
                commit_dict = json.loads(commit_set_string)
                commit_sets = {k: v.keys() for k, v in commit_dict.items()}
    else:
        commit_sets = {item["name"]: set() for item in repo_list}
    for item in repo_list:
        repo = item["repo"]
        commit_set = commit_sets[item["name"]]
        repo_name = item["url"]
        action_lists, file_line_changes = mining.get_repo_actions(repo, commit_set)
        send_xapi_statements(action_lists, file_line_changes, repo_name)

    with open(str(commit_set_path), "w") as commit_file:
        commit_dicts = {k: dict.fromkeys(v) for k, v in commit_sets.items()}
        json.dump(commit_dicts, commit_file)


if __name__ == "__main__":
    main()
