"""Naive scheduler
"""
from typing import Any, Dict, List
from nmzswarm.scheduler.scheduler import Scheduler


class NaiveScheduler(Scheduler):
    """Naive scheduler
    """
    def schedule(self, tests: List[Dict[str, Any]],
                 max_parallel: int) -> List[List[Dict[str, Any]]]:
        start = 0
        cols = min(len(tests), max_parallel)
        l = []
        for i in range(cols):
            stop = start + len(tests[i::cols])
            l.append(tests[start:stop])
            start = stop
        return l
