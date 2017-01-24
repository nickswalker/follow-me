# Follow Me

A command line utility that periodically commits and pushes all changes made in a Git working tree. Perfect for workshops or
other live-coding setups where you want to have a live view of your project state available for the audience.

## Installation

Clone the repo down. Now you can run `run.py` with Python 3.

## Usage

Make sure your repo is configured to push the current branch to some remote, then

    # In the directory you'd like to broadcast
    python <install-path>/run.py

That's it. You're in a live session now. `ctrl-c` to end the session. You'll have the option to squash your session and enter
a new commit message.

### Options

* `<path> <remote>`: path and the name of the remote to push to
* `--no-push`: Local only. Good for testing

## Tips and Workarounds

* Some editors use an alternative method of saving files which [presents difficulties](https://github.com/gorakhargosh/watchdog#about-using-watchdog-with-editors-like-vim) for file system change notifications. You may need
to reconfigure your editor.