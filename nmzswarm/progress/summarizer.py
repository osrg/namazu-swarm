"""Event sequence summarizer
"""
import time
from nmzswarm.progress.event import Event, JobEvent


class Summarizer:
    """summarize the result"""

    def __init__(self) -> None:
        self.completed = 0
        self.failed = 0
        self.job_started = {}  # type: Dict[str, float]
        self.job_took = {}  # type: Dict[str, float]

    def handle_event(self, ev: Event) -> None:
        """handles an event"""
        if isinstance(ev, JobEvent):
            job_id = ev.command
            if not ev.finished:
                self.job_started[job_id] = time.time()
            else:
                self.job_took[job_id] = time.time() - self.job_started[job_id]
                self.completed += 1
                if ev.code != 0:
                    self.failed += 1

    def __str__(self) -> str:
        """summarize the result"""
        s = 'Completed %d jobs (%d failed)\n' % \
            (self.completed, self.failed)
        for k in sorted(self.job_took, key=self.job_took.get):
            v = self.job_took[k]
            s += '%s: took %f seconds (job creation..completion)\n' % (k, v)
        return s
