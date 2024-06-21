"""
Comprehensive utilities for JSON and Markdown processing.

This module provides a set of functions and classes for handling JSON and
Markdown data, including parsing, conversion, and manipulation of structured
data. It includes utilities for extracting JSON from Markdown, creating and
manipulating parts of structured documents, and converting between different
data formats.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Callable
import pandas as pd
from io import StringIO

# Constants
md_json_char_map = {"'": '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}

py_json_msp = {
    "str": "string",
    "int": "number",
    "float": "number",
    "list": "array",
    "tuple": "array",
    "bool": "boolean",
    "dict": "object",
}

class Part:
    def __init__(
        self,
        id: str,
        part_type: str,
        content: Any,
        title_level: Optional[int] = None,
        table_output: Optional[Any] = None,
        table: Optional[pd.DataFrame] = None,
        markdown: Optional[str] = None,
        page_number: Optional[int] = None,
    ):
        self.id = id
        self.type = part_type
        self.content = content
        self.title_level = title_level
        self.table_output = table_output
        self.table = table
        self.markdown = markdown
        self.page_number = page_number

class MarkdownUtils:
    
    @staticmethod
    def md_to_json(
        str_to_parse: str,
        *,
        expected_keys: Optional[List[str]] = None,
        parser: Optional[Callable[[str], Any]] = None,
    ) -> Any:
        """Parse a JSON block from a Markdown string and validate its keys."""
        json_obj = MarkdownUtils.extract_json_block(str_to_parse, parser=parser or MarkdownUtils.fuzzy_parse_json)

        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in json_obj]
            if missing_keys:
                raise ValueError(f"Missing expected keys in JSON object: {', '.join(missing_keys)}")

        return json_obj

    @staticmethod
    def escape_chars_in_json(value: str, char_map: Optional[Dict[str, str]] = None) -> str:
        """Escape special characters in a JSON string using a character map."""
        char_map = char_map or md_json_char_map
        for k, v in char_map.items():
            value = value.replace(k, v)
        return value

    @staticmethod
    def extract_json_block(
        str_to_parse: str,
        regex_pattern: Optional[str] = None,
        *,
        parser: Optional[Callable[[str], Any]] = None,
    ) -> Any:
        """Extract and parse a JSON block from Markdown content."""
        regex_pattern = regex_pattern or r"```json\n?(.*?)\n?```"

        match = re.search(regex_pattern, str_to_parse, re.DOTALL)
        if match:
            code_str = match.group(1).strip()
        else:
            str_to_parse = str_to_parse.strip()
            if str_to_parse.startswith("```json\n") and str_to_parse.endswith("\n```"):
                code_str = str_to_parse[8:-4].strip()
            else:
                raise ValueError("No JSON code block found in the Markdown content.")

        parser = parser or MarkdownUtils.fuzzy_parse_json
        return parser(code_str)

    @staticmethod
    def create_part(
        part_type: str, element_idx: int, page_number: int, json_item: Dict[str, Any]
    ) -> Part:
        """Create a Part object from JSON item data."""
        return Part(
            id=f"id_page_{page_number}_{part_type}_{element_idx}",
            part_type=part_type,
            title_level=json_item.get("lvl"),
            content=json_item.get("value"),
            markdown=json_item.get("md"),
            page_number=page_number,
        )

    @staticmethod
    def validate_table(part: Part) -> Tuple[bool, bool]:
        """Validate a table part and determine if it's a perfect table."""
        should_keep = True
        perfect_table = True

        table_lines = part.markdown.split("\n")
        table_columns = [len(line.split("|")) for line in table_lines]
        if len(set(table_columns)) > 1:
            perfect_table = False

        if len(table_lines) < 2:
            should_keep = False

        return should_keep, perfect_table

    @staticmethod
    def create_table_part(
        part: Part,
        table: pd.DataFrame,
        node_id: Optional[str],
        page_number: Optional[int],
        idx: int,
    ) -> Part:
        """Create a table part from a DataFrame."""
        return Part(
            id=(f"id_page_{page_number}_{node_id}_{idx}" if node_id else f"id_{idx}"),
            part_type="table",
            content=part.content,
            table=table,
        )

    @staticmethod
    def create_nonperfect_table_part(
        part: Part,
        node_id: Optional[str],
        page_number: Optional[int],
        idx: int,
        perfect_table: bool,
    ) -> Part:
        """Create a part for a non-perfect table or text."""
        return Part(
            id=(f"id_page_{page_number}_{node_id}_{idx}" if node_id else f"id_{idx}"),
            part_type="table_text" if not perfect_table else "text",
            content=part.content,
        )

    @staticmethod
    def create_text_part(
        part: Part, node_id: Optional[str], page_number: Optional[int], idx: int
    ) -> Part:
        """Create a text part."""
        return Part(
            id=(
                f"id_page_{page_number}_{node_id}_{idx}"
                if node_id
                else f"id_page_{page_number}_{idx}"
            ),
            part_type="text",
            content=part.content,
        )

    @staticmethod
    def merge_consecutive_text_parts(parts: List[Part]) -> List[Part]:
        """Merge consecutive text parts into a single part."""
        merged_parts = []
        for part in parts:
            if merged_parts and part.type == "text" and merged_parts[-1].type == "text":
                merged_parts[-1].content += "\n" + part.content
            else:
                merged_parts.append(part)
        return merged_parts

    @staticmethod
    def markdown_to_dataframe(md: str) -> pd.DataFrame:
        """Convert a Markdown table to a pandas DataFrame."""
        return pd.read_csv(StringIO(md), sep="|", engine="python")

    @staticmethod
    def filter_table_part(table_df: Optional[pd.DataFrame]) -> bool:
        """Filter out empty or single-column DataFrames."""
        return table_df is not None and not table_df.empty and len(table_df.columns) > 1

