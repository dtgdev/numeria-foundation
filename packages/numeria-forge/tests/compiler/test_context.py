
from numeria_forge.compiler import CompilerContext

def test_context_defaults() -> None:

    context = CompilerContext(

        project_name="Numeria",

    )

    assert context.project_name == "Numeria"

    assert context.characters == []

    assert context.publish_results == []

    assert context.diagnostics == []

