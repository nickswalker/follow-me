# Follow Me

A command line utility that periodically commits and pushes all changes made in a Git working tree. Perfect for workshops or
other live-coding setups where you want to have a live view of your project state available for the audience.

## Installation

Clone the repo down. Now you can run the included `run.py` with Python 3.


## Usage

Make sure your repo is configured to push the current branch to some remote, then

    # In the directory you'd like to broadcast
    python <install-path>/run.py

That's it. You're in a live session now. `ctrl-c` to end the session. You'll have the option to squash your session and enter a new commit message.

You can also specify the path to the repo and the remote you'd like to push to

    python <install-path>/run.py <path> <remote>

### Options

* `-h`: display information about arguments and options
* `--no-push`: Local only. Good for testing
* `--modification-debounce <int>`:
* `--baseline-timer <int>`: 
* `--force-all`: Instead of only adding files that are modified, run use `git add --all` to catch all changes. You can use this to work around issues with modification detection


## Tips and Workarounds

* Some editors, including Vim and Xcode, use an alternative method of saving files which [presents difficulties](https://github.com/gorakhargosh/watchdog#about-using-watchdog-with-editors-like-vim) for file system change notifications. You can work around this by using the force all flag and a frequent baseline timer. Note that this will commit **all** changes, so if you had

	python <install-path>/run.py --baseline-timer 20 --force-all

	