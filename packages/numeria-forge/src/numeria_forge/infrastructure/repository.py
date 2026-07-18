from pathlib import Path


class RepositoryWriter:
    """Safely writes generated content into a Forge repository."""

    def write(
        self,
        destination: Path,
        content: str,
        overwrite: bool = False,
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists() and not overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing file: {destination}"
            )

        destination.write_text(content, encoding="utf-8")

        return destination
