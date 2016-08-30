"""Scheduler
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Scheduler(ABC):
    """Scheduler
    """

    @abstractmethod
    def schedule(self, tests: List[Dict[str, Any]], max_parallel:
                 int) -> List[List[Dict[str, Any]]]:
        """Schedules the test cases in parallel
        """
        pass
