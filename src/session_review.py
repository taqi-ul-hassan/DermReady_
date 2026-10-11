"""Per-browser-session invalidation: a late response cannot restore an old review."""
from threading import Lock


class ReviewSession:
    def __init__(self):
        self._revision=0
        self._lock=Lock()

    def __deepcopy__(self,memo):
        # Each Gradio browser session gets its own gate and no image storage.
        return type(self)()

    def invalidate(self):
        with self._lock:
            self._revision+=1

    def run(self,operation):
        with self._lock:
            self._revision+=1
            revision=self._revision
        result=operation()
        with self._lock:
            return result if revision==self._revision else None
