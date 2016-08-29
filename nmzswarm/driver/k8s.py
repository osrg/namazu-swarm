"""Kubernetes driver
"""
import os.path
import shlex
import subprocess  # type: ignore
import time
from typing import Any, Generator, List
import nmzswarm
from nmzswarm.util import parse_json
from nmzswarm.driver.driver import Driver, ExecutionError

LOG = nmzswarm.LOG.getChild(__name__)


def _generate_pod_name(image: str)->str:
    return '%s-%s' % (os.path.basename(image).replace(':', '-'),
                      str(time.time()).replace('.', '-'))


def _run_subprocess(command: List[str]) -> Any:
    LOG.debug('Executing "%s"' % command)
    return subprocess.run(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)


def _kubectl_get_pod_ready(pod: str) -> bool:
    kcommand = ['kubectl', 'get', '-o', 'json', 'pod', pod]
    result = _run_subprocess(kcommand)
    if not result.returncode == 0:
        raise RuntimeError('Could not get %s: %s'
                           % (pod, str(result.stdout)))
    info = parse_json(result.stdout)
    ready = False
    try:
        statuses = info['status']['containerStatuses']
        if len(statuses) != 1:
            raise RuntimeError('strange statuses (len must be 1): %s',
                               statuses)
        ready = statuses[0]['ready']
    except KeyError:
        # expected while scheduling
        return False
    return ready


def _wait_pod_ready(pod: str,
                    times: int=1000 * 1000,
                    interval_secs: float=2) -> None:
    for _ in range(times):
        ready = _kubectl_get_pod_ready(pod)
        if ready:
            return
        time.sleep(interval_secs)
    raise RuntimeError('timed out while waiting %s to be ready', pod)


class KubernetesDriver(Driver):
    """Kubernetes driver
    """
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return 'KubernetesDriver'

    def _exec(self, container: str, command: str) \
            -> Generator[bytes, None, None]:
        kcommand = ['kubectl', 'exec', str(container), '--']
        kcommand.extend(shlex.split(command))
        result = _run_subprocess(kcommand)
        yield result.stdout
        if not result.returncode == 0:
            raise ExecutionError(command, result.returncode)

    def spawn_container(self, image: str, privileged: bool) -> str:
        if privileged:
            raise NotImplementedError('privileged is not supported yet')
        name = _generate_pod_name(image)
        kcommand = ['kubectl', 'run', name,
                    '--image', image,
                    '--restart=Never']
        result = _run_subprocess(kcommand)
        if not result.returncode == 0:
            raise RuntimeError('Could not spawn a pod %s for container: %s'
                               % (name, str(result.stdout)))
        LOG.debug('Created pod %s' % name)
        _wait_pod_ready(name)
        return name

    def remove_container(self, container: str) -> None:
        kcommand = ['kubectl', 'delete', 'pod', str(container)]
        result = _run_subprocess(kcommand)
        if not result.returncode == 0:
            raise RuntimeError('Could not remove %s: %s'
                               % (str(container), str(result.stdout)))
        LOG.debug('removed pod %s' % container)
