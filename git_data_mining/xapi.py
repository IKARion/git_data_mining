import datetime

from git_data_mining.xapi_schema import *

# TODO: user and group mapping
def xapi_statement(git_diff, commit, repo_name, action_type, file_line_changes, userMapping=None, groupMapping=None):
    # Z stands for UTC timezone
    # example 2013-08-20T14:22:20.028Z
    timestamp_template = "{}-{:0>2}-{:0>2}T{:0>2}:{:0>2}:{:0>2}.000Z"
    epoch_time = commit.committed_date
    # utc time
    utc_time = datetime.datetime.utcfromtimestamp(epoch_time)
    timestamp = timestamp_template.format(utc_time.year,
                                          utc_time.month,
                                          utc_time.day,
                                          utc_time.hour,
                                          utc_time.minute,
                                          utc_time.second)

    statement_types = {
        "A": {
            "id": ADD_VERB_ID,
            "display": "added",
            "fileUrl": git_diff.b_path,
        },
        "D": {
            "id": DELETE_VERB_ID,
            "display": "deleted",
            "fileUrl": git_diff.a_path,
        },
        "M": {
            "id": MODIFIED_VERB_ID,
            "display": "updated",
            "fileUrl": git_diff.a_path,
        },
        "R": {
            "id": RENAMED_VERB_ID,
            "display": "renamed",
            "fileUrl": git_diff.a_path,
        },
    }

    action_data = statement_types[action_type]
    added_lines, deleted_lines = file_line_changes[action_data["fileUrl"]]

    statement = {
        "actor": {
            "name": commit.author.name if userMapping is None else userMapping[commit.author.name],
            "mbox": "mailto:" + commit.author.email,
            # "account": {
            #     "name": commit.author.name,
            #     "homePage": "http://collide.info",
            # },
            "objectType": "Agent",
        },
        "verb": {
            "id": action_data["id"],
            "display": {
                "en-US": action_data["display"]
            }
        },
        "object": {
            # Ids need to be urls
            "id": repo_name + action_data["fileUrl"],
            "definition": {
                "name": {
                    "en-US": "File"
                },
                "extensions": {
                    GIT_EXTENSION_ID: {
                        "name": "gitExtension",
                        "fileURL": action_data["fileUrl"],
                        "type": FILE_ID,
                        "added_lines": added_lines,
                        "deleted_lines": deleted_lines,
                    }
                },
            },
        },
        "timestamp": timestamp,

        "context": {
            "extensions": {
                COMMIT_EXTENSION_ID: {
                    "name": "Commit Data",
                    "repository": repo_name,
                    "commit_hash": commit.hexsha,
                    "commit_message": commit.message,
                    "type": COMMIT_EXTENSION_ID
                },
                GROUP_EXTENSION : { # Added group extension
                    repo_name: {
                        "name": repo_name,
                        "id": repo_name
                    }

                }
            }
        }
    }
    if groupMapping is not None:
        statement[GROUP_EXTENSION] = groupMapping[repo_name] # Add repo - moodle group mapping

    if action_type == "R":
        statement["object"]["definition"]["extensions"][GIT_EXTENSION_ID]["newFileName"] = git_diff.b_path

    return statement


def xapi_commit_statement(commit_data, repo_name):
    """

    :param commit_data:
    :type commit_data: mining.CommitData
    :return:
    :rtype:
    """

    # Z stands for UTC timezone
    # example 2013-08-20T14:22:20.028Z
    timestamp_template = "{}-{}-{}T{}:{}:{}.000Z"
    epoch_time = commit_data.time
    # utc time
    utc = datetime.utc(epoch_time)

    timestamp = timestamp_template.format(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second)
    statement = {
        "actor": {
            "name": commit_data.author,
        },
        "verb": {
            "id": COMMIT_VERB_ID,
            "display": {
                "en-US": "commited"
            }
        },
        "object": {
            "id": REPO_OBJECT_ID,
            "definition": {
                "name": {
                    "en-US": "repository"
                },
            },
        },
        "timestamp": timestamp,
    }

    return statement
