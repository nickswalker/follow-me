import argparse
import os
import sys
import tempfile
import time
from subprocess import call

from git import Repo, InvalidGitRepositoryError
from watchdog.observers import Observer

from follow_me.event_handler import GitCommittingEventHandler
from follow_me.util import query_yes_no


def validate_repo(path, remote_name):
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError as e:
        sys.stderr.write("Please create a Git repository in " + path)
        exit(1)

    if len(repo.branches) == 0:
        sys.stderr.write("Repo has no branches. You may need to add an initial commit if this is a new repo.")
        exit(1)

    print("Attached to repo on branch " + repo.active_branch.name)

    if len(repo.remotes) == 0:
        sys.stderr.write("Please configure an origin remote to sync with.")
        exit(1)

    remote = None
    for candidate in repo.remotes:
        if candidate.name == remote_name:
            remote = candidate

    if remote is None:
        sys.stderr.write("Did not find an " + remote_name + " remote. Please configure origin.")
        exit(1)

    try:
        pass
        # branch_has_remote = repo.active_branch.remote_name
    except ValueError:
        sys.stderr.write("Current branch doesn't have a remote. Please set its upstream.")
        exit(1)

    remote.pull()
    print("Local and remote are in sync. Session started.")
    return repo, remote


def squash_session(repo, commits):
    first_commit = commits[0]
    repo.git.reset("--soft", str(first_commit) + "^")

    print("Squashed " + str(len(commits)) + " automated commits.")

    message = get_commit_message(b"Follow Me session\n# Enter a commit message")
    repo.git.commit(m=message)


def get_commit_message(initial_message=b""):
    EDITOR = os.environ.get('EDITOR', 'nano')

    with tempfile.NamedTemporaryFile(suffix=b".tmp", mode="w+b") as tf:
        tf.write(initial_message)
        tf.flush()
        call([EDITOR, tf.name])

        # do the parsing with `tf` using regular File operations.
        # for instance:
        tf.seek(0)
        edited_message = tf.read()

    edited_message = edited_message.decode("utf-8")

    lines = edited_message.split("\n")
    lines = [line.strip() for line in lines if not line.strip().startswith("#")]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path", type=str, default=".", nargs="?", help="Path to git repo to use")
    parser.add_argument("remote", type=str, default="origin", nargs="?", help="Name of remote to push to")
    parser.add_argument("--no-push", action='store_true', default=False)
    parser.add_argument("--modification-debounce", type=int, default=20)
    parser.add_argument("--baseline-timer", type=int, default=60)
    parser.add_argument("--force-all", action='store_true', default=False)
    args = parser.parse_args()

    abs_path = os.path.abspath(args.path)
    if not os.path.isdir(args.path):
        sys.stderr.write(abs_path + " is not a valid path.")
        exit(1)

    repo, remote = validate_repo(abs_path, args.remote)

    handler = GitCommittingEventHandler(repo, remote, no_push=args.no_push,
                                        modification_debounce=args.modification_debounce,
                                        baseline_timer=args.baseline_timer,
                                        force_all=args.force_all)
    observer = Observer()
    observer.schedule(handler, path=abs_path)
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

    squash = query_yes_no("Squash this session's commits?")
    if squash:
        squash_session(repo, commits)
        if not args.no_push:
            repo.git.push(force=True)


if __name__ == '__main__':
    main()
