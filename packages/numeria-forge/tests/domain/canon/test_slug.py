import pytest

from numeria_forge.util import slugify


def test_slugify_normalizes_character_name() -> None:
    assert (
        slugify("Captain Integral")
        == "captain-integral"
    )


def test_slugify_removes_extra_symbols() -> None:
    assert (
        slugify("  Lady Limit!  ")
        == "lady-limit"
    )


def test_slugify_rejects_empty_result() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot create a slug",
    ):
        slugify("!!!")
