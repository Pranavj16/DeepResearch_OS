"""Safe loader for packaged prompt files."""

from __future__ import annotations

from pathlib import Path

PROMPTS_DIRECTORY = Path(__file__).resolve().parent


def load_prompt(prompt_name: str) -> str:
    """Load a named Markdown prompt from the prompt directory.

    Only direct Markdown files within the package are accepted to prevent a caller
    from reading arbitrary files through a prompt name.
    """
    prompt_path = (PROMPTS_DIRECTORY / prompt_name).resolve()
    if prompt_path.parent != PROMPTS_DIRECTORY or prompt_path.suffix != ".md":
        message = "Prompt name must reference a Markdown file in the prompts directory."
        raise ValueError(message)
    return prompt_path.read_text(encoding="utf-8")
