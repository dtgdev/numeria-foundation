from numeria_forge.domain.artifacts import create_builtin_registry


def test_builtin_registry_contains_readme():
    registry = create_builtin_registry()

    definition = registry.lookup("readme")

    assert definition.name == "readme"
    assert definition.template == "concept/README.md.j2"
    assert definition.default_destination == "README.md"
    assert definition.media_type == "text/markdown"