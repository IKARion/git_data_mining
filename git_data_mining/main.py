import json
import os
import pathlib

import git
import requests
import csv

from git_data_mining import xapi, mining
import git_data_mining.config as config

headers = {
    "Content-Type": "application/json",
    "X-Experience-API-Version": config.XPERIENCE_API_VERSION,
}


parent_dir = pathlib.Path(__file__).resolve().parent.parent
os.chdir(parent_dir)

META_DATA_PATH = "mikrokurs_bitbucket_account_mapping_processed.csv"

def read_user_metadata(path):
    git_name_moodle_name_mapping = {}
    repo_group_mapping = {}
    with open(path, encoding="utf8") as f:
        dict_reader = csv.DictReader(f)
        processed_user_data_list = []
        for user_data in dict_reader:
            user_data["group"] = int(user_data["group"][1:])
            processed_user_data_list.append(user_data)

        for user_data in processed_user_data_list:
            git_name_moodle_name_mapping[user_data["gitname"]] = user_data["moodlename"]
            repo_name = user_data["repo"].lower()
            repo_group_mapping[repo_name] = user_data["group"]
    return git_name_moodle_name_mapping, repo_group_mapping





def send_xapi_statements(action_lists,
                         file_line_changes,
                         repo_url,
                         repo_name,
                         user_mapping=None,
                         group_mapping=None):
    for k, v in action_lists.items():
        for item in v:
            statement = xapi.xapi_statement(item["action"],
                                            item["commit"],
                                            repo_url,
                                            repo_name,
                                            k,
                                            file_line_changes,
                                            user_mapping,
                                            group_mapping)
            # response = requests.post(SERVER_URL, json=statement, auth=(KEY, SECRET), headers=headers)
            response = send_statement(config.SERVER_URL, statement=statement, auth=(config.KEY, config.SECRET), headers=headers)
            # print("Sent statement:")
            # print(statement)


def send_statement(server_url, statement, auth, headers):
    return requests.post(server_url, json=statement, auth=auth, headers=headers)


def read_commit_sets(path, repo_list):
    commit_set_path = pathlib.Path(path)
    if commit_set_path.exists():
        commit_set_string = commit_set_path.read_text()
        if commit_set_string == "":
            commit_sets = {item["name"]: set() for item in repo_list}
        else:
            commit_dict = json.loads(commit_set_string)
            commit_sets = {k: v.keys() for k, v in commit_dict.items()}
        for repo in repo_list:
            if repo["name"] not in commit_sets:
                commit_sets[repo["name"]] = set()
    else:
        commit_sets = {item["name"]: set() for item in repo_list}

    return commit_sets

def write_commit_sets(commit_set_path, commit_sets):
    with open(str(commit_set_path), "w") as commit_file:
        commit_dicts = {k: dict.fromkeys(v) for k, v in commit_sets.items()}
        json.dump(commit_dicts, commit_file)


#TODO: Mapping from Bitbucket to Moodle users and groups. Use 'mikrokurs_bitbucket_account_mapping.csv'
def main():
    # Collect all repo_data remote and local in a list
    repo_list = []
    for repo_url in config.REMOTE_REPO_LIST:
        repo_name = repo_url.split("/")[-1].split(".")[0]
        repo_dir = os.path.join(config.LOCAL_REPO_PATH, repo_name)
        path = pathlib.Path(repo_dir)
        if path.exists():
            repo = git.Repo(repo_dir)
            repo.remotes[0].pull()
        else:
            repo = git.Repo.clone_from(repo_url, repo_dir)

        repo_url = repo_url[:-4] + "/"
        if "@" in repo_url:
            repo_url = "https://" + repo_url.split("@")[1]
        repo_data = {
            "repo": repo,
            "name": repo_name,
            "path": repo_dir,
            "url": repo_url
        }
        repo_list.append(repo_data)

    for repo_dir in config.LOCAL_REPO_LIST:
        path = pathlib.Path(repo_dir)
        repo = git.Repo(repo_dir)
        repo.remotes[0].pull()
        repo_url = config.LOCAL_URL_PREFIX + repo_dir + "/"
        repo_name = repo_dir.split("/")[-1]

        repo_data = {
            "repo": repo,
            "name": repo_name,
            "path": path,
            "url": repo_url
        }
        repo_list.append(repo_data)

    commit_set_path = "commit_set.json"
    commit_sets = read_commit_sets(commit_set_path, repo_list)

    git_moodle_user_mapping, repo_group_mapping = read_user_metadata(META_DATA_PATH)
    for item in repo_list:
        repo = item["repo"]
        commit_set = commit_sets[item["name"]]
        repo_url = item["url"]
        repo_name = item["name"]
        action_lists, file_line_changes = mining.get_repo_actions(repo, commit_set)
        send_xapi_statements(action_lists,
                             file_line_changes,
                             repo_url,
                             repo_name,
                             git_moodle_user_mapping,
                             repo_group_mapping)

    write_commit_sets(commit_set_path, commit_sets)




if __name__ == "__main__":
    print(os.getcwd())
    main()

