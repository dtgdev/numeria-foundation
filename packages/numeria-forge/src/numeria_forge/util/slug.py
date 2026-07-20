"""Utilities for creating canonical URL-safe slugs."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str) -> str:
    """Convert text into a lowercase, hyphen-separated slug."""

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        ascii_value,
    ).strip("-").lower()

    if not slug:
        raise ValueError(
            "Cannot create a slug from an empty value."
        )

    return slug
