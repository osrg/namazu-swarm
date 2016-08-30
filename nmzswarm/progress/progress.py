"""UI for showing the progress
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from queue import Queue
from nmzswarm.progress.summarizer import Summarizer


class ProgressUI(ABC):
    """Abstract user interface class
    """

    @abstractmethod
    def run(self, workers: int, queue: Queue, headers:
            Dict[str, Any]) -> Summarizer:
        """run the UI loop
        """
        pass
