"""Event sequence summarizer
"""
from nmzswarm.progress.event import Event, JobEvent


class Summarizer:
    """summarize the result"""
    def __init__(self) -> None:
        self.completed = 0
        self.failed = 0

    def handle_event(self, ev: Event) -> None:
        """handles an event"""
        if isinstance(ev, JobEvent):
            if ev.finished:
                self.completed += 1
                if ev.code != 0:
                    self.failed += 1

    def __str__(self) -> str:
        """summarize the result"""
        return 'Completed %d jobs (%d failed)' % \
            (self.completed, self.failed)
