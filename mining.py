import time
import os
from collections import namedtuple
import xapi
import json
import git
import csv

repo_dir = "C:/Users/Yassin/Downloads/smalltestgit"


def get_repo_data(git_repo, branch="master"):
    """

    :param git_repo: list of CommitData named tuples
    :type git_repo: git.repo.base.Repo
    :param branch:
    :type branch: str
    :return:
    :rtype: list
    """
    result_list = []
    for commit in git_repo.iter_commits(branch):
        result_list.append(commit)
    return result_list

def get_commit_line_changes(prior, successor, repo):
    diff_lines = repo.git.diff("--numstat", prior.hexsha, successor.hexsha).split("\n")
    diff_reader = csv.reader(diff_lines, delimiter="\t")
    file_changes = {line[2]: (line[0], line[1]) for line in diff_reader}
    return file_changes


def get_repo_actions(repo, commit_set):
    # String Manipulation because using a function on the git attribute equals a
    # commandline git command of which the output has to be parsed
    branches = [item.replace("*", "").strip() for item in repo.git.branch().split("\n")]

    # 4 change types A - Add, D - Delete, M - Modified, R - Renamed
    action_lists = {
        "A": [],
        "D": [],
        "M": [],
        "R": [],
    }
    file_line_changes = {}
    for branch in branches:
        repo_data = get_repo_data(repo, branch)


        for successor, prior in zip(repo_data[:-1], repo_data[1:]):
            commit_line_changes = get_commit_line_changes(prior, successor, repo)
            file_line_changes.update(commit_line_changes)
            if successor.hexsha not in commit_set:
                # print(successor.hexsha)
                # Important to diff prior to successor other way around all file ops are reversed
                diff_list = prior.diff(successor)
                commit_set.add(successor.hexsha)
                for action_type in ["A", "D", "M", "R"]:
                    for action in diff_list.iter_change_type(action_type):
                        action_lists[action_type].append({
                            "commit": successor,
                            "action": action,
                        })
            else:
                print("commit already processed")

    return action_lists, file_line_changes
if __name__ == "__main__":
    repo = git.Repo(repo_dir)
    commit_set = set()
    action_lists, file_line_changes = get_repo_actions(repo, commit_set)

    for k, v in action_lists.items():
        print("Action type: {}".format(k))
        for item in v:
            commit_data = item["commit"]
            print("Author: {}, Date: {}, Hash: {}".format(commit_data.author.name,
                         commit_data.committed_date,
                         commit_data.hexsha))

    add_action = action_lists["A"][0]
    add_statemnt = xapi.xapi_statement(add_action["action"],
                                          add_action["commit"],
                                          "",
                                          add_action["action"].change_type,
                                          file_line_changes)
    print("Add Statement")
    print(json.dumps(add_statemnt))

    # commit_list = list(repo.iter_commits("master"))
    # changes = get_commit_line_changes(commit_list[1], commit_list[0], repo)
    # print(changes)


