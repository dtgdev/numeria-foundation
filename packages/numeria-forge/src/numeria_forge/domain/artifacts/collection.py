from dataclasses import dataclass, field
from .artifact import Artifact



@dataclass(slots=True)
class ArtifactCollection:
    artifacts: list[Artifact] = field(default_factory=list)

    def add(self, artifact: Artifact) -> None:
        self.artifacts.append(artifact)

    def clear(self) -> None:
        self.artifacts.clear()

    def __iter__(self):
        return iter(self.artifacts)

    def __len__(self):
        return len(self.artifacts)

    def __getitem__(self, index: int) -> Artifact:
        return self.artifacts[index]