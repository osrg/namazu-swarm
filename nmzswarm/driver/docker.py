"""Docker driver
"""
from typing import Generator
from docker import Client
import nmzswarm
from nmzswarm.driver.driver import Driver, ExecutionError

LOG = nmzswarm.LOG.getChild(__name__)


class DockerDriver(Driver):
    """Docker driver
    """

    def __init__(self) -> None:
        self.cli = Client()

    def __str__(self) -> str:
        return 'DockerDriver'

    def _exec(self, container: str, command: str) \
            -> Generator[bytes, None, None]:
        exec_ctx = self.cli.exec_create(container=container, cmd=command)
        gen = self.cli.exec_start(exec_ctx, stream=True)
        yield from gen
        status = self.cli.exec_inspect(exec_ctx)
        code = status['ExitCode']
        if not code == 0:
            raise ExecutionError(command, code)

    def spawn_container(self, image: str, privileged: bool) -> str:
        host_config = self.cli.create_host_config(privileged=privileged)
        container = self.cli.create_container(
            image=image, host_config=host_config)
        self.cli.start(container)
        return container['Id']

    def remove_container(self, container: str) -> None:
        self.cli.stop(container)
        self.cli.remove_container(container)
