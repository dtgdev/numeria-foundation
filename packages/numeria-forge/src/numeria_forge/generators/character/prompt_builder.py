"""Prompt builder for Numeria characters."""

from numeria_forge.ai import Prompt


class CharacterPromptBuilder:

    def build(
        self,
        concept: str,
    ) -> Prompt:
        return Prompt(
            instructions=(
                "Generate a children's educational mathematics character."
            ),
            input_text=concept,
        )
