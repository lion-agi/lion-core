# Action Module

## Overview

The Action module is a core component of the Lion framework, providing a flexible and extensible system for managing, calling, and executing tools (functions) with advanced processing capabilities. This module is designed to support complex workflows, function chaining, and dynamic tool management in AI-driven applications.

## Components

### ToolManager (`tool_manager.py`)

The `ToolManager` class is responsible for registering, managing, and invoking tools within the system. It provides a centralized registry for all available tools and handles the matching of function calls to the appropriate tool.

Key features:
- Tool registration and management
- Function call matching and invocation
- Tool schema retrieval

### FunctionCalling (`function_calling.py`)

The `FunctionCalling` class represents a callable function with its arguments. It encapsulates the execution process, including pre-processing, function invocation, and post-processing steps.

Key features:
- Delayed function execution
- Support for pre-processing and post-processing
- Integration with the `Tool` class for advanced function handling

### Tool (`tool.py`)

The `Tool` class represents a callable tool with metadata and processing capabilities. It encapsulates a function along with its schema and optional processing functions.

Key features:
- Function schema generation
- Pre-processing and post-processing capabilities
- Result parsing for JSON serialization

## Interaction Flow

1. Tools are registered with the `ToolManager` using the `register_tool` or `register_tools` methods.
2. When a function call is received, the `ToolManager` matches it to the appropriate tool using the `match_tool` method.
3. The matched tool is wrapped in a `FunctionCalling` object, which handles the execution process.
4. The `FunctionCalling` object invokes the tool, applying any pre-processing or post-processing steps defined in the `Tool` object.

## Usage Example

```python
from lion_core.action import ToolManager, Tool

# Define a simple function
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Create a Tool object
greet_tool = Tool(function=greet)

# Create a ToolManager and register the tool
manager = ToolManager()
manager.register_tool(greet_tool)

# Invoke the tool
result = await manager.invoke({"function": "greet", "arguments": {"name": "Alice"}})
print(result)  # Output: Hello, Alice!
```

## Important Notes

1. All tools must be registered with the `ToolManager` before they can be invoked.
2. The `Tool` class automatically generates a schema for the function if one is not provided.
3. Pre-processors must return a dictionary of arguments to be passed to the main function.
4. Post-processors can modify the result of the main function before it's returned.
5. The `parser` attribute of a `Tool` can be used to ensure the result is JSON serializable.

## Best Practices

- Use descriptive names for your tools to make them easily identifiable in the `ToolManager`.
- Leverage pre-processors for input validation and transformation.
- Use post-processors for result formatting or additional computations based on the function output.
- When creating complex workflows, consider chaining multiple tools together using the `ToolManager`.

## Future Improvements

- Implementation of tool versioning
- Support for tool dependencies and automatic resolution
- Enhanced error handling and logging capabilities

For more detailed information on each component, please refer to the respective source files and their docstrings.
