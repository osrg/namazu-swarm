"""log storage
"""
from abc import ABC, abstractmethod


class LogDirectory(ABC):
    """log directory"""
    @abstractmethod
    def get_path(self) -> str:
        """returns the abstract path to dir"""
        pass

    @abstractmethod
    def write(self, b: bytes) -> None:
        """write bytes"""
        pass

    @abstractmethod
    def finish(self, code: int) -> None:
        """finalize the log with the exit code"""
        pass


class LogStorage(ABC):
    """Stores log output, exit code, and timestamps"""
    @abstractmethod
    def create_directory(self, test_name: str) -> LogDirectory:
        """instantiate LogDirectory"""
        pass
