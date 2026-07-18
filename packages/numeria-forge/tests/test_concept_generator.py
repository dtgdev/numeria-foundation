from numeria_forge.domain.generators.concept import ConceptGenerator


def test_generator_name():
    generator = ConceptGenerator()

    assert generator.name == "concept"
