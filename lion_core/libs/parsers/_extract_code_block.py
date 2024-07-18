"""Provide utility for extracting code blocks from Markdown-formatted text."""


def extract_code_block(str_to_parse: str) -> str:
    """
    Extract code blocks from a given string containing Markdown code blocks.

    This function identifies code blocks enclosed by triple backticks (```)
    and extracts their content. It handles multiple code blocks and
    concatenates them with two newlines between each block.

    Args:
        str_to_parse: The input string containing Markdown code blocks.

    Returns:
        Extracted code blocks concatenated with two newlines. If no code
        blocks are found, returns an empty string.

    Example:
        >>> text = "Some text\\n```python\\nprint('Hello')\\n```\\nMore text"
        >>> extract_code_blocks(text)
        "print('Hello')"
    """
    code_blocks = []
    lines = str_to_parse.split("\n")
    inside_code_block = False
    current_block = []

    for line in lines:
        if line.startswith("```"):
            if inside_code_block:
                code_blocks.append("\n".join(current_block))
                current_block = []
                inside_code_block = False
            else:
                inside_code_block = True
        elif inside_code_block:
            current_block.append(line)

    if current_block:
        code_blocks.append("\n".join(current_block))

    return "\n\n".join(code_blocks)


# File: lion_core/libs/parsers/_extract_code_blocks.py
