"""Event for showing the progress
"""
from typing import Any


class Event:
    """Generic event
    """
    def __init__(self, worker_id: int) -> None:
        self.worker_id = worker_id


class ContainerEvent(Event):
    """container
    """
    def __init__(self, worker_id: int,
                 container: Any,
                 finished: bool=False) -> None:
        super().__init__(worker_id)
        self.container = container
        self.finished = finished


class ContainerCreationEvent(ContainerEvent):
    """container creation
    """
    def __init__(self, worker_id: int,
                 container: Any=None,
                 finished: bool=False) -> None:
        super().__init__(worker_id, container, finished)

    def __str__(self) -> str:
        if self.finished:
            return 'W%d created container %s' % \
                (self.worker_id, str(self.container))
        else:
            return 'W%d creating container' % self.worker_id


class ContainerRemovalEvent(ContainerEvent):
    """container removal
    """
    def __init__(self, worker_id: int,
                 container: Any,
                 finished: bool=False) -> None:
        super().__init__(worker_id, container, finished)

    def __str__(self) -> str:
        v = 'removed' if self.finished else 'removing'
        return 'W%d %s container %s' % \
            (self.worker_id, v, str(self.container))


class JobEvent(Event):
    """Job progress information
    """
    def __init__(self,
                 worker_id: int,
                 command: str,
                 current: int,
                 jobs: int,
                 finished: bool=False,
                 code: int=0) -> None:
        super().__init__(worker_id)
        self.command = command
        self.current = current
        self.jobs = jobs
        self.finished = finished
        self.code = code

    def __str__(self) -> str:
        v = 'finished (code: %d)' % self.code if self.finished else 'starting'
        return 'W%d %s \"%s\" (%d/%d)' % \
            (self.worker_id, v, self.command, self.current + 1, self.jobs)


class WorkerCompletionEvent(Event):
    """worker completion
    """
    def __init__(self, worker_id: int) -> None:
        super().__init__(worker_id)

    def __str__(self) -> str:
        return 'W%d completed' % self.worker_id
