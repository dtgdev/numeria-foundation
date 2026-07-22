"""Load every `entity.yaml` beneath a knowledge root into a Canon."""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.domain.canon.canon import (
    Canon,
    CanonLoadError,
    CanonLoadErrorCode,
)
from numeria_forge.domain.canon.entity import CanonEntity


class CanonLoader:
    """Walk a knowledge root and load every entity into a :class:`Canon`.

    Unlike the original ``scripts/validate_*.py``, a single bad file never
    aborts the whole load or crashes with a raw traceback: read/parse
    failures are recorded as :class:`CanonLoadError` entries on the
    returned ``Canon`` so validators (or callers) can report them as
    proper diagnostics.
    """

    ENTITY_FILENAME = "entity.yaml"

    def load(self, knowledge_root: Path) -> Canon:
        canon = Canon(root=knowledge_root)

        if not knowledge_root.is_dir():
            canon.load_errors.append(
                CanonLoadError(
                    path=knowledge_root,
                    message=f"Knowledge root does not exist: {knowledge_root}",
                    code=CanonLoadErrorCode.MISSING_ROOT,
                )
            )
            return canon

        for path in sorted(knowledge_root.rglob(self.ENTITY_FILENAME)):
            self._load_one(path, canon)

        return canon

    def _load_one(self, path: Path, canon: Canon) -> None:
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message=f"Could not read file: {exc}",
                    code=CanonLoadErrorCode.READ_ERROR,
                )
            )
            return

        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message=f"Invalid YAML: {exc}",
                    code=CanonLoadErrorCode.PARSE_ERROR,
                )
            )
            return

        if not isinstance(data, dict):
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message="Entity root must be a mapping",
                    code=CanonLoadErrorCode.INVALID_SHAPE,
                )
            )
            return

        entity_id = data.get("id")
        entity_type = data.get("type")

        if not entity_id:
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message="Entity is missing 'id'",
                    code=CanonLoadErrorCode.MISSING_ID,
                )
            )
            return

        if not entity_type:
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message="Entity is missing 'type'",
                    code=CanonLoadErrorCode.MISSING_TYPE,
                )
            )
            return

        if entity_id in canon.entities:
            existing = canon.entities[entity_id]
            canon.load_errors.append(
                CanonLoadError(
                    path=path,
                    message=(
                        f"Duplicate id '{entity_id}'; already used by "
                        f"{existing.source_path}"
                    ),
                    code=CanonLoadErrorCode.DUPLICATE_ID,
                )
            )
            return

        canon.entities[entity_id] = CanonEntity(
            id=entity_id,
            type=entity_type,
            source_path=path,
            data=data,
        )
