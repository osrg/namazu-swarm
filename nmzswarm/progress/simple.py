"""Simple UI
"""
from typing import Any, Dict
from queue import Queue
import nmzswarm
from nmzswarm.progress.event import Event, WorkerCompletionEvent
from nmzswarm.progress.progress import ProgressUI
from nmzswarm.progress.summarizer import Summarizer

LOG = nmzswarm.LOG.getChild(__name__)


def _log_headers(headers: Dict[str, Any]) -> None:
    for k, v in headers.items():
        LOG.info('%s: %s' % (k, v))


def _log_event(ev: Event) -> None:
    LOG.info('Progress: %s' % ev)


class SimpleProgressUI(ProgressUI):
    """Simple UI
    """

    def run(self, workers: int, queue: Queue, headers:
            Dict[str, Any]) -> Summarizer:
        _log_headers(headers)
        summarizer = Summarizer()
        completed = 0
        while completed < workers:
            ev = queue.get()
            assert isinstance(ev, Event)
            _log_event(ev)
            summarizer.handle_event(ev)
            if isinstance(ev, WorkerCompletionEvent):
                completed += 1
        return summarizer
