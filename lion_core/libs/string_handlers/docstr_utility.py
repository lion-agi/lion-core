"""
Enhanced utilities for function introspection and schema generation.

This module provides tools for extracting function details from docstrings
and generating function schemas based on type annotations and docstrings.
"""

import inspect
from collections import defaultdict
from typing import Callable, Dict, Tuple, Any, Optional


def strip_lower(s: str) -> str:
    """Convert string to lowercase and strip whitespace."""
    return s.strip().lower()


class DocstringUtils:
    @staticmethod
    def extract_docstring_details(
        func: Callable,
        style: str = "google"
    ) -> Tuple[Optional[str], Dict[str, str]]:
        """
        Extract function description and parameter descriptions from docstring.

        Args:
            func: The function from which to extract docstring details.
            style: The style of docstring to parse ('google' or 'reST').

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.

        Raises:
            ValueError: If an unsupported style is provided.

        Examples:
            >>> def example_function(param1: int, param2: str):
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     pass
            >>> desc, params = FunctionUtils.extract_docstring_details(
            ...     example_function, style='google'
            ... )
            >>> desc
            'Example function.'
            >>> params == {'param1': 'The first parameter.',
            ...            'param2': 'The second parameter.'}
            True
        """
        if strip_lower(style) == "google":
            return DocstringUtils._extract_docstring_details_google(func)
        elif strip_lower(style) == "rest":
            return DocstringUtils._extract_docstring_details_rest(func)
        else:
            raise ValueError(
                f'{style} is not supported. Choose "google" or "reST".'
            )

    @staticmethod
    def _extract_docstring_details_google(
        func: Callable
    ) -> Tuple[Optional[str], Dict[str, str]]:
        """
        Extract details from Google-style docstring.

        Args:
            func: The function from which to extract docstring details.

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.
        """
        docstring = inspect.getdoc(func)
        if not docstring:
            return None, {}
        
        lines = docstring.split("\n")
        func_description = lines[0].strip()

        params_description = {}
        param_start_pos = next(
            (
                i + 1
                for i in range(1, len(lines))
                if strip_lower(lines[i]).startswith(("args", "arguments", "parameters"))
            ),
            0,
        )
        current_param = None
        for line in lines[param_start_pos:]:
            if line == "":
                continue
            elif line.startswith(" "):
                param_desc = line.split(":", 1)
                if len(param_desc) == 1:
                    params_description[current_param] += f" {param_desc[0].strip()}"
                    continue
                param, desc = param_desc
                param = param.split("(")[0].strip()
                params_description[param] = desc.strip()
                current_param = param
            else:
                break
        return func_description, params_description

    @staticmethod
    def _extract_docstring_details_rest(
        func: Callable
    ) -> Tuple[Optional[str], Dict[str, str]]:
        """
        Extract details from reStructuredText-style docstring.

        Args:
            func: The function from which to extract docstring details.

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.
        """
        docstring = inspect.getdoc(func)
        if not docstring:
            return None, {}
        
        lines = docstring.split("\n")
        func_description = lines[0].strip()

        params_description = {}
        current_param = None
        for line in lines[1:]:
            line = line.strip()
            if line.startswith(":param"):
                param_desc = line.split(":", 2)
                _, param, desc = param_desc
                param = param.split()[-1].strip()
                params_description[param] = desc.strip()
                current_param = param
            elif line.startswith(" "):
                params_description[current_param] += f" {line}"

        return func_description, params_description

    @staticmethod
    def function_to_schema(
        func: Callable,
        style: str = "google",
        func_description: Optional[str] = None,
        params_description: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a schema description for a given function.

        Args:
            func: The function to generate a schema for.
            style: The docstring style ('google' or 'reST').
            func_description: Custom function description.
            params_description: Custom parameter descriptions.

        Returns:
            A schema describing the function, including its name,
            description, and parameter details.

        Example:
            >>> def example_func(param1: int, param2: str) -> bool:
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     return True
            >>> schema = FunctionUtils.function_to_schema(example_func)
            >>> schema['function']['name']
            'example_func'
        """
        func_name = func.__name__

        if not func_description or not params_description:
            func_desc, params_desc = DocstringUtils.extract_docstring_details(
                func, style
            )
            func_description = func_description or func_desc
            params_description = params_description or params_desc

        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        py_json_msp = defaultdict(
            lambda: "string",
            {
                "int": "integer",
                "float": "number",
                "bool": "boolean",
                "list": "array",
                "dict": "object"
            }
        )

        for name, param in sig.parameters.items():
            param_type = (py_json_msp[param.annotation.__name__]
                          if param.annotation is not inspect.Parameter.empty
                          else "string")
            param_description = params_description.get(name)
            parameters["required"].append(name)
            parameters["properties"][name] = {
                "type": param_type,
                "description": param_description,
            }

        return {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func_description,
                "parameters": parameters,
            },
        }


# Example usage
if __name__ == "__main__":
    def example_func(param1: int, param2: str) -> bool:
        """Example function.

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.

        Returns:
            bool: A boolean result.
        """
        return True

    schema = DocstringUtils.function_to_schema(example_func)
    print(schema)