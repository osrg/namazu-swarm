"""job runner
"""
import sys
import threading  # type: ignore
from typing import Any, Dict, List
from queue import Queue
import nmzswarm
from nmzswarm.driver.driver import Driver, ExecutionError
from nmzswarm.scheduler.scheduler import Scheduler
from nmzswarm.logstorage.logstorage import LogStorage
from nmzswarm.progress.event import \
    ContainerCreationEvent, ContainerRemovalEvent, \
    JobEvent, WorkerCompletionEvent
from nmzswarm.progress.progress import ProgressUI
from nmzswarm.progress.summarizer import Summarizer

LOG = nmzswarm.LOG.getChild(__name__)


def run(driver: Driver, scheduler: Scheduler, storage: LogStorage, ui:
        ProgressUI, parallel: int, image: str) -> None:
    """run the job defined in the image in parallel
    """
    schedule = _schedule(driver, scheduler, parallel, image)
    queue = Queue()  # type: Queue
    workers = []
    for i, assigned in enumerate(schedule):
        w = threading.Thread(
            target=_thread,
            args=(i,
                  queue,
                  driver,
                  storage,
                  image,
                  assigned, ))
        workers.append(w)
        w.start()
    LOG.info('Switching to the UI')
    summarizer = ui.run(len(workers),
                        queue,
                        headers={
                            'Orchestration Driver': str(driver),
                            'Image': image,
                            'Workers': len(workers)
                        })
    for w in workers:
        w.join()
    _summarize(summarizer)


def _schedule(driver: Driver, scheduler: Scheduler, parallel: int, image:
              str) -> List[List[Dict[str, Any]]]:
    LOG.info('Determining the schedule')
    container = None  # type: str
    try:
        container = driver.spawn_container(image, privileged=False)
        info, tests = driver.info(container), driver.enum(container)
    finally:
        if container:
            driver.remove_container(container)
    driver.verify_info(info)
    schedule = scheduler.schedule(tests, parallel)
    return schedule


def _summarize(summarizer: Summarizer) -> None:
    LOG.info(str(summarizer))
    if summarizer.failed != 0:
        sys.exit(64)


def _thread(worker_id: int, q: Queue, driver: Driver, storage: LogStorage,
            image: str, tests: List[Dict[str, Any]]):
    q.put(ContainerCreationEvent(worker_id, None))
    container = driver.spawn_container(image, privileged=False)
    q.put(ContainerCreationEvent(worker_id, container, finished=True))
    try:
        for i, test in enumerate(tests):
            command = test['Command']
            q.put(JobEvent(worker_id, command, i, len(tests)))
            code = _run1(driver, storage, container, command)
            q.put(
                JobEvent(
                    worker_id,
                    command,
                    i,
                    len(tests),
                    finished=True,
                    code=code))
    finally:
        q.put(ContainerRemovalEvent(worker_id, container))
        driver.remove_container(container)
        q.put(ContainerRemovalEvent(worker_id, container, finished=True))
        q.put(WorkerCompletionEvent(worker_id))


def _run1(driver: Driver, storage: LogStorage, container: Any, command:
          str) -> int:
    code = 0
    d = storage.create_directory(command)
    try:
        for log_bytes in driver.exek(container, command):
            d.write(log_bytes)
    except ExecutionError as ex:
        code = ex.code
    finally:
        d.finish(code)
    return code
