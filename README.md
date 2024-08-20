# Lion-Core

Lion-Core is a lightweight yet powerful Python library designed to serve as a foundational framework for machine learning, artificial intelligence, workflow automation, scientific computing, and advanced data management. With a focus on simplicity and extensibility, Lion-Core aims to provide a robust toolkit for complex computational tasks while maintaining a minimal dependency footprint.

## 🌟 Highlights

- **Minimal Dependencies**: Built with only `Pydantic` as a dependency, ensuring a lightweight and easily maintainable codebase.
- **Extensible Architecture**: Designed from the ground up to be modular and adaptable to a wide range of computational needs.
- **Performance-Focused**: Optimized data structures and algorithms for efficient large-scale data processing.

## 🚀 Current Features

- **Advanced Data Structures**:
  - `Pile`: A flexible container that combines the best of lists and dictionaries, offering efficient access and powerful querying capabilities.
  - `Progression`: An ordered sequence container designed for high-performance operations on large datasets.

- **Robust Type System**: Leveraging Pydantic for data validation, ensuring type safety and data integrity across your entire project.

- **Converter System**: A flexible framework for seamless data conversion between various formats.

- **Element-based Architecture**: A foundational `Element` class that serves as the building block for creating modular and composable components.

- **Communication Framework**: A groundwork for inter-component messaging, facilitating the development of distributed and microservices-based applications.

- **Form and Validator System**: Dynamic workflow manipulation tools that allow for flexible and adaptable process designs.

- **Worker System**: Powerful workflow composition capabilities, enabling the creation of complex, multi-stage computational pipelines.

## 📦 Installation

```bash
pip install lion-core
```

## 🛠️ Development Environment Setup

To set up the development environment for Lion-Core:

1. Clone the repository:
    ```bash
    git clone https://github.com/lion-agi/lion-core.git
    cd lion-core
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -e .[dev]
    ```

4. Run tests:
    ```bash
    pytest --maxfail=1 --disable-warnings tests/
    ```

5. Check code style and run linters:
    ```bash
    black --check .
    isort --check-only .
    flake8 .
    ```

## 📚 Documentation

Comprehensive documentation is under development. For now, please refer to the inline documentation and comments in the source code.

## 🤝 Contributing

We welcome contributions! As the project is in its early stages, please open an issue to discuss potential changes before submitting pull requests.

## 📄 License

Lion-Core is released under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions, support, or to discuss potential collaborations, please open an issue on our [GitHub repository](https://github.com/lion-agi/lion-core/issues).

Join our Discord community for discussions, support, and updates: [Lion-Core Discord Server](https://discord.gg/JDj9ENhUE8)

---

Note: Lion-Core is an extraction and refinement of core components from the larger lionagi project. After reaching version 0.1.0, development will continue on Lion-Core while also informing a rewrite of the lionagi library.
