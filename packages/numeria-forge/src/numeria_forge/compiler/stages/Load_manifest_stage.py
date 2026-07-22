"""Deprecated duplicate module.

Kept only so any stale import of this (incorrectly capitalized) module
path keeps working. Use
``numeria_forge.compiler.stages.load_manifest.LoadManifestStage`` (also
re-exported as ``numeria_forge.compiler.stages.LoadManifestStage``).
"""

from __future__ import annotations

from numeria_forge.compiler.stages.load_manifest import LoadManifestStage

__all__ = ["LoadManifestStage"]
