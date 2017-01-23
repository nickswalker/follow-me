import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from git import Repo, InvalidGitRepositoryError

from follow_me.event_handler import GitCommittingEventHandler


def main():
    args = sys.argv[1:]
    path = args[0]
    abs_path = os.path.abspath(path)
    if not os.path.isdir(path):
        sys.stderr.write(abs_path + " is not a valid path.")
        exit(1)
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError as e:
        sys.stderr.write("Please create a Git repository in " + abs_path)
        exit(1)

    if len(repo.branches) == 0:
        sys.stderr.write("Repo has no branches. You may need to add an initial commit if this is a new repo.")
        exit(1)

    print("Attached to repo on branch " + repo.active_branch.name)

    if len(repo.remotes) == 0:
        sys.stderr.write("Please configure an origin remote to sync with.")
        exit(1)

    origin = None
    for remote in repo.remotes:
        if remote.name == "origin":
            origin = remote

    if origin is None:
        sys.stderr.write("Did not find an on origin remote. Please configure origin.")
        exit(1)

    try:
        pass
        # branch_has_remote = repo.active_branch.remote_name
    except ValueError:
        sys.stderr.write("Current branch doesn't have a remote. Please set its upstream.")
        exit(1)

    origin.pull()
    print("Local and remote are in sync. Ready to go.")
    handler = GitCommittingEventHandler(repo, origin)
    observer = Observer()
    observer.schedule(handler, path=path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

    commits = handler.commit_hashes
    if len(commits) == 0:
        exit(0)

    first_commit = commits[0]
    repo.git.reset("--soft", str(first_commit) + "^")

    print("Compressed " + str(len(commits)) + " automated commits.")
    commit_message = input("Enter a commit message for this session:")
    repo.git.commit(m=commit_message)

    repo.git.push(force=True)

if __name__ == '__main__':
    main()