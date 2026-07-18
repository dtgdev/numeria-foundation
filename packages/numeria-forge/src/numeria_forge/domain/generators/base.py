from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class BaseGenerator(ABC):
    """Base class for all Forge generators."""

    name: str

    @abstractmethod
    def generate(
        self,
        output_directory: Path,
        context: Mapping[str, Any],
    ) -> list[Path]:
        """Generate one or more artifacts."""
        raise NotImplementedError
