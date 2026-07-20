from pathlib import Path

import pytest

from numeria_forge.publishing import (
    PublishContext,
    Publisher,
    PublishResult,
)


class TextPublisher(Publisher[str]):
    @property
    def name(self) -> str:
        return "text"

    def publish(
        self,
        value: str,
        context: PublishContext,
    ) -> PublishResult:
        path = context.output_directory / "value.txt"
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            value,
            encoding="utf-8",
        )

        return PublishResult(
            publisher=self.name,
            path=path,
            media_type="text/plain",
        )


def test_publisher_writes_domain_value(
    tmp_path: Path,
) -> None:
    publisher = TextPublisher()

    result = publisher.publish(
        "Numeria",
        PublishContext(
            output_directory=tmp_path,
        ),
    )

    assert result.publisher == "text"
    assert result.media_type == "text/plain"
    assert result.path == tmp_path / "value.txt"
    assert result.path.read_text(
        encoding="utf-8",
    ) == "Numeria"


def test_publish_context_rejects_non_path() -> None:
    with pytest.raises(
        TypeError,
        match="output_directory must be a Path",
    ):
        PublishContext(
            output_directory="output",  # type: ignore[arg-type]
        )


def test_publish_result_rejects_empty_publisher() -> None:
    with pytest.raises(
        ValueError,
        match="publisher must not be empty",
    ):
        PublishResult(
            publisher=" ",
            path=Path("value.txt"),
            media_type="text/plain",
        )


def test_publish_result_rejects_empty_media_type() -> None:
    with pytest.raises(
        ValueError,
        match="media_type must not be empty",
    ):
        PublishResult(
            publisher="text",
            path=Path("value.txt"),
            media_type=" ",
        )
