from numeria_forge.domain.artifacts import ArtifactDefinition


def test_definition_fields():
    definition = ArtifactDefinition(
        name="readme",
        template="concept/README.md.j2",
        media_type="text/markdown",
        default_destination="README.md",
    )

    assert definition.name == "readme"
    assert definition.template.endswith(".j2")