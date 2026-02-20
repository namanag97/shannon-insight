"""Runtime context for FRESH-BUILD kernel."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Optional
import time


class Phase(Enum):
    INIT = auto()
    EXTRACT = auto()
    POPULATE = auto()
    ALGORITHMS = auto()
    CROSS_LAYER = auto()
    FUSION = auto()
    FINDERS = auto()
    PERSIST = auto()
    DONE = auto()


@dataclass
class RuntimeContext:
    """Execution context for the FRESH-BUILD kernel."""
    root: Path
    phase: Phase = Phase.INIT
    start_time: float = field(default_factory=time.time)

    # Progress tracking
    total_files: int = 0
    processed_files: int = 0

    # Cancellation
    _cancelled: bool = False

    # Callbacks
    on_progress: Optional[Callable[[str, float], None]] = None

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def advance(self, message: str = "") -> None:
        self.processed_files += 1
        if self.on_progress:
            progress = self.processed_files / max(self.total_files, 1)
            self.on_progress(message, progress)

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time
