import unittest
import os
from test.t_config import *
import git_data_mining.config as config
import git_data_mining.main as m





class MainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(os.getcwd())
        def send_statement_dummy(server_url, statement, auth, headers):
            print("Dummy sending Statement:")
            print(statement)
        m.send_statement = send_statement_dummy
        config.REMOTE_REPO_LIST = TEST_REMOTES
        config.LOCAL_REPO_LIST = TEST_LOCALS

        def read_commit_sets_dummy(path, repo_list):
            commit_sets = {}
            for repo in repo_list:
                commit_sets[repo["name"]] = set()
            return commit_sets

        def write_commit_sets_dummy(commit_set_path, commit_sets):
            pass

        m.read_commit_sets = read_commit_sets_dummy
        m.write_commit_sets = write_commit_sets_dummy

    def test_send_statements(self):
        m.main()





if __name__ == '__main__':
    unittest.main()