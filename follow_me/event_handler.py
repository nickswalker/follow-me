import os
from threading import Timer

from watchdog.events import PatternMatchingEventHandler


class GitCommittingEventHandler(PatternMatchingEventHandler):
    def __init__(self, repo, remote, no_push=False, modification_debounce=20, baseline_timer=60, force_all=False):
        super().__init__()
        self.repo = repo
        self.remote = remote
        self.modifications_timer = None
        self.modifications = []
        self.baseline_timer_period = baseline_timer
        self.modification_debounce = modification_debounce
        self.baseline_timer = Timer(baseline_timer, self._baseline_expired)
        self.baseline_timer.start()
        self.commit_hashes = []
        self.no_push = no_push
        self.force_all = force_all

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        if self.modifications_timer:
            self.modifications_timer.cancel()
        self.modifications_timer = Timer(self.modification_debounce, self._modifications_timer_expired)
        self.modifications_timer.start()

        self.modifications.append(os.path.abspath(event.src_path))
        print(event.src_path, event.event_type)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)

    def on_moved(self, event):
        self.process(event)

    def _filter_modification(self, modification):
        return os.path.exists(modification) and not ".git" in modification and modification != self.repo.working_dir

    def commitandpush(self):
        to_commit = [mod for mod in self.modifications if self._filter_modification(mod)]
        self.modifications = []
        if self.force_all:
            self.repo.git.add(all=True)
        else:
            if len(to_commit) == 0:
                return
            self.repo.index.add(to_commit)

        commit = self.repo.index.commit("Automated commit")
        if not self.no_push:
            self.remote.push()
            print("Pushed " + str(commit)[:10])
        else:
            print("New commit " + str(commit)[:10])
        self.commit_hashes.append(commit)

    def _modifications_timer_expired(self):
        self.baseline_timer.cancel()

        self.commitandpush()
        self.modifications_timer = None
        self.baseline_timer = Timer(self.baseline_timer_period, self._baseline_expired)
        self.baseline_timer.start()

    def _baseline_expired(self):
        if self.modifications_timer:
            self.modifications_timer.cancel()
            self.modifications_timer = None
        self.commitandpush()
        self.baseline_timer = Timer(self.baseline_timer_period, self._baseline_expired)
        self.baseline_timer.start()
