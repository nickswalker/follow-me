from threading import Timer
import os
from watchdog.events import PatternMatchingEventHandler


class GitCommittingEventHandler(PatternMatchingEventHandler):

    def __init__(self, repo, remote):
        super().__init__()
        self.repo = repo
        self.remote = remote
        self.modifications_timer = None
        self.modifications = []
        self.baseline_timer = Timer(60.0, self._baseline_expired)
        self.commit_hashes = []

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
        self.modifications_timer = Timer(20.0, self._modifications_timer_expired)
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
        if len(to_commit) == 0:
            return
        self.repo.index.add(to_commit)
        commit = self.repo.index.commit("Automated commit")
        self.remote.push()
        self.commit_hashes.append(commit)
        print("Pushed " + str(commit)[:10])

    def _modifications_timer_expired(self):
        self.baseline_timer.cancel()

        self.commitandpush()
        self.modifications_timer = None
        self.baseline_timer = Timer(60.0, self._baseline_expired)
        self.baseline_timer.start()

    def _baseline_expired(self):
        if self.modifications_timer:
            self.modifications_timer.cancel()
            self.modifications_timer = None
        self.commitandpush()
        self.baseline_timer = Timer(60.0, self._baseline_expired)
        self.baseline_timer.start()
