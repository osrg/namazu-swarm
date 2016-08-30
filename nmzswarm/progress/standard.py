"""Standard UI
TODO: use curses (we cannot use urwid because it is released under LGPL)
"""
from typing import Any, Dict
from queue import Queue
import textwrap
from terminaltables import SingleTable
from nmzswarm.progress.event import Event, \
    ContainerCreationEvent, ContainerRemovalEvent, \
    JobEvent, WorkerCompletionEvent
from nmzswarm.progress.progress import ProgressUI
from nmzswarm.progress.summarizer import Summarizer


def clear_screen() -> None:
    """clear the screen"""
    print("\033[H" "\033[J")


class TablePrinter:
    """print the table"""

    def __init__(self) -> None:
        self.status = {}  # type: Dict[int, str]
        self.current_job = {}  # type: Dict[int, int]
        self.failed_jobs = {}  # type: Dict[int, int]
        self.jobs = {}  # type: Dict[int, int]

    def handle_event(self, ev: Event) -> None:
        """handles event"""
        wid = ev.worker_id
        if wid not in self.status:
            self.status[wid] = ''
            self.jobs[wid] = 0
            self.current_job[wid] = 0
            self.failed_jobs[wid] = 0
        if isinstance(ev, JobEvent):
            self.status[wid] = 'starting "%s"' % ev.command
            self.jobs[wid] = ev.jobs
            if ev.finished:
                self.current_job[wid] = ev.current
                if ev.code != 0:
                    self.failed_jobs[wid] += 1
                self.status[wid] = 'finished (code: %d) "%s"' % \
                                   (ev.code, ev.command)
        elif isinstance(ev, ContainerCreationEvent):
            if ev.finished:
                self.status[wid] = 'created container %.8s..' % ev.container
            else:
                self.status[wid] = 'creating container'
        elif isinstance(ev, ContainerRemovalEvent):
            if ev.finished:
                self.status[wid] = 'removed container %.8s..' % ev.container
            else:
                self.status[wid] = 'removing container %.8s..' % ev.container
        elif isinstance(ev, WorkerCompletionEvent):
            self.status[wid] = 'completed'

    def do_print(self) -> None:
        """do print"""
        data = [('', 'Jobs', 'Status')]
        for wid, status in self.status.items():
            jobs = '%d/%d (%d failed)' % \
                   (self.current_job[wid] + 1,
                    self.jobs[wid],
                    self.failed_jobs[wid])
            st = '\n'.join(textwrap.wrap(status, 60))
            data.append((str(wid), jobs, st))
        table = SingleTable(data)
        print(table.table)


class ExitMainLoop(Exception):
    """exits the main loop, not an error"""
    pass


class StandardProgressUI(ProgressUI):
    """Standard UI
    """

    def __init__(self) -> None:
        self.headers = {}  # type: Dict[str,Any]
        self.workers = 0
        self.completed = 0
        self.printer = TablePrinter()
        self.summarizer = Summarizer()

    def run(self, workers: int, queue: Queue, headers:
            Dict[str, Any]) -> Summarizer:
        self.workers = workers
        self.headers = headers
        while True:
            try:
                self._step(queue)
            except ExitMainLoop:
                break
        return self.summarizer

    def _step(self, queue: Queue) -> None:
        ev = queue.get()
        assert isinstance(ev, Event)
        self._handle_event(ev)

    def _print_header(self) -> None:
        print('Namazu Swarm: CI Job Parallelizer')
        print('https://github.com/osrg/namazu-swarm')
        print('==============================')
        for k, v in self.headers.items():
            print('%s: %s' % (k, v))
        print('')

    def _handle_event(self, ev: Event) -> None:
        self.printer.handle_event(ev)
        self.summarizer.handle_event(ev)
        # update ui
        clear_screen()
        self._print_header()
        self.printer.do_print()
        # break the loop if all the workers has completed
        if isinstance(ev, WorkerCompletionEvent):
            self.completed += 1
        if self.completed == self.workers:
            raise ExitMainLoop()
