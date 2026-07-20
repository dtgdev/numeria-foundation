from enum import Enum


class HookPoint(str, Enum):
    """Stable lifecycle points exposed by the Forge compiler."""

    AFTER_LOAD_MANIFEST = "after_load_manifest"
    AFTER_REGISTER_ARTIFACTS = "after_register_artifacts"
    BEFORE_RENDER = "before_render"
    AFTER_RENDER = "after_render"
    BEFORE_PUBLISH = "before_publish"
    AFTER_PUBLISH = "after_publish"
