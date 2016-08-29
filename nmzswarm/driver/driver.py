"""Orchestration driver
"""
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from typing import Any, Dict, Generator, List
from nmzswarm.util import parse_jsonl


class Driver(ABC):
    """Abstract driver class"""
    def info(self, container: str) -> Dict[str, Any]:
        """Executes info-jsonl defined in NamazuSwarmfile"""
        jsons = self._exec_jsonl(container, '/NamazuSwarmfile info-jsonl')
        if len(jsons) != 1:
            raise RuntimeError('bad json lines (must be 1): %s', jsons)
        return jsons[0]

    def enum(self, container: str) -> List[Dict[str, Any]]:
        """Executes enum-jsonl defined in NamazuSwarmfile"""
        return self._exec_jsonl(container, '/NamazuSwarmfile enum-jsonl')

    def exek(self, container: str,
             command: str) -> Generator[bytes, None, None]:
        """Executes exec defined in NamazuSwarmfile.
        If the command exits with a non-zero status,
        an ExecutionError will be raised."""
        # do not need to consider the injection issue here,
        # because the command is executed in the container.
        yield from self._exec(container, '/NamazuSwarmfile exec %s' % command)

    # pylint: disable=no-self-use
    def verify_info(self, info: Dict[str, Any]) -> None:
        """verifies the info"""
        if not info['API'] == 'v0':
            raise RuntimeError('bad info (API not v0) %s' % info)
        try:
            if info['NotReady']:
                raise NotImplementedError('NotReady unsupported: %s' % info)
            if info['RequiresPrivileged']:
                raise NotImplementedError(
                    'RequiresPrivileged unsupported: %s' % info)
        except KeyError:
            pass

    @abstractmethod
    def _exec(self, container: str, command: str) \
            -> Generator[bytes, None, None]:
        pass

    def _exec_jsonl(self, container: str, command: str) \
            -> List[Dict[str, Any]]:
        try:
            out = b''.join(self._exec(container, command))
            jsons = parse_jsonl(out)
            return jsons
        except JSONDecodeError as jde:
            raise RuntimeError(jde, 'error while parsing %s' % out)
        except ExecutionError as ee:
            raise RuntimeError(ee)

    @abstractmethod
    def spawn_container(self, image: str, privileged: bool) -> str:
        """spawn a container"""
        pass

    @abstractmethod
    def remove_container(self, container: str) -> None:
        """remove the container"""
        pass


class ExecutionError(Exception):
    """Raised from Driver.exek.
    """
    def __init__(self, command, code, *args, **kwargs):
        super().__init__('code %d while executing %s' % (code, command),
                         args, kwargs)
        self.command = command
        self.code = code
