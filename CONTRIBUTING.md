## Contributing

We welcome contributions! If you'd like to help improve these migration tools, follow these steps to set up your local development environment.

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (for fast Python package management)
- [mise](https://mise.jdx.dev/) (for task running and environment management)
- Python 3.14+

### Local Setup
1. Clone the repository and navigate into it.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Copy the configuration template and configure your connection strings (defaults to `valkey://localhost:6379`):
   ```bash
   cp fnox.toml.example fnox.toml
   ```

### Running the CLI Locally
You can run the CLI tool locally using `uv`:
```bash
uv run vk_migrate --help
```

### Running Tests
We use standard Python unit tests located in the `tests/` directory.

To run the test suite, use `uv`:
```bash
uv run pytest
```

You can also use the `mise` tasks defined in `mise.toml` to interactively run checks and data loading against your configured test databases. Use `mise tasks` to see all available commands.
