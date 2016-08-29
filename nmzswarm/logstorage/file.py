"""filesystem-based log storage
"""
import json
import os
import os.path
import time
import urllib.parse
from nmzswarm.logstorage.logstorage import LogDirectory, LogStorage


def _quote(path: str) -> str:
    return urllib.parse.quote(path, safe='')


class FileLogStorage(LogStorage):
    """Filesystem-based implementation
    """
    def __init__(self, path: str) -> None:
        self.path = path

    def create_directory(self, test_name: str) -> LogDirectory:
        return FileLogDirectory(self.path, test_name)


class FileLogDirectory(LogDirectory):
    """Filesystem-based implementation
    """
    def __init__(self, path: str, test_name: str) -> None:
        self.path = path
        self.test_name = test_name
        self.start = time.time()
        self.directory = self._directory()
        os.makedirs(self.directory)
        log_path = os.path.join(self.directory, 'log.txt')
        self.log_file = open(log_path, 'wb')

    def _directory(self) -> str:
        base = os.path.join(self.path, _quote(self.test_name))
        # FIXME: d can cause collision
        d = '%0.9f' % self.start
        path = os.path.join(base, d)
        return path

    def get_path(self) -> str:
        return self.directory

    def write(self, b: bytes) -> None:
        self.log_file.write(b)
        self.log_file.flush()

    def finish(self, code: int) -> None:
        finish = time.time()
        result_path = os.path.join(self.directory, 'result.json')
        result = {'StartedAt': self.start,
                  'FinishedAt': finish,
                  'ExitCode': code}
        with open(result_path, 'w') as f:
            json.dump(result, f)
            f.write('\n')
        self.log_file.close()
        self.log_file = None
